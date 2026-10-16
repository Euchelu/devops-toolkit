# DevOps Toolkit

[![CI/CD Pipeline](https://github.com/Euchelu/devops-toolkit/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Euchelu/devops-toolkit/actions/workflows/ci-cd.yml)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)

System health monitor with a full **4-stage CI/CD pipeline** using GitHub Actions.

## CI/CD Pipeline

```
push to main
     │
     ▼
┌─────────┐     ┌─────────┐     ┌──────────────┐     ┌────────┐
│  Lint   │────▶│  Test   │────▶│ Docker Build │────▶│ Deploy │
│  (ruff) │     │ (pytest)│     │  & Verify    │     │  (sim) │
└─────────┘     └─────────┘     └──────────────┘     └────────┘
```

Each stage only runs if the previous one passes. A failed lint blocks tests; failed tests block the Docker build.

## Tech Stack

- **psutil** — Cross-platform system metrics (CPU, memory, disk)
- **pytest + pytest-cov** — Testing with coverage report
- **ruff** — Fast Python linter
- **Docker** — Containerized build and run
- **GitHub Actions** — CI/CD automation

## Project Structure

```
devops-toolkit/
├── app/
│   └── monitor.py            # Health check logic
├── tests/
│   └── test_monitor.py       # 18 tests with mocks
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # 4-stage pipeline definition
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt
```

## What the Monitor Does

Collects three system metrics and classifies each as `ok`, `warning` or `critical`:

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU usage | ≥ 70% | ≥ 90% |
| Memory usage | ≥ 75% | ≥ 90% |
| Disk usage | ≥ 80% | ≥ 95% |

Overall status is the worst individual metric.

## Getting Started

### Run with Docker

```bash
docker build -t devops-toolkit .
docker run --rm devops-toolkit
```

Example output:
```json
{
  "overall_status": "ok",
  "system": {
    "os": "Linux",
    "hostname": "myserver",
    "python_version": "3.13.0"
  },
  "metrics": [
    { "name": "cpu_usage",    "value": 12.5, "unit": "%", "status": "ok" },
    { "name": "memory_usage", "value": 45.2, "unit": "%", "status": "ok" },
    { "name": "disk_usage",   "value": 38.0, "unit": "%", "status": "ok" }
  ]
}
```

### Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

pip install -r requirements-dev.txt
python -c "from app.monitor import run_health_check; import json; print(json.dumps(run_health_check(), indent=2))"
```

## Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

```
tests/test_monitor.py::test_classify[...]                          PASSED (x5)
tests/test_monitor.py::test_metric_to_dict                         PASSED
tests/test_monitor.py::test_get_cpu_ok                             PASSED
tests/test_monitor.py::test_get_cpu_warning                        PASSED
tests/test_monitor.py::test_get_cpu_critical                       PASSED
tests/test_monitor.py::test_get_memory_ok                          PASSED
tests/test_monitor.py::test_get_memory_critical                    PASSED
tests/test_monitor.py::test_get_disk_ok                            PASSED
tests/test_monitor.py::test_get_disk_warning                       PASSED
tests/test_monitor.py::test_get_system_info_keys                   PASSED
tests/test_monitor.py::test_health_check_overall_ok                PASSED
tests/test_monitor.py::test_health_check_overall_warning           PASSED
tests/test_monitor.py::test_health_check_overall_critical          PASSED
tests/test_monitor.py::test_health_check_critical_overrides_warning PASSED

18 passed in 0.27s
```

## Author

**Euchelu**
- GitHub: [@Euchelu](https://github.com/Euchelu)
- LinkedIn: [José Ángel Ceballos](https://www.linkedin.com/in/josé-ángel-ceballos-rodríguez-a44996346/)
