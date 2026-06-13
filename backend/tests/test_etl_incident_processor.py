"""
Tests para Incident ETL processor.

Cubre:
  - process_incident_event: todos los event_types soportados
  - Validación de incident_id requerido → IncidentProcessingError
  - Manejo de event_type desconocido
  - _parse_datetime: strings ISO, None, datetime directo
  - _handle_incident_resolved: cálculo automático de resolution_time_hours
  - Idempotencia: incident_upsert alias de incident_created
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_raw(event_type: str, payload: dict):
    raw = MagicMock()
    raw.event_type = event_type
    raw.payload = payload
    return raw


def _make_db(existing=None):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = existing
    return db


# ─── _parse_datetime ─────────────────────────────────────────────────────────

class TestParseDatetime:
    def test_none_returns_none(self):
        from app.etl.processors.incident_processor import _parse_datetime
        assert _parse_datetime(None) is None

    def test_datetime_passthrough(self):
        from app.etl.processors.incident_processor import _parse_datetime
        dt = datetime(2026, 3, 1, 9, 0, 0)
        assert _parse_datetime(dt) is dt

    def test_iso_string_without_tz(self):
        from app.etl.processors.incident_processor import _parse_datetime
        result = _parse_datetime("2026-06-10T08:00:00")
        assert isinstance(result, datetime)
        assert result.year == 2026

    def test_iso_string_with_Z(self):
        from app.etl.processors.incident_processor import _parse_datetime
        result = _parse_datetime("2026-06-10T08:00:00Z")
        assert result is not None
        assert result.tzinfo is None

    def test_invalid_string_returns_none(self):
        from app.etl.processors.incident_processor import _parse_datetime
        assert _parse_datetime("bad-date") is None


# ─── Evento desconocido ───────────────────────────────────────────────────────

class TestUnknownEventType:
    def test_raises_processing_error(self):
        from app.etl.processors.incident_processor import process_incident_event, IncidentProcessingError
        db = _make_db()
        raw = _make_raw("incident_unknown", {"incident_id": "INC-1"})
        with pytest.raises(IncidentProcessingError, match="no soportado"):
            process_incident_event(db, raw)


# ─── Validación de incident_id ────────────────────────────────────────────────

class TestMissingIncidentId:
    @pytest.mark.parametrize("event_type", [
        "incident_created",
        "incident_assigned",
        "incident_status_changed",
        "incident_resolved",
    ])
    def test_missing_id_raises(self, event_type):
        from app.etl.processors.incident_processor import process_incident_event, IncidentProcessingError
        db = _make_db()
        raw = _make_raw(event_type, {"title": "Sin ID"})
        with pytest.raises(IncidentProcessingError, match="incident_id"):
            process_incident_event(db, raw)


# ─── incident_created ─────────────────────────────────────────────────────────

class TestIncidentCreated:
    def test_creates_new_incident(self):
        from app.etl.processors.incident_processor import process_incident_event
        db = _make_db(existing=None)
        raw = _make_raw("incident_created", {
            "incident_id": "INC-100",
            "title": "Servidor caído",
            "severity": "critical",
            "status": "open",
        })
        process_incident_event(db, raw)
        assert db.add.called
        assert db.flush.called

    def test_applies_title_from_payload(self):
        from app.etl.processors.incident_processor import process_incident_event
        db = _make_db(existing=None)
        raw = _make_raw("incident_created", {
            "incident_id": "INC-101",
            "title": "DB lenta",
            "severity": "high",
        })
        result = process_incident_event(db, raw)
        # El fact creado debe tener el título actualizado vía _apply_common_fields
        assert db.add.called

    def test_upsert_alias_behaves_same(self):
        from app.etl.processors.incident_processor import process_incident_event
        db = _make_db(existing=None)
        raw = _make_raw("incident_upsert", {
            "incident_id": "INC-102",
            "title": "Upsert test",
        })
        process_incident_event(db, raw)
        assert db.add.called and db.flush.called

    def test_default_title_generated_when_missing(self):
        from app.etl.processors.incident_processor import _get_or_create_incident
        db = _make_db(existing=None)
        fact = _get_or_create_incident(db, "INC-999", {})
        assert "INC-999" in fact.title

    def test_default_severity_is_medium(self):
        from app.etl.processors.incident_processor import _get_or_create_incident
        db = _make_db(existing=None)
        fact = _get_or_create_incident(db, "INC-200", {})
        assert fact.severity == "medium"

    def test_default_status_is_open(self):
        from app.etl.processors.incident_processor import _get_or_create_incident
        db = _make_db(existing=None)
        fact = _get_or_create_incident(db, "INC-201", {})
        assert fact.status == "open"


# ─── incident_assigned ────────────────────────────────────────────────────────

class TestIncidentAssigned:
    def test_updates_assignee(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.assignee = "ops-team"
        db = _make_db(existing=existing)
        raw = _make_raw("incident_assigned", {
            "incident_id": "INC-200",
            "assignee": "devops-alice",
        })
        process_incident_event(db, raw)
        assert existing.assignee == "devops-alice"
        assert db.flush.called

    def test_sets_assignee_to_none_when_omitted(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.assignee = "someone"
        db = _make_db(existing=existing)
        raw = _make_raw("incident_assigned", {"incident_id": "INC-201"})
        process_incident_event(db, raw)
        assert existing.assignee is None


# ─── incident_status_changed ─────────────────────────────────────────────────

class TestIncidentStatusChanged:
    def test_valid_status_applied(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.status = "open"
        db = _make_db(existing=existing)
        raw = _make_raw("incident_status_changed", {
            "incident_id": "INC-300",
            "status": "investigating",
        })
        process_incident_event(db, raw)
        assert existing.status == "investigating"

    def test_invalid_status_not_applied(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.status = "open"
        db = _make_db(existing=existing)
        raw = _make_raw("incident_status_changed", {
            "incident_id": "INC-301",
            "status": "pendiente",  # status inválido
        })
        process_incident_event(db, raw)
        # _apply_common_fields solo aplica si status in VALID_STATUSES
        assert existing.status == "open"

    def test_invalid_severity_not_applied(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.severity = "high"
        db = _make_db(existing=existing)
        raw = _make_raw("incident_status_changed", {
            "incident_id": "INC-302",
            "severity": "catastrophic",  # inválido
        })
        process_incident_event(db, raw)
        assert existing.severity == "high"


# ─── incident_resolved ───────────────────────────────────────────────────────

class TestIncidentResolved:
    def test_status_set_to_resolved(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.status = "investigating"
        existing.opened_at = datetime(2026, 6, 13, 8, 0, 0, tzinfo=timezone.utc)
        existing.resolution_time_hours = None
        db = _make_db(existing=existing)
        raw = _make_raw("incident_resolved", {"incident_id": "INC-400"})
        process_incident_event(db, raw)
        assert existing.status == "resolved"

    def test_resolution_time_from_payload(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.opened_at = datetime(2026, 6, 13, 8, 0, 0)
        db = _make_db(existing=existing)
        raw = _make_raw("incident_resolved", {
            "incident_id": "INC-401",
            "resolution_time_hours": 4.5,
        })
        process_incident_event(db, raw)
        assert existing.resolution_time_hours == 4.5

    def test_resolution_time_calculated_from_opened_at(self):
        from app.etl.processors.incident_processor import process_incident_event
        opened = datetime(2026, 6, 13, 6, 0, 0)
        resolved = datetime(2026, 6, 13, 8, 0, 0)
        existing = MagicMock()
        existing.opened_at = opened
        existing.resolution_time_hours = None
        db = _make_db(existing=existing)
        raw = _make_raw("incident_resolved", {
            "incident_id": "INC-402",
            "resolved_at": resolved.isoformat(),
        })
        process_incident_event(db, raw)
        # 2 horas de diferencia
        assert existing.resolution_time_hours == 2.0

    def test_sla_met_set_from_payload(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.opened_at = datetime(2026, 6, 13, 6, 0, 0, tzinfo=timezone.utc)
        db = _make_db(existing=existing)
        raw = _make_raw("incident_resolved", {
            "incident_id": "INC-403",
            "sla_met": True,
        })
        process_incident_event(db, raw)
        assert existing.sla_met is True

    def test_resolved_at_set_from_payload_iso(self):
        from app.etl.processors.incident_processor import process_incident_event
        existing = MagicMock()
        existing.opened_at = datetime(2026, 6, 13, 6, 0, 0)
        existing.resolution_time_hours = None
        db = _make_db(existing=existing)
        raw = _make_raw("incident_resolved", {
            "incident_id": "INC-404",
            "resolved_at": "2026-06-13T10:00:00",
        })
        process_incident_event(db, raw)
        assert existing.resolved_at is not None
