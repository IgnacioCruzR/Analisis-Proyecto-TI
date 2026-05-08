from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import uuid
from app.db.base import Base


class RawAlerta(Base):
    __tablename__ = "raw_alertas"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event info
    event_type = Column(String(50), nullable=False, index=True)  # created, updated, resolved, escalated
    source = Column(String(50), nullable=False, default="health_module", index=True)
    
    # Alerta data
    paciente_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    visita_id = Column(PG_UUID(as_uuid=True))
    tipo = Column(String(50))
    mensaje = Column(String(500))
    prioridad = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    estado = Column(String(20))     # OPEN, ACKNOWLEDGED, RESOLVED
    metadata = Column(JSONB)
    
    # Processing
    processed = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_raw_alertas_source_type", "source", "event_type"),
        Index("idx_raw_alertas_paciente_id", "paciente_id"),
        Index("idx_raw_alertas_prioridad", "prioridad"),
        Index("idx_raw_alertas_processed_created", "processed", "created_at"),
    )
    
    def __repr__(self):
        return f"<RawAlerta(id={self.id}, tipo={self.tipo}, prioridad={self.prioridad})>"
