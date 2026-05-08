from .pacientes import router as pacientes_router
from .visitas import router as visitas_router
from .alertas import router as alertas_router
from .dashboard import router as dashboard_router

__all__ = [
    "pacientes_router",
    "visitas_router",
    "alertas_router",
    "dashboard_router",
]
