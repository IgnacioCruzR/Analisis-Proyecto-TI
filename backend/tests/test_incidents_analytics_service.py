"""
Tests para app.services.incidents_analytics_service.

Cubre:
  - get_incidents_kpis: todos los campos, manejo de None en avg, no ZeroDivisionError
  - get_incidents_timeline: longitud, campos por punto, ordenamiento
  - get_incidents_list: serialización de FactIncident a dict, campo assignee default
  - _format_relative_time: lógica de tiempo relativo
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _scalar_db(value):
    db = MagicMock()
    db.query.return_value.scalar.return_value = value
    db.query.return_value.filter.return_value.scalar.return_value = value
    db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = value
    db.query.return_value.filter.return_value.filter.return_value.filter.return_value.scalar.return_value = value
    return db


def _make_incident(incident_id="INC-1", title="Test", severity="high",
                   status="open", assignee="ops", opened_at=None, updated_at=None):
    row = MagicMock()
    row.incident_id = incident_id
    row.title = title
    row.severity = severity
    row.status = status
    row.assignee = assignee
    row.opened_at = opened_at or datetime(2026, 6, 13, 8, 0, 0, tzinfo=timezone.utc)
    row.updated_at = updated_at or datetime(2026, 6, 13, 9, 0, 0, tzinfo=timezone.utc)
    return row


# ─── _format_relative_time ────────────────────────────────────────────────────

class TestFormatRelativeTime:
    def test_just_now_for_seconds(self):
        from app.services.incidents_analytics_service import _format_relative_time
        dt = datetime.now(tz=timezone.utc) - timedelta(seconds=30)
        assert _format_relative_time(dt) == "just now"

    def test_minutes_for_recent(self):
        from app.services.incidents_analytics_service import _format_relative_time
        dt = datetime.now(tz=timezone.utc) - timedelta(minutes=5)
        result = _format_relative_time(dt)
        assert "min ago" in result

    def test_hours_for_same_day(self):
        from app.services.incidents_analytics_service import _format_relative_time
        dt = datetime.now(tz=timezone.utc) - timedelta(hours=3)
        result = _format_relative_time(dt)
        assert "hours ago" in result

    def test_days_for_older(self):
        from app.services.incidents_analytics_service import _format_relative_time
        dt = datetime.now(tz=timezone.utc) - timedelta(days=2)
        result = _format_relative_time(dt)
        assert "days ago" in result


# ─── get_incidents_kpis ───────────────────────────────────────────────────────

class TestGetIncidentsKpis:
    def test_returns_all_required_keys(self):
        from app.services.incidents_analytics_service import get_incidents_kpis
        db = _scalar_db(0)
        result = get_incidents_kpis(db)
        for key in ("activeIncidents", "resolvedToday", "avgResolutionTime",
                    "slaCompliance", "criticalCount"):
            assert key in result, f"Falta clave: {key}"

    def test_avg_resolution_none_returns_zero(self):
        from app.services.incidents_analytics_service import get_incidents_kpis
        db = _scalar_db(None)
        result = get_incidents_kpis(db)
        assert result["avgResolutionTime"] == 0.0

    def test_sla_compliance_zero_when_no_resolved(self):
        from app.services.incidents_analytics_service import get_incidents_kpis
        db = _scalar_db(0)
        result = get_incidents_kpis(db)
        assert result["slaCompliance"] == 0.0

    def test_active_incidents_is_int(self):
        from app.services.incidents_analytics_service import get_incidents_kpis
        db = _scalar_db(5)
        result = get_incidents_kpis(db)
        assert isinstance(result["activeIncidents"], int)

    def test_critical_count_is_int(self):
        from app.services.incidents_analytics_service import get_incidents_kpis
        db = _scalar_db(3)
        result = get_incidents_kpis(db)
        assert isinstance(result["criticalCount"], int)

    def test_sla_compliance_percentage_range(self):
        from app.services.incidents_analytics_service import get_incidents_kpis
        db = _scalar_db(10)
        result = get_incidents_kpis(db)
        assert 0.0 <= result["slaCompliance"] <= 100.0


# ─── get_incidents_timeline ───────────────────────────────────────────────────

class TestGetIncidentsTimeline:
    def test_default_14_days(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db)
        assert len(result) == 14

    def test_custom_7_days(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db, days=7)
        assert len(result) == 7

    def test_each_point_has_required_fields(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db, days=3)
        for point in result:
            assert "date" in point
            assert "opened" in point
            assert "resolved" in point
            assert "critical" in point

    def test_dates_valid_iso_format(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db, days=3)
        for point in result:
            datetime.strptime(point["date"], "%Y-%m-%d")

    def test_clamps_days_below_1(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db, days=0)
        assert len(result) == 14

    def test_clamps_days_above_90(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db, days=200)
        assert len(result) == 90

    def test_ordered_chronologically(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(0)
        result = get_incidents_timeline(db, days=5)
        dates = [point["date"] for point in result]
        assert dates == sorted(dates)

    def test_counts_are_ints(self):
        from app.services.incidents_analytics_service import get_incidents_timeline
        db = _scalar_db(2)
        result = get_incidents_timeline(db, days=2)
        for point in result:
            assert isinstance(point["opened"], int)
            assert isinstance(point["resolved"], int)
            assert isinstance(point["critical"], int)


# ─── get_incidents_list ───────────────────────────────────────────────────────

class TestGetIncidentsList:
    def _db_with_rows(self, rows):
        db = MagicMock()
        db.query.return_value.order_by.return_value.limit.return_value.all.return_value = rows
        return db

    def test_returns_list_of_dicts(self):
        from app.services.incidents_analytics_service import get_incidents_list
        db = self._db_with_rows([_make_incident()])
        result = get_incidents_list(db)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_each_item_has_all_fields(self):
        from app.services.incidents_analytics_service import get_incidents_list
        db = self._db_with_rows([_make_incident()])
        result = get_incidents_list(db)
        for field in ("id", "title", "severity", "status", "assignee",
                      "createdAt", "updatedAt"):
            assert field in result[0], f"Falta campo: {field}"

    def test_empty_db_returns_empty_list(self):
        from app.services.incidents_analytics_service import get_incidents_list
        db = self._db_with_rows([])
        result = get_incidents_list(db)
        assert result == []

    def test_assignee_none_defaults_to_unassigned(self):
        from app.services.incidents_analytics_service import get_incidents_list
        incident = _make_incident(assignee=None)
        db = self._db_with_rows([incident])
        result = get_incidents_list(db)
        assert result[0]["assignee"] == "Unassigned"

    def test_respects_limit(self):
        from app.services.incidents_analytics_service import get_incidents_list
        db = self._db_with_rows([])
        get_incidents_list(db, limit=25)
        db.query.return_value.order_by.return_value.limit.assert_called_with(25)

    def test_incident_id_mapped_to_id_field(self):
        from app.services.incidents_analytics_service import get_incidents_list
        incident = _make_incident(incident_id="INC-999")
        db = self._db_with_rows([incident])
        result = get_incidents_list(db)
        assert result[0]["id"] == "INC-999"

    def test_created_at_is_relative_string(self):
        from app.services.incidents_analytics_service import get_incidents_list
        incident = _make_incident()
        db = self._db_with_rows([incident])
        result = get_incidents_list(db)
        # createdAt debe ser una cadena (formato relativo)
        assert isinstance(result[0]["createdAt"], str)
        assert len(result[0]["createdAt"]) > 0
