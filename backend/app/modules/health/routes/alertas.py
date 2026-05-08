from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.modules.health.schemas import (
    AlertaCreate,
    AlertaUpdate,
    AlertaResponse,
)
from app.modules.health.services import AlertaService

router = APIRouter(prefix="/api/v1/salud/alertas", tags=["Salud - Alertas"])


@router.post("/", response_model=AlertaResponse, status_code=201)
async def crear_alerta(
    alerta: AlertaCreate,
    db: Session = Depends(get_db)
):
    """Crea una nueva alerta"""
    try:
        raw_alerta = AlertaService.crear_alerta(db, alerta)
        return AlertaResponse.from_orm(raw_alerta)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[AlertaResponse])
async def listar_alertas(
    paciente_id: UUID = Query(None),
    criticas_solo: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista alertas (filtradas opcionalmente)"""
    if paciente_id:
        alertas = AlertaService.listar_alertas_paciente(db, paciente_id, skip, limit)
    elif criticas_solo:
        alertas = AlertaService.listar_alertas_criticas(db, skip, limit)
    else:
        alertas = db.query(db).offset(skip).limit(limit).all()
    
    return [AlertaResponse.from_orm(a) for a in alertas]


@router.get("/{alerta_id}", response_model=AlertaResponse)
async def obtener_alerta(
    alerta_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtiene una alerta específica"""
    alerta = AlertaService.obtener_alerta(db, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return AlertaResponse.from_orm(alerta)


@router.put("/{alerta_id}", response_model=AlertaResponse)
async def actualizar_alerta(
    alerta_id: UUID,
    alerta: AlertaUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una alerta existente"""
    alerta_actualizada = AlertaService.actualizar_alerta(db, alerta_id, alerta)
    if not alerta_actualizada:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return AlertaResponse.from_orm(alerta_actualizada)


@router.post("/{alerta_id}/resolver", response_model=AlertaResponse)
async def resolver_alerta(
    alerta_id: UUID,
    db: Session = Depends(get_db)
):
    """Resuelve una alerta"""
    alerta = AlertaService.resolver_alerta(db, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return AlertaResponse.from_orm(alerta)


@router.get("/resumen/por-prioridad", response_model=dict)
async def obtener_resumen_alertas(
    db: Session = Depends(get_db)
):
    """Obtiene el resumen de alertas abiertas por prioridad"""
    return AlertaService.contar_alertas_por_prioridad(db)
