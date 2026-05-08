from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import uuid
from app.db.base import Base


class RawFichaClinica(Base):
    __tablename__ = "raw_fichas_clinicas"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event info
    event_type = Column(String(50), nullable=False, index=True)  # created, updated, finalized
    source = Column(String(50), nullable=False, default="health_module", index=True)
    
    # Ficha data
    visita_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    estado = Column(String(30))
    contenido = Column(JSONB)
    creada_por_usuario_id = Column(PG_UUID(as_uuid=True))
    actualizada_por_usuario_id = Column(PG_UUID(as_uuid=True))
    
    # Processing
    processed = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_raw_fichas_source_type", "source", "event_type"),
        Index("idx_raw_fichas_visita_id", "visita_id"),
        Index("idx_raw_fichas_processed_created", "processed", "created_at"),
    )
    
    def __repr__(self):
        return f"<RawFichaClinica(id={self.id}, event_type={self.event_type}, estado={self.estado})>"
