FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-c", "from app.monitor import run_health_check; import json; print(json.dumps(run_health_check(), indent=2))"]
