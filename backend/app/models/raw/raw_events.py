from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy import JSON
from app.db.base import Base


class RawEvent(Base):
    __tablename__ = "raw_events"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Event Source (e.g., "subscriptions", "orders", "iot_devices")
    source = Column(String(50), nullable=False, index=True)
    
    # Event Type (e.g., "subscription_created", "order_placed")
    event_type = Column(String(100), nullable=False, index=True)
    
    # Event payload in JSON for flexibility (works with SQLite and Postgres)
    payload = Column(JSON, nullable=True)
    
    # Processing flag
    processed = Column(Boolean, default=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Composite index for efficient filtering
    __table_args__ = (
        Index("idx_raw_events_source_type", "source", "event_type"),
        Index("idx_raw_events_processed_created", "processed", "created_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<RawEvent(id={self.id}, source={self.source}, "
            f"event_type={self.event_type}, processed={self.processed})>"
        )
