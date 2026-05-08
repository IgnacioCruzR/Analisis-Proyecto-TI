from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class DimProfesional(Base):
    __tablename__ = "dim_profesionales"
    
    # Primary Key (Surrogate)
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Business Key
    profesional_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True, unique=True)
    
    # Attributes
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    profesion = Column(String(50))
    numero_registro = Column(String(50))
    
    # Specialties and zones
    especialidades = Column(String(500))  # JSON serialized
    zonas = Column(String(500))           # JSON serialized
    
    # Status
    activo = Column(String(20), default="active")
    
    # Metrics
    total_visitas = Column(Integer, default=0)
    pacientes_atendidos = Column(Integer, default=0)
    tasa_completacion = Column(String(5))  # "95.2%"
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_dim_profesionales_profesion", "profesion"),
        Index("idx_dim_profesionales_activo", "activo"),
    )
    
    def __repr__(self):
        return f"<DimProfesional(id={self.id}, nombres={self.nombres} {self.apellidos})>"
