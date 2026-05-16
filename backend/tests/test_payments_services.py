import os
import sys
from datetime import datetime, date
from decimal import Decimal
import uuid

# use local sqlite for testing
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_payments.db")
os.environ.setdefault("SQL_ECHO", "False")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app.db import engine, Base, SessionLocal
from app.models.raw.raw_events import RawEvent
from app.models.warehouse.pagos.fact_pagos import FactPagos
from app.models.warehouse.pagos.dim_estados_conciliacion import DimEstadosConciliacion
from app.models.warehouse.pagos.cierre_diario import CierreDiario

# ensure a clean sqlite file for test
db_path = os.path.join(BASE_DIR, "test_payments.db")
if os.path.exists(db_path):
    os.remove(db_path)

# create tables only for the necessary models
Base.metadata.create_all(bind=engine, tables=[RawEvent.__table__, FactPagos.__table__, DimEstadosConciliacion.__table__, CierreDiario.__table__])

from app.services.event_service import create_event
from app.services.payment_service import register_payment_attempt, confirm_payment
from app.services.closure_service import process_cierre_diario


def run_flow():
    db = SessionLocal()
    try:
        # 1) create raw evento intento_pago
        tx_id = uuid.uuid4()
        token = "tok-test-456"
        # raw event payload must be JSON-serializable (strings)
        raw_payload = {
            "transaction_id": str(tx_id),
            "order_id": "ORD-1",
            "subscription_id": None,
            "monto": str(Decimal("200.75")),
            "token_transaccion": token,
            "timestamp_evento": datetime.utcnow().isoformat(),
        }

        event = type("E", (), {"source": "payments", "event_type": "intento_pago", "payload": raw_payload})
        # create_event expects pydantic EventCreate but minimal object with attributes works for insertion via create_event
        db_event = create_event(db=db, event=event)
        print("Created raw event id", db_event.id)

        # 2) register attempt via service
        # For DB insertion, use UUID object for transaction_id
        attempt_payload = {
            "transaction_id": tx_id,
            "order_id": "ORD-1",
            "subscription_id": None,
            "monto": Decimal("200.75"),
            "token_transaccion": token,
            "timestamp_evento": datetime.utcnow(),
        }

        fact = register_payment_attempt(db, attempt_payload)
        db.commit()
        print("Registered fact pagos tx", fact.transaction_id)

        # 3) confirm payment
        confirm_payload = {
            "transaction_id": str(tx_id),
            "approved": True,
            "codigo_error": None,
            "timestamp_evento": datetime.utcnow(),
        }

        fact2 = confirm_payment(db, token, confirm_payload)
        db.commit()
        print("Confirmed payment, estado_id", fact2.estado_conciliacion_id)

        # 4) cierre diario
        cierre_payload = {
            "fecha": date.today(),
            "reported_total": str(Decimal("200.75")),
            "reported_count": 1,
        }

        cierre = process_cierre_diario(db, cierre_payload)
        db.commit()
        print("Cierre created id", cierre.id, "estado_id", cierre.estado_id, "duration", cierre.duration_seconds)

    finally:
        db.close()


if __name__ == '__main__':
    run_flow()
    print("Service flow test completed")
