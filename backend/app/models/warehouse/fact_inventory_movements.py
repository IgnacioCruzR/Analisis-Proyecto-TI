from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class FactInventoryMovement(Base):
    """Un registro por evento de movimiento de stock (received, reserved, dispatched, adjusted, transfer)."""

    __tablename__ = "fact_inventory_movements"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(String(50), nullable=False, index=True)
    sku_id = Column(String(100), nullable=False, index=True)
    location_id = Column(String(100), nullable=True, index=True)
    quantity = Column(Integer, nullable=True)

    # Campos opcionales según el event_type
    reservation_id = Column(String(100), nullable=True)
    order_id = Column(String(100), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    raw_event_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    movement_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    ingested_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_fim_sku_event_ts", "sku_id", "event_type", "movement_at"),
        Index("idx_fim_location_ts", "location_id", "movement_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<FactInventoryMovement(id={self.id}, event_type={self.event_type}, "
            f"sku_id={self.sku_id}, quantity={self.quantity})>"
        )
