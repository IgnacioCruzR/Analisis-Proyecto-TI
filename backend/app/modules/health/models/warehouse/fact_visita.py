from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class FactVisita(Base):
    __tablename__ = "fact_visitas"
    
    # Primary Key (Surrogate)
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Business Keys (Dimensions)
    visita_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True, unique=True)
    paciente_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    profesional_id = Column(PG_UUID(as_uuid=True), nullable=False)
    zona_id = Column(PG_UUID(as_uuid=True))
    
    # Fact Measures
    duracion_minutos = Column(Integer)
    estado = Column(String(30))
    completada = Column(Boolean, default=False)
    tuvo_alerta = Column(Boolean, default=False)
    alerta_critica = Column(Boolean, default=False)
    
    # Dates
    fecha_visita = Column(String(20))  # YYYY-MM-DD
    hora_inicio = Column(String(8))
    hora_fin = Column(String(8))
    
    # Metadata
    documentos_adjuntos = Column(Integer, default=0)
    notas_clinicas = Column(Boolean, default=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_fact_visitas_paciente_fecha", "paciente_id", "fecha_visita"),
        Index("idx_fact_visitas_profesional", "profesional_id"),
        Index("idx_fact_visitas_zona", "zona_id"),
        Index("idx_fact_visitas_completada", "completada"),
    )
    
    def __repr__(self):
        return f"<FactVisita(id={self.id}, estado={self.estado}, completada={self.completada})>"
