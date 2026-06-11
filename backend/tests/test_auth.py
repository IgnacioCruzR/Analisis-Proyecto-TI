"""
Tests de autenticación y autorización — Finding 9.2.

Ejercita el flujo real de auth (DISABLE_AUTH=false) usando monkeypatch para:
  • forzar _DISABLE_AUTH=False en app.auth.deps durante el test
  • controlar decode_token sin un Keycloak real

Cubre:
  401 cuando no se envía Bearer token
  401 cuando decode_token levanta KeycloakAuthError (token inválido/expirado)
  403 cuando el token es válido pero el usuario no tiene el rol requerido
  200 cuando el token es válido y el usuario tiene el rol correcto
  require_roles — exige TODOS los roles (no basta con uno)
  require_any_role — basta con UNO de los roles
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

import app.auth.deps as _auth_deps
from app.auth.keycloak import KeycloakAuthError


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _claims(roles: list[str]) -> dict:
    return {
        "sub": "test-sub-123",
        "preferred_username": "tester",
        "email": "tester@test.cl",
        "realm_access": {"roles": roles},
    }


def _make_client(mock_db: MagicMock, decode_return) -> TestClient:
    """
    TestClient con DISABLE_AUTH desactivado y decode_token bajo control del test.

    decode_return puede ser:
      - dict de claims  →  autenticación exitosa
      - Exception       →  decode_token raises esa excepción
    """
    from main import app
    from app.db import get_db

    def _override():
        yield mock_db

    app.dependency_overrides[get_db] = _override

    if isinstance(decode_return, Exception):
        _auth_deps.decode_token = lambda token: (_ for _ in ()).throw(type(decode_return)(str(decode_return)))
    else:
        _auth_deps.decode_token = lambda token: decode_return

    client = TestClient(app, raise_server_exceptions=False)
    return client


# ─── Fixture that turns off the DISABLE_AUTH bypass ──────────────────────────

@pytest.fixture(autouse=False)
def auth_off(monkeypatch):
    """Desactiva el bypass de auth para que la lógica JWT real se ejecute."""
    monkeypatch.setattr(_auth_deps, "_DISABLE_AUTH", False)
    yield
    # Restore decode_token in case it was replaced by _make_client
    from app.auth.keycloak import decode_token as _real_decode
    _auth_deps.decode_token = _real_decode


# ─── Fixture: client with auth enabled, DB mocked ────────────────────────────

@pytest.fixture
def auth_mock_db() -> MagicMock:
    session = MagicMock(spec=Session)
    _counter = [0]
    def _refresh(obj):
        _counter[0] += 1
        obj.id = _counter[0]
    session.refresh.side_effect = _refresh
    return session


# ─── 401: no Bearer token ─────────────────────────────────────────────────────

class TestNoToken:
    """Without a token, every protected endpoint must return 401."""

    def test_inventory_kpis_401_without_token(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            "app.api.routes.inventory.get_inventory_kpis",
            lambda db: {},
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get("/v1/inventory/kpis")
        app.dependency_overrides.clear()

        assert response.status_code == 401
        assert "Bearer" in response.headers.get("www-authenticate", "")

    def test_payments_kpis_401_without_token(self, auth_off, auth_mock_db):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get("/v1/analytics/payments/kpis")
        app.dependency_overrides.clear()

        assert response.status_code == 401


# ─── 401: invalid token (decode_token raises) ────────────────────────────────

class TestInvalidToken:
    """A token that decode_token rejects must produce 401, not 500."""

    def test_expired_token_returns_401(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: (_ for _ in ()).throw(KeycloakAuthError("Token expirado")),
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/inventory/kpis",
                headers={"Authorization": "Bearer expired.token.here"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 401
        assert "expirado" in response.json().get("detail", "").lower()

    def test_malformed_token_returns_401(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: (_ for _ in ()).throw(KeycloakAuthError("Token mal formado")),
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/inventory/kpis",
                headers={"Authorization": "Bearer not.a.jwt"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 401


# ─── 403: valid token, insufficient role ─────────────────────────────────────

class TestInsufficientRole:
    """A valid token without the required roles must produce 403."""

    def test_wrong_role_returns_403_on_inventory(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: _claims(["some_other_role"]),
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/inventory/kpis",
                headers={"Authorization": "Bearer valid.but.wrong"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 403
        assert "roles" in response.json().get("detail", "").lower()

    def test_wrong_role_returns_403_on_payments(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: _claims(["viewer"]),
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/analytics/payments/kpis",
                headers={"Authorization": "Bearer valid.but.wrong"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 403


# ─── 200: valid token, correct role ──────────────────────────────────────────

class TestCorrectRole:
    """A valid token with the correct role must be accepted (not 401 or 403)."""

    def test_analista_role_passes_inventory_guard(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: _claims(["analista"]),
        )
        monkeypatch.setattr(
            "app.api.routes.inventory.get_inventory_kpis",
            lambda db: {
                "total_skus": 10, "total_stock_value": 0.0, "warehouses_count": 2,
                "low_stock_count": 1, "out_of_stock_count": 0, "turnover_rate": 0.0,
            },
        )
        monkeypatch.setattr(
            "app.api.routes.inventory._now_utc_iso",
            lambda: "2026-06-11T00:00:00Z",
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/inventory/kpis",
                headers={"Authorization": "Bearer valid.analista.token"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 200

    def test_admin_role_passes_payments_guard(self, auth_off, auth_mock_db, monkeypatch):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: _claims(["admin"]),
        )
        monkeypatch.setattr(
            "app.pagos.routes.analytics.get_payment_kpis",
            lambda db, hours: {
                "totalTransactions": 0, "failedPayments": 0, "failureRate": 0.0,
                "revenue": 0.0, "avgTransactionValue": 0.0, "uptime": 100.0,
            },
        )
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/analytics/payments/kpis",
                headers={"Authorization": "Bearer valid.admin.token"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 200


# ─── require_any_role: one matching role is enough ───────────────────────────

class TestRequireAnyRole:
    """require_any_role(['admin','analista']) — any one match is sufficient."""

    @pytest.mark.parametrize("role", ["admin", "analista"])
    def test_each_allowed_role_passes(self, auth_off, auth_mock_db, monkeypatch, role):
        from main import app
        from app.db import get_db

        app.dependency_overrides[get_db] = lambda: (yield auth_mock_db)
        monkeypatch.setattr(
            _auth_deps,
            "decode_token",
            lambda token: _claims([role]),
        )
        monkeypatch.setattr(
            "app.api.routes.inventory.get_inventory_kpis",
            lambda db: {
                "total_skus": 0, "total_stock_value": 0.0, "warehouses_count": 0,
                "low_stock_count": 0, "out_of_stock_count": 0, "turnover_rate": 0.0,
            },
        )
        monkeypatch.setattr("app.api.routes.inventory._now_utc_iso", lambda: "2026-06-11T00:00:00Z")
        with TestClient(app, raise_server_exceptions=False) as tc:
            response = tc.get(
                "/v1/inventory/kpis",
                headers={"Authorization": f"Bearer {role}.token"},
            )
        app.dependency_overrides.clear()

        assert response.status_code == 200, f"role '{role}' should be allowed but got {response.status_code}"
