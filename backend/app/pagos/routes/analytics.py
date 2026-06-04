from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.pagos.schemas.payment_analytics_schema import (
    PaymentConciliationResponse,
    PaymentFailuresResponse,
    PaymentKPIsResponse,
    PaymentTimelinePoint,
    SlaStatusResponse,
)
from app.pagos.analytics.payment_metrics import get_conciliation_summary, get_failure_reasons
from app.pagos.services.payment_analytics_service import get_payment_kpis, get_payment_timeline
from app.pagos.services.sla_service import get_sla_status

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={500: {"description": "Internal server error"}},
)


@router.get(
    "/payments/kpis",
    response_model=PaymentKPIsResponse,
    summary="KPIs agregados del módulo de pagos",
    description=(
        "Consulta fact_payments_events y retorna métricas agregadas del rolling window "
        "indicado (default: últimas 24 h). "
        "El campo uptime refleja disponibilidad real desde fact_sla_events; "
        "si cae bajo 99.5% se registra automáticamente una alerta crítica."
    ),
)
async def get_payments_kpis(
    hours: int = Query(default=24, ge=1, le=8760, description="Ventana en horas (1–8760)"),
    db: Session = Depends(get_db),
) -> PaymentKPIsResponse:
    try:
        data = get_payment_kpis(db, hours=hours)
        return PaymentKPIsResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando KPIs de pagos: {exc}",
        )


@router.get(
    "/payments/timeline",
    response_model=List[PaymentTimelinePoint],
    summary="Timeline horario de transacciones de pagos",
    description=(
        "Agrupa fact_payments_events por hora y devuelve conteos de transacciones "
        "exitosas (Aprobado) y fallidas para cada bloque horario. "
        "Las horas sin actividad devuelven failed=0 y successful=0 (nunca null). "
        "Ordenado cronológicamente, hora más antigua primero."
    ),
)
async def get_payments_timeline(
    hours: int = Query(default=24, ge=1, le=168, description="Ventana en horas (1–168, default 24)"),
    db: Session = Depends(get_db),
) -> List[PaymentTimelinePoint]:
    try:
        data = get_payment_timeline(db, hours=hours)
        return [PaymentTimelinePoint(**point) for point in data]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando timeline de pagos: {exc}",
        )


@router.get(
    "/payments/failures",
    response_model=PaymentFailuresResponse,
    summary="Razones de fallo de pagos",
    description=(
        "Retorna la tasa de rechazo y el top N de razones de fallo (descripción legible) "
        "para la ventana de horas indicada. Usa dim_error_codes.descripcion para nombres "
        "en español. Solo considera transacciones con estado != Aprobado."
    ),
)
async def get_payments_failures(
    hours: int = Query(default=24, ge=1, le=8760, description="Ventana en horas (1–8760)"),
    top_n: int = Query(default=10, ge=1, le=50,   description="Máximo de razones a retornar"),
    db: Session = Depends(get_db),
) -> PaymentFailuresResponse:
    try:
        data = get_failure_reasons(db, hours=hours, top_n=top_n)
        return PaymentFailuresResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando razones de fallo: {exc}",
        )


@router.get(
    "/payments/conciliation",
    response_model=PaymentConciliationResponse,
    summary="Estado de conciliación de pagos",
    description=(
        "Agrupa fact_pagos por estado de conciliación (Aprobado / esperando_revisión / "
        "discrepancia_*) y retorna conteos y porcentajes. "
        "Incluye la tasa de aprobación global en la ventana."
    ),
)
async def get_payments_conciliation(
    hours: int = Query(default=24, ge=1, le=8760, description="Ventana en horas (1–8760)"),
    db: Session = Depends(get_db),
) -> PaymentConciliationResponse:
    try:
        data = get_conciliation_summary(db, hours=hours)
        return PaymentConciliationResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando estado de conciliación: {exc}",
        )


@router.get(
    "/payments/sla",
    response_model=SlaStatusResponse,
    summary="Estado SLA del servicio de pagos",
    description=(
        "Calcula el uptime real desde fact_sla_events para la ventana indicada. "
        "Si el uptime cae bajo 99.5% se registra automáticamente una PriorityAlert crítica "
        "(deduplicada: máximo una alerta cada 2 horas). "
        "Retorna eventos de downtime activos y alertas SLA no reconocidas de las últimas 24h."
    ),
)
async def get_payments_sla(
    hours: int = Query(default=24, ge=1, le=720, description="Ventana en horas (1–720, default 24)"),
    db: Session = Depends(get_db),
) -> SlaStatusResponse:
    try:
        data = get_sla_status(db, hours=hours)
        return SlaStatusResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error consultando estado SLA: {exc}",
        )
