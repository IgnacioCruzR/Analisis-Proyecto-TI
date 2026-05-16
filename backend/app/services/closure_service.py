from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.warehouse.pagos.fact_pagos import FactPagos
from app.models.warehouse.pagos.dim_estados_conciliacion import DimEstadosConciliacion
from app.models.warehouse.pagos.cierre_diario import CierreDiario


TOLERANCE = Decimal("0.01")  # tolerance in monetary comparison (1 cent)


def process_cierre_diario(db: Session, payload: Dict) -> CierreDiario:
    """Process a daily closure reconciliation.

    Steps:
    - Compute internal approved totals/counts for the date
    - Compare with reported totals
    - If matches within tolerance -> mark pending transactions as 'Aprobado' and record closure as 'Aprobado'
    - If mismatch in count or amount -> record closure with corresponding discrepancy state

    Uses SELECT ... FOR UPDATE when updating transaction rows to avoid race conditions.
    """
    fecha = payload["fecha"]
    reported_total = Decimal(payload["reported_total"])
    reported_count = int(payload["reported_count"])

    # compute date range (UTC day)
    start = datetime.combine(fecha, datetime.min.time())
    end = datetime.combine(fecha, datetime.max.time())

    # compute internal approved totals
    approved_estado = db.query(DimEstadosConciliacion).filter(DimEstadosConciliacion.nombre == "Aprobado").one_or_none()
    approved_id = approved_estado.id if approved_estado else None

    internal_q = (
        db.query(func.coalesce(func.count(FactPagos.transaction_id), 0).label("cnt"), func.coalesce(func.sum(FactPagos.monto), 0).label("sum"))
        .filter(FactPagos.timestamp_evento >= start, FactPagos.timestamp_evento <= end)
    )
    if approved_id:
        internal_q = internal_q.filter(FactPagos.estado_conciliacion_id == approved_id)

    row = internal_q.one()
    internal_count = int(row.cnt or 0)
    internal_total = Decimal(row.sum or 0)

    # Determine status
    status_name = "Aprobado"
    note = None

    if internal_count != reported_count:
        status_name = "discrepancia_de_transacciones"
        note = f"count_mismatch: internal={internal_count} reported={reported_count}"
    else:
        # compare amounts with tolerance
        diff = abs(internal_total - reported_total)
        if diff > TOLERANCE:
            status_name = "discrepancia_de_monto"
            note = f"amount_mismatch: internal={internal_total} reported={reported_total} diff={diff}"

    estado = db.query(DimEstadosConciliacion).filter(DimEstadosConciliacion.nombre == status_name).one_or_none()
    if not estado:
        estado = DimEstadosConciliacion(nombre=status_name)
        db.add(estado)
        db.flush()

    # create closure record
    inicio = datetime.utcnow()
    cierre = CierreDiario(
        fecha=fecha,
        reported_total=reported_total,
        reported_count=reported_count,
        internal_total=internal_total,
        internal_count=internal_count,
        estado_id=estado.id,
        processed_at=None,
        duration_seconds=None,
        note=note,
    )
    db.add(cierre)
    db.flush()

    # If approved, mark pending transactions in the day as approved (locking rows)
    if status_name == "Aprobado":
        pending_estado = db.query(DimEstadosConciliacion).filter(DimEstadosConciliacion.nombre == "esperando_revisión").one_or_none()
        if pending_estado:
            pending_rows = (
                db.query(FactPagos)
                .filter(FactPagos.timestamp_evento >= start, FactPagos.timestamp_evento <= end, FactPagos.estado_conciliacion_id == pending_estado.id)
                .with_for_update()
                .all()
            )
            for p in pending_rows:
                p.estado_conciliacion_id = estado.id
            db.flush()

    # finalize closure
    fin = datetime.utcnow()
    cierre.processed_at = fin
    cierre.duration_seconds = int((fin - inicio).total_seconds())

    # commit will be handled by caller
    return cierre
