
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import Alert


def save_alert(
    db: Session,
    metric_name: str,
    severity: str,
    message: str,
    metric_value: float,
    threshold: float
) -> Alert:
    alert = (
        db.query(Alert)
        .filter(
            Alert.metric_name == metric_name,
            Alert.resolved_at.is_(None)
        )
        .order_by(Alert.created_at.desc())
        .first()
    )

    if alert:
        alert.severity = severity
        alert.message = message
        alert.metric_value = metric_value
        alert.threshold = threshold
    else:
        alert = Alert(
            metric_name=metric_name,
            severity=severity,
            message=message,
            metric_value=metric_value,
            threshold=threshold
        )
        db.add(alert)

    db.commit()
    db.refresh(alert)

    return alert


def resolve_alerts(
    db: Session,
    metric_name: str
) -> int:
    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.metric_name == metric_name,
            Alert.resolved_at.is_(None)
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for alert in active_alerts:
        alert.resolved_at = now

    db.commit()

    return len(active_alerts)

