
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.monitoring.processes import get_process_metrics
from app.monitoring.health import get_health_status
from app.monitoring.metrics_collector import collect_and_save_metrics

from typing import Optional

from app.database.models import MetricHistory
from app.schemas.metrics import MetricHistoryResponse

from app.database.models import Alert
from app.schemas.alerts import AlertResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["Monitoring"]
)


@router.get("/processes")
def get_processes(
    limit: int = Query(default=10, ge=1, le=100),
    username: str = Depends(get_current_user)
):
    processes = get_process_metrics(limit)

    return {
        "server": "Linux",
        "requested_by": username,
        "process_count": len(processes),
        "processes": processes
    }


@router.get("/health")
def get_health(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    health = get_health_status(db)

    return {
        "server": "Linux",
        "requested_by": username,
        **health
    }


@router.post("/metrics/collect")
def collect_metrics(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    result = collect_and_save_metrics(db)

    return {
        "message": "Metrics collected and saved successfully",
        "requested_by": username,
        **result
    }


@router.get(
    "/metrics",
    response_model=list[MetricHistoryResponse]
)
def get_metric_history(
    metric_name: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    query = db.query(MetricHistory)

    if metric_name:
        query = query.filter(
            MetricHistory.metric_name == metric_name
        )

    return (
        query.order_by(MetricHistory.recorded_at.desc())
        .limit(limit)
        .all()
    )

@router.get(
    "/alerts",
    response_model=list[AlertResponse]
)
def get_alerts(
    severity: str | None = Query(
        default=None,
        pattern="^(Warning|Critical)$"
    ),
    is_resolved: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)

    if is_resolved is True:
        query = query.filter(Alert.resolved_at.is_not(None))
    elif is_resolved is False:
        query = query.filter(Alert.resolved_at.is_(None))

    return (
        query.order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )
