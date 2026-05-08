from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.modules.health.schemas import (
    VisitaCreate,
    VisitaUpdate,
    VisitaResponse,
)
from app.modules.health.services import VisitaService

router = APIRouter(prefix="/api/v1/salud/visitas", tags=["Salud - Visitas"])


@router.post("/", response_model=VisitaResponse, status_code=201)
async def crear_visita(
    visita: VisitaCreate,
    db: Session = Depends(get_db)
):
    """Crea una nueva visita"""
    try:
        raw_visita = VisitaService.crear_visita(db, visita)
        return VisitaResponse.from_orm(raw_visita)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[VisitaResponse])
async def listar_visitas(
    paciente_id: UUID = Query(None),
    profesional_id: UUID = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista visitas (filtradas opcionalmente)"""
    if paciente_id:
        visitas = VisitaService.listar_visitas_paciente(db, paciente_id, skip, limit)
    elif profesional_id:
        visitas = VisitaService.listar_visitas_profesional(db, profesional_id, skip, limit)
    else:
        visitas = db.query(db).offset(skip).limit(limit).all()
    
    return [VisitaResponse.from_orm(v) for v in visitas]


@router.get("/{visita_id}", response_model=VisitaResponse)
async def obtener_visita(
    visita_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtiene una visita específica"""
    visita = VisitaService.obtener_visita(db, visita_id)
    if not visita:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    return VisitaResponse.from_orm(visita)


@router.put("/{visita_id}", response_model=VisitaResponse)
async def actualizar_visita(
    visita_id: UUID,
    visita: VisitaUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una visita existente"""
    visita_actualizada = VisitaService.actualizar_visita(db, visita_id, visita)
    if not visita_actualizada:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    return VisitaResponse.from_orm(visita_actualizada)


@router.post("/{visita_id}/completar", response_model=VisitaResponse)
async def completar_visita(
    visita_id: UUID,
    db: Session = Depends(get_db)
):
    """Marca una visita como completada"""
    visita = VisitaService.completar_visita(db, visita_id)
    if not visita:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    return VisitaResponse.from_orm(visita)


@router.post("/{visita_id}/cancelar", response_model=VisitaResponse)
async def cancelar_visita(
    visita_id: UUID,
    db: Session = Depends(get_db)
):
    """Cancela una visita"""
    visita = VisitaService.cancelar_visita(db, visita_id)
    if not visita:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    return VisitaResponse.from_orm(visita)


@router.get("/hoy/programadas", response_model=list[VisitaResponse])
async def obtener_visitas_hoy(
    zona_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    """Obtiene las visitas programadas para hoy"""
    visitas = VisitaService.obtener_visitas_hoy(db, zona_id)
    return [VisitaResponse.from_orm(v) for v in visitas]
