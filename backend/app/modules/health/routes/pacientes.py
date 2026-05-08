from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.modules.health.schemas import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
)
from app.modules.health.services import PacienteService

router = APIRouter(prefix="/api/v1/salud/pacientes", tags=["Salud - Pacientes"])


@router.post("/", response_model=PacienteResponse, status_code=201)
async def crear_paciente(
    paciente: PacienteCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo paciente"""
    try:
        raw_paciente = PacienteService.crear_paciente(db, paciente)
        return PacienteResponse.from_orm(raw_paciente)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[PacienteResponse])
async def listar_pacientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista todos los pacientes"""
    pacientes = PacienteService.listar_pacientes(db, skip=skip, limit=limit)
    return [PacienteResponse.from_orm(p) for p in pacientes]


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obtener_paciente(
    paciente_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtiene un paciente específico"""
    paciente = PacienteService.obtener_paciente(db, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PacienteResponse.from_orm(paciente)


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def actualizar_paciente(
    paciente_id: UUID,
    paciente: PacienteUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un paciente existente"""
    paciente_actualizado = PacienteService.actualizar_paciente(db, paciente_id, paciente)
    if not paciente_actualizado:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PacienteResponse.from_orm(paciente_actualizado)


@router.delete("/{paciente_id}", status_code=204)
async def eliminar_paciente(
    paciente_id: UUID,
    db: Session = Depends(get_db)
):
    """Elimina un paciente"""
    if not PacienteService.eliminar_paciente(db, paciente_id):
        raise HTTPException(status_code=404, detail="Paciente no encontrado")


@router.get("/{paciente_id}/estadisticas", response_model=dict)
async def obtener_estadisticas(
    paciente_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas del paciente desde el warehouse"""
    return PacienteService.obtener_estadisticas_paciente(db, paciente_id)
