from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class FactAlerta(Base):
    __tablename__ = "fact_alertas"
    
    # Primary Key (Surrogate)
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Business Keys (Dimensions)
    alerta_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True, unique=True)
    paciente_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    visita_id = Column(PG_UUID(as_uuid=True))
    
    # Fact Measures
    tipo = Column(String(50))
    prioridad = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    estado = Column(String(20))     # OPEN, ACKNOWLEDGED, RESOLVED
    
    # Timing
    minutos_sin_resolver = Column(Integer)
    resuelta = Column(String(20), default="pending")  # pending, resolved, escalated
    
    # Count metrics
    escalamientos = Column(Integer, default=0)
    intentos_contacto = Column(Integer, default=0)
    
    # Dates
    fecha_creacion = Column(String(20))  # YYYY-MM-DD
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_fact_alertas_paciente", "paciente_id"),
        Index("idx_fact_alertas_prioridad", "prioridad"),
        Index("idx_fact_alertas_estado", "estado"),
        Index("idx_fact_alertas_resuelta", "resuelta"),
    )
    
    def __repr__(self):
        return f"<FactAlerta(id={self.id}, tipo={self.tipo}, prioridad={self.prioridad})>"
