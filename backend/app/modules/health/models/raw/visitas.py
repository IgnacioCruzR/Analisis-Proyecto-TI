from datetime import datetime
from sqlalchemy import Column, String, DateTime, Time, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class RawVisita(Base):
    __tablename__ = "raw_visitas"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event info
    event_type = Column(String(50), nullable=False, index=True)  # created, updated, completed, cancelled
    source = Column(String(50), nullable=False, default="health_module", index=True)
    
    # Visita data
    paciente_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    profesional_salud_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    zona_id = Column(PG_UUID(as_uuid=True))
    fecha_programada = Column(String(20))  # YYYY-MM-DD
    hora_programada = Column(String(8))    # HH:MM:SS
    fecha_hora_inicio_real = Column(DateTime)
    fecha_hora_fin_real = Column(DateTime)
    estado = Column(String(30))
    creada_por_usuario_id = Column(PG_UUID(as_uuid=True))
    
    # Processing
    processed = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_raw_visitas_source_type", "source", "event_type"),
        Index("idx_raw_visitas_paciente_id", "paciente_id"),
        Index("idx_raw_visitas_profesional_id", "profesional_salud_id"),
        Index("idx_raw_visitas_processed_created", "processed", "created_at"),
    )
    
    def __repr__(self):
        return f"<RawVisita(id={self.id}, event_type={self.event_type}, estado={self.estado})>"
