from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class RawPaciente(Base):
    __tablename__ = "raw_pacientes"
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event info
    event_type = Column(String(50), nullable=False, index=True)  # created, updated, deleted
    source = Column(String(50), nullable=False, default="health_module", index=True)
    
    # Paciente data
    rut = Column(String(20))
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date)
    sexo = Column(String(20))
    telefono = Column(String(30))
    email = Column(String(150))
    direccion = Column(String(255))
    zona_id = Column(PG_UUID(as_uuid=True))
    
    # Processing
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_raw_pacientes_source_type", "source", "event_type"),
        Index("idx_raw_pacientes_processed_created", "processed", "created_at"),
    )
    
    def __repr__(self):
        return f"<RawPaciente(id={self.id}, event_type={self.event_type}, nombres={self.nombres})>"
