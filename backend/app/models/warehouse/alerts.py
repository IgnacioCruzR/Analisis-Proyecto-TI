from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import JSON

from app.db.base import Base


class PriorityAlert(Base):
    __tablename__ = "priority_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False)
    message = Column(String(1000), nullable=False)
    metadata = Column(JSON, nullable=True)
    acknowledged = Column(Boolean, default=False, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<PriorityAlert(id={self.id}, type={self.alert_type}, severity={self.severity})>"
