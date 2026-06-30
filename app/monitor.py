"""
System health monitor — reports CPU, memory, disk and network stats.
Designed to be lightweight, testable and CI/CD friendly.
"""
import platform
import psutil
from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Metric:
    name: str
    value: float
    unit: str
    status: HealthStatus

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": round(self.value, 2),
            "unit": self.unit,
            "status": self.status.value,
        }


def _classify(value: float, warn: float, critical: float) -> HealthStatus:
    if value >= critical:
        return HealthStatus.CRITICAL
    if value >= warn:
        return HealthStatus.WARNING
    return HealthStatus.OK


def get_cpu() -> Metric:
    usage = psutil.cpu_percent(interval=0.5)
    return Metric("cpu_usage", usage, "%", _classify(usage, warn=70, critical=90))


def get_memory() -> Metric:
    mem = psutil.virtual_memory()
    used_pct = mem.percent
    return Metric("memory_usage", used_pct, "%", _classify(used_pct, warn=75, critical=90))


def get_disk(path: str = "/") -> Metric:
    disk = psutil.disk_usage(path)
    used_pct = disk.percent
    return Metric("disk_usage", used_pct, "%", _classify(used_pct, warn=80, critical=95))


def get_system_info() -> dict:
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


def run_health_check(disk_path: str = "/") -> dict:
    """
    Ejecuta un health check completo del sistema.
    Devuelve un diccionario con métricas y estado global.
    """
    metrics = [
        get_cpu(),
        get_memory(),
        get_disk(disk_path),
    ]

    # Estado global: el peor de todos los individuales
    statuses = [m.status for m in metrics]
    if HealthStatus.CRITICAL in statuses:
        overall = HealthStatus.CRITICAL
    elif HealthStatus.WARNING in statuses:
        overall = HealthStatus.WARNING
    else:
        overall = HealthStatus.OK

    return {
        "overall_status": overall.value,
        "system": get_system_info(),
        "metrics": [m.to_dict() for m in metrics],
    }
