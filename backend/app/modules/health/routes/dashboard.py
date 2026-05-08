from fastapi import APIRouter
from app.db import get_db
from app.modules.health.schemas import DashboardSalud
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import func
from app.modules.health.models.raw import RawVisita, RawAlerta
from app.modules.health.models.warehouse import DimPaciente

router = APIRouter(prefix="/api/v1/salud", tags=["Salud - Dashboard"])


@router.get("/dashboard", response_model=DashboardSalud)
async def obtener_dashboard(db: Session = Depends(get_db)):
    """Obtiene el dashboard del módulo de salud"""
    
    # Obtener métricas de la capa Raw
    total_visitas = db.query(func.count(RawVisita.id)).scalar() or 0
    visitas_completadas = db.query(func.count(RawVisita.id)).filter(
        RawVisita.estado == "completada"
    ).scalar() or 0
    visitas_pendientes = db.query(func.count(RawVisita.id)).filter(
        RawVisita.estado.in_(["programada", "en_progreso"])
    ).scalar() or 0
    
    # Alertas
    alertas_criticas = db.query(func.count(RawAlerta.id)).filter(
        RawAlerta.prioridad == "CRITICAL"
    ).scalar() or 0
    alertas_altas = db.query(func.count(RawAlerta.id)).filter(
        RawAlerta.prioridad == "HIGH"
    ).scalar() or 0
    
    # Pacientes desde warehouse
    total_pacientes = db.query(func.count(DimPaciente.id)).scalar() or 0
    
    # Tasa de completación
    tasa_completacion = "0%"
    if total_visitas > 0:
        tasa = (visitas_completadas / total_visitas) * 100
        tasa_completacion = f"{tasa:.1f}%"
    
    return DashboardSalud(
        total_pacientes=total_pacientes,
        total_visitas=total_visitas,
        visitas_completadas=visitas_completadas,
        visitas_pendientes=visitas_pendientes,
        alertas_criticas=alertas_criticas,
        alertas_altas=alertas_altas,
        tasa_completacion=tasa_completacion,
    )
