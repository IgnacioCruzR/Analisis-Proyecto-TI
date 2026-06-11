from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class FactInventoryAlert(Base):
    """Un registro por alerta crítica de stock (critical_threshold_reached, stock_out_error)."""

    __tablename__ = "fact_inventory_alerts"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(String(50), nullable=False, index=True)    # critical_threshold_reached | stock_out_error
    sku_id = Column(String(100), nullable=False, index=True)
    location_id = Column(String(100), nullable=True, index=True)
    current_stock = Column(Integer, nullable=True)
    threshold_limite = Column(Integer, nullable=True)
    is_stock_out = Column(Boolean, nullable=False, default=False)

    raw_event_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    alert_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    ingested_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_fia_sku_alert_ts", "sku_id", "alert_at"),
        Index("idx_fia_event_type_ts", "event_type", "alert_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<FactInventoryAlert(id={self.id}, event_type={self.event_type}, "
            f"sku_id={self.sku_id}, current_stock={self.current_stock})>"
        )
