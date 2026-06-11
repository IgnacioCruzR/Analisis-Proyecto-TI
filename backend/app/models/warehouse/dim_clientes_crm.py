from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, Integer, String

from app.db.base import Base


class DimClienteCRM(Base):
    __tablename__ = "dim_clientes_crm"

    id = Column(Integer, primary_key=True, index=True)

    cliente_identidad_id = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    telefono = Column(String(30), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_dim_clientes_crm_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<DimClienteCRM(cliente_identidad_id={self.cliente_identidad_id}, email={self.email})>"
