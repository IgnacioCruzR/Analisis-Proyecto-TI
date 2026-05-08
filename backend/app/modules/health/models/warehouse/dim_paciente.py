from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Index, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from app.db.base import Base


class DimPaciente(Base):
    __tablename__ = "dim_pacientes"
    
    # Primary Key (Surrogate)
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Business Key
    paciente_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True, unique=True)
    
    # Attributes
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    rut = Column(String(20), index=True)
    sexo = Column(String(20))
    
    # Calculated fields
    edad = Column(Integer)
    zona = Column(String(100))
    
    # Status
    activo = Column(String(20), default="active")
    
    # Metrics
    total_visitas = Column(Integer, default=0)
    total_alertas = Column(Integer, default=0)
    alertas_criticas = Column(Integer, default=0)
    ultima_visita = Column(String(20))  # YYYY-MM-DD
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_dim_pacientes_rut", "rut"),
        Index("idx_dim_pacientes_zona", "zona"),
        Index("idx_dim_pacientes_activo", "activo"),
    )
    
    def __repr__(self):
        return f"<DimPaciente(id={self.id}, nombres={self.nombres} {self.apellidos})>"
