
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Text

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password = Column(String, nullable=False)


class MetricHistory(Base):
    __tablename__ = "metric_history"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    metric_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )