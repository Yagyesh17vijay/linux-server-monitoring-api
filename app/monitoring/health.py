
from sqlalchemy.orm import Session

from app.monitoring.cpu import get_cpu_metrics
from app.monitoring.memory import get_memory_metrics
from app.monitoring.disk import get_disk_metrics
from app.database.alerts import save_alert, resolve_alerts

CPU_WARNING_THRESHOLD = 70
CPU_CRITICAL_THRESHOLD = 90

MEMORY_WARNING_THRESHOLD = 75
MEMORY_CRITICAL_THRESHOLD = 90

DISK_WARNING_THRESHOLD = 80
DISK_CRITICAL_THRESHOLD = 95


def evaluate_metric(
    metric: str,
    value: float,
    warning_threshold: float,
    critical_threshold: float
) -> dict:
    if value >= critical_threshold:
        status = "Critical"
        message = f"{metric.capitalize()} usage is critically high"
    elif value >= warning_threshold:
        status = "Warning"
        message = f"{metric.capitalize()} usage is high"
    else:
        status = "Normal"
        message = f"{metric.capitalize()} usage is normal"

    return {
        "metric": metric,
        "status": status,
        "value": value,
        "message": message
    }


def get_health_status(db: Session | None = None) -> dict:
    cpu = get_cpu_metrics()
    memory = get_memory_metrics()
    disks = get_disk_metrics()

    checks = []

    cpu_check = evaluate_metric(
        "cpu",
        cpu["cpu_usage_percent"],
        CPU_WARNING_THRESHOLD,
        CPU_CRITICAL_THRESHOLD
    )
    checks.append(cpu_check)

    memory_check = evaluate_metric(
        "memory",
        memory["memory_usage_percent"],
        MEMORY_WARNING_THRESHOLD,
        MEMORY_CRITICAL_THRESHOLD
    )
    checks.append(memory_check)

    for disk in disks:
        disk_check = evaluate_metric(
            "disk",
            disk["usage_percent"],
            DISK_WARNING_THRESHOLD,
            DISK_CRITICAL_THRESHOLD
        )
        disk_check["mountpoint"] = disk["mountpoint"]
        checks.append(disk_check)

    if any(check["status"] == "Critical" for check in checks):
        overall_status = "Critical"
    elif any(check["status"] == "Warning" for check in checks):
        overall_status = "Warning"
    else:
        overall_status = "Normal"

   
    # Save or resolve alerts when a database session is supplied.
    if db is not None:
        for check in checks:
            metric_name = check["metric"]

            if "mountpoint" in check:
                metric_name = f"disk:{check['mountpoint']}"

            if check["status"] == "Normal":
                resolve_alerts(
                    db=db,
                    metric_name=metric_name
                )
                continue

            if check["metric"] == "cpu":
                threshold = (
                    CPU_CRITICAL_THRESHOLD
                    if check["status"] == "Critical"
                    else CPU_WARNING_THRESHOLD
                )
            elif check["metric"] == "memory":
                threshold = (
                    MEMORY_CRITICAL_THRESHOLD
                    if check["status"] == "Critical"
                    else MEMORY_WARNING_THRESHOLD
                )
            else:
                threshold = (
                    DISK_CRITICAL_THRESHOLD
                    if check["status"] == "Critical"
                    else DISK_WARNING_THRESHOLD
                )

            save_alert(
                db=db,
                metric_name=metric_name,
                severity=check["status"],
                message=check["message"],
                metric_value=check["value"],
                threshold=threshold
            )


    return {
        "overall_status": overall_status,
        "checks": checks
    }
