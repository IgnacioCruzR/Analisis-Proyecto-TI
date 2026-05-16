import os
import uuid
import json
from datetime import datetime, date
from decimal import Decimal

# Use a local SQLite DB for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_payments.db")
os.environ.setdefault("SQL_ECHO", "False")

from fastapi.testclient import TestClient
import runpy
import os
import sys

# import app by executing main.py so env vars are read first
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
MAIN_PATH = os.path.join(BASE_DIR, "main.py")
g = runpy.run_path(MAIN_PATH)
app = g["app"]

client = TestClient(app)


def iso_now():
    return datetime.utcnow().isoformat()


def test_payments_flow():
    tx_id = str(uuid.uuid4())
    token = "tok-test-123"

    # 1) intento_pago
    intento_payload = {
        "source": "payments",
        "event_type": "intento_pago",
        "payload": {
            "transaction_id": tx_id,
            "order_id": "ORD-1",
            "subscription_id": None,
            "monto": str(Decimal('100.50')),
            "token_transaccion": token,
            "timestamp_evento": iso_now()
        }
    }

    r = client.post("/events", json=intento_payload)
    print("intento_pago ->", r.status_code, r.json())
    assert r.status_code == 201

    # 2) confirmar_pago (approved)
    confirm_payload = {
        "source": "payments",
        "event_type": "confirmar_pago",
        "payload": {
            "token_transaccion": token,
            "transaction_id": tx_id,
            "approved": True,
            "codigo_error": None,
            "timestamp_evento": iso_now()
        }
    }

    r2 = client.post("/events", json=confirm_payload)
    print("confirmar_pago ->", r2.status_code, r2.json())
    assert r2.status_code == 201

    # 3) cierre_diario_completado
    today = date.today().isoformat()
    cierre_payload = {
        "source": "payments",
        "event_type": "cierre_diario_completado",
        "payload": {
            "fecha": today,
            "reported_total": str(Decimal('100.50')),
            "reported_count": 1,
            "reference_id": "report-1",
            "timestamp_event": iso_now()
        }
    }

    r3 = client.post("/events", json=cierre_payload)
    print("cierre_diario_completado ->", r3.status_code, r3.json())
    assert r3.status_code == 201


if __name__ == "__main__":
    test_payments_flow()
    print("All done")
