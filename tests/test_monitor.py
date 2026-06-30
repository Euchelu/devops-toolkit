import pytest
from unittest.mock import patch, MagicMock
from app.monitor import (
    _classify, get_cpu, get_memory, get_disk,
    get_system_info, run_health_check,
    HealthStatus, Metric,
)


# ── _classify ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("value,warn,critical,expected", [
    (50,  70, 90, HealthStatus.OK),
    (75,  70, 90, HealthStatus.WARNING),
    (90,  70, 90, HealthStatus.CRITICAL),
    (100, 70, 90, HealthStatus.CRITICAL),
    (69,  70, 90, HealthStatus.OK),
])
def test_classify(value, warn, critical, expected):
    assert _classify(value, warn, critical) == expected


# ── Metric.to_dict ────────────────────────────────────────────────────────────

def test_metric_to_dict():
    m = Metric("cpu_usage", 55.678, "%", HealthStatus.OK)
    d = m.to_dict()
    assert d["name"] == "cpu_usage"
    assert d["value"] == 55.68  # redondeado a 2 decimales
    assert d["unit"] == "%"
    assert d["status"] == "ok"


# ── get_cpu ───────────────────────────────────────────────────────────────────

def test_get_cpu_ok():
    with patch("app.monitor.psutil.cpu_percent", return_value=45.0):
        m = get_cpu()
        assert m.name == "cpu_usage"
        assert m.value == 45.0
        assert m.status == HealthStatus.OK


def test_get_cpu_warning():
    with patch("app.monitor.psutil.cpu_percent", return_value=80.0):
        assert get_cpu().status == HealthStatus.WARNING


def test_get_cpu_critical():
    with patch("app.monitor.psutil.cpu_percent", return_value=95.0):
        assert get_cpu().status == HealthStatus.CRITICAL


# ── get_memory ────────────────────────────────────────────────────────────────

def test_get_memory_ok():
    mock_mem = MagicMock()
    mock_mem.percent = 60.0
    with patch("app.monitor.psutil.virtual_memory", return_value=mock_mem):
        m = get_memory()
        assert m.name == "memory_usage"
        assert m.status == HealthStatus.OK


def test_get_memory_critical():
    mock_mem = MagicMock()
    mock_mem.percent = 95.0
    with patch("app.monitor.psutil.virtual_memory", return_value=mock_mem):
        assert get_memory().status == HealthStatus.CRITICAL


# ── get_disk ──────────────────────────────────────────────────────────────────

def test_get_disk_ok():
    mock_disk = MagicMock()
    mock_disk.percent = 50.0
    with patch("app.monitor.psutil.disk_usage", return_value=mock_disk):
        m = get_disk("/")
        assert m.name == "disk_usage"
        assert m.status == HealthStatus.OK


def test_get_disk_warning():
    mock_disk = MagicMock()
    mock_disk.percent = 85.0
    with patch("app.monitor.psutil.disk_usage", return_value=mock_disk):
        assert get_disk("/").status == HealthStatus.WARNING


# ── get_system_info ───────────────────────────────────────────────────────────

def test_get_system_info_keys():
    info = get_system_info()
    assert "os" in info
    assert "hostname" in info
    assert "python_version" in info
    assert "architecture" in info


# ── run_health_check ──────────────────────────────────────────────────────────

def _mock_metrics(cpu=40.0, mem=50.0, disk=60.0):
    mock_mem = MagicMock(); mock_mem.percent = mem
    mock_disk = MagicMock(); mock_disk.percent = disk
    return (
        patch("app.monitor.psutil.cpu_percent", return_value=cpu),
        patch("app.monitor.psutil.virtual_memory", return_value=mock_mem),
        patch("app.monitor.psutil.disk_usage", return_value=mock_disk),
    )


def test_health_check_overall_ok():
    p1, p2, p3 = _mock_metrics(cpu=40, mem=50, disk=60)
    with p1, p2, p3:
        result = run_health_check()
    assert result["overall_status"] == "ok"
    assert len(result["metrics"]) == 3
    assert "system" in result


def test_health_check_overall_warning():
    p1, p2, p3 = _mock_metrics(cpu=80, mem=50, disk=60)
    with p1, p2, p3:
        result = run_health_check()
    assert result["overall_status"] == "warning"


def test_health_check_overall_critical():
    p1, p2, p3 = _mock_metrics(cpu=95, mem=50, disk=60)
    with p1, p2, p3:
        result = run_health_check()
    assert result["overall_status"] == "critical"


def test_health_check_critical_overrides_warning():
    p1, p2, p3 = _mock_metrics(cpu=95, mem=80, disk=60)
    with p1, p2, p3:
        result = run_health_check()
    assert result["overall_status"] == "critical"
