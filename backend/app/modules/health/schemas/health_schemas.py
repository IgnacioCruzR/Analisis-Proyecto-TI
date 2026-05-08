# Color palette from design system
# Graphite: #353535
# Stormy Teal: #3C6E71
# White: #FFFFFF
# Alabaster Grey: #D9D9D9
# Yale Blue: #284B63

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class PacienteBase(BaseModel):
    rut: Optional[str] = Field(None, description="RUT del paciente")
    nombres: str = Field(..., description="Nombres del paciente")
    apellidos: str = Field(..., description="Apellidos del paciente")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento (YYYY-MM-DD)")
    sexo: Optional[str] = Field(None, description="Sexo (M/F/Otro)")
    telefono: Optional[str] = Field(None, description="Teléfono de contacto")
    email: Optional[str] = Field(None, description="Email del paciente")
    direccion: Optional[str] = Field(None, description="Dirección")
    zona_id: Optional[UUID] = Field(None, description="ID de la zona")


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class PacienteResponse(PacienteBase):
    id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VisitaBase(BaseModel):
    paciente_id: UUID = Field(..., description="ID del paciente")
    profesional_salud_id: UUID = Field(..., description="ID del profesional de salud")
    zona_id: Optional[UUID] = Field(None, description="ID de la zona")
    fecha_programada: str = Field(..., description="Fecha programada (YYYY-MM-DD)")
    hora_programada: str = Field(..., description="Hora programada (HH:MM:SS)")
    estado: str = Field(default="programada", description="Estado de la visita")


class VisitaCreate(VisitaBase):
    pass


class VisitaUpdate(BaseModel):
    estado: Optional[str] = None
    fecha_hora_inicio_real: Optional[datetime] = None
    fecha_hora_fin_real: Optional[datetime] = None


class VisitaResponse(VisitaBase):
    id: UUID
    fecha_hora_inicio_real: Optional[datetime] = None
    fecha_hora_fin_real: Optional[datetime] = None
    creada_por_usuario_id: Optional[UUID] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertaBase(BaseModel):
    paciente_id: UUID = Field(..., description="ID del paciente")
    visita_id: Optional[UUID] = Field(None, description="ID de la visita")
    tipo: str = Field(..., description="Tipo de alerta")
    mensaje: str = Field(..., description="Mensaje de la alerta")
    prioridad: str = Field(..., description="Prioridad: LOW, MEDIUM, HIGH, CRITICAL")
    estado: str = Field(default="open", description="Estado: OPEN, ACKNOWLEDGED, RESOLVED")


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    mensaje: Optional[str] = None


class AlertaResponse(AlertaBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FichaClinicaBase(BaseModel):
    visita_id: UUID = Field(..., description="ID de la visita")
    estado: str = Field(default="draft", description="Estado: draft, in_progress, finalized")
    contenido: Optional[dict] = Field(None, description="Contenido de la ficha en JSON")


class FichaClinicaCreate(FichaClinicaBase):
    pass


class FichaClinicaUpdate(BaseModel):
    estado: Optional[str] = None
    contenido: Optional[dict] = None


class FichaClinicaResponse(FichaClinicaBase):
    id: UUID
    creada_por_usuario_id: Optional[UUID] = None
    actualizada_por_usuario_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DashboardSalud(BaseModel):
    """Schema para dashboard del módulo de salud"""
    total_pacientes: int = Field(0, description="Total de pacientes")
    total_visitas: int = Field(0, description="Total de visitas")
    visitas_completadas: int = Field(0, description="Visitas completadas")
    visitas_pendientes: int = Field(0, description="Visitas pendientes")
    alertas_criticas: int = Field(0, description="Alertas críticas")
    alertas_altas: int = Field(0, description="Alertas altas")
    tasa_completacion: str = Field("0%", description="Tasa de completación de visitas")
    
    class Config:
        # Colores del sistema para referencias en frontend
        color_critico = "#353535"  # Graphite
        color_alerta = "#284B63"   # Yale Blue
        color_exito = "#3C6E71"    # Stormy Teal
        color_neutro = "#D9D9D9"   # Alabaster Grey
