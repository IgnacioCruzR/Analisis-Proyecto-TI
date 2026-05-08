from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

# =====================================
# Base de Datos y Modelos
# =====================================
from app.core.database import engine, get_db
from app.db import Base
from app.models import RawEvent, FactSubscription  # noqa: F401

# =====================================
# Módulo de Salud (Data Warehouse)
# =====================================
from app.modules.health import (  # noqa: F401
    RawUsuario,
    RawPaciente,
    RawVisita,
    RawAlerta,
    RawFichaClinica,
    RawDocumentoAdjunto,
    FactVisita,
    FactAlerta,
    DimPaciente,
    DimProfesional,
)
from app.modules.health.router import health_router

# =====================================
# Inicializar Base de Datos
# =====================================

# Crear todas las tablas (subscripciones + salud en misma BD)
Base.metadata.create_all(bind=engine)

# =====================================
# Crear Aplicación FastAPI
# =====================================

app = FastAPI(
    title="Proyecto TI - Sistema Integrado",
    description="Backend para gestión de subscripciones y módulo de salud",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# =====================================
# Incluir Routers por Módulo
# =====================================

# Módulo de Salud
app.include_router(health_router)

# =====================================
# Endpoints Raíz
# =====================================

@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "Proyecto TI - Backend",
        "version": "1.0.0",
        "modules": {
            "subscripciones": "Módulo de gestión de subscripciones",
            "salud": "Módulo de gestión de salud con Data Warehouse"
        },
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health/status"
    }


@app.get("/health/status", tags=["General"])
async def health_status():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.post("/seed/salud", tags=["Admin"])
async def seed_health_data(db: Session = Depends(get_db)):
    """
    Genera datos de prueba para el módulo de salud.
    ⚠️ ADVERTENCIA: Útil solo para desarrollo/testing
    """
    from app.modules.health.scripts.seed import run_seed
    
    result = run_seed(db)
    return {
        "message": "Seed data creado exitosamente",
        "data": result
    }


# =====================================
# Información de la Aplicación
# =====================================

@app.get("/info", tags=["General"])
async def app_info():
    """Información sobre la aplicación y módulos disponibles"""
    return {
        "name": "Proyecto TI",
        "version": "1.0.0",
        "modules": {
            "subscripciones": {
                "status": "active",
                "database": "PostgreSQL (puerto 5434)",
                "routes": "/api/v1/subscripciones"
            },
            "salud": {
                "status": "active",
                "database": "PostgreSQL (puerto 5435)",
                "architecture": "Data Warehouse (Raw + Warehouse)",
                "routes": "/api/v1/salud",
                "endpoints": {
                    "pacientes": "/api/v1/salud/pacientes",
                    "visitas": "/api/v1/salud/visitas",
                    "alertas": "/api/v1/salud/alertas",
                    "dashboard": "/api/v1/salud/dashboard"
                }
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

