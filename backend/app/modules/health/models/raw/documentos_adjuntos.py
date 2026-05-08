from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class RawDocumentoAdjunto(Base):
    __tablename__ = "raw_documentos_adjuntos"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event info
    event_type = Column(String(50), nullable=False, index=True)  # uploaded, deleted
    source = Column(String(50), nullable=False, default="health_module", index=True)
    
    # Documento data
    ficha_clinica_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    nombre_archivo = Column(String(150))
    tipo_archivo = Column(String(50))
    url = Column(String(500))
    descripcion = Column(String(255))
    tamaño_bytes = Column(String(20))
    
    # Processing
    processed = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_raw_documentos_source_type", "source", "event_type"),
        Index("idx_raw_documentos_ficha_id", "ficha_clinica_id"),
        Index("idx_raw_documentos_processed_created", "processed", "created_at"),
    )
    
    def __repr__(self):
        return f"<RawDocumentoAdjunto(id={self.id}, nombre_archivo={self.nombre_archivo})>"
