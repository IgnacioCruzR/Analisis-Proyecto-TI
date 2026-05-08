"""
Router consolidado para el módulo de Salud
Agrupa todos los endpoints por entidad
"""

from fastapi import APIRouter
from app.modules.health.routes import (
    pacientes_router,
    visitas_router,
    alertas_router,
    dashboard_router,
)

# Router principal del módulo de salud
health_router = APIRouter(prefix="/api/v1/salud", tags=["Salud"])

# Incluir todos los routers del módulo
health_router.include_router(pacientes_router, prefix="/pacientes", tags=["Pacientes"])
health_router.include_router(visitas_router, prefix="/visitas", tags=["Visitas"])
health_router.include_router(alertas_router, prefix="/alertas", tags=["Alertas"])
health_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

__all__ = ["health_router"]
