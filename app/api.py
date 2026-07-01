"""
FastAPI REST layer for the system health monitor.
Run with: uvicorn app.api:app --reload --port 8001
"""
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .monitor import run_health_check

app = FastAPI(title="DevOps Toolkit API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    result = run_health_check()
    result["timestamp"] = time.time()
    return result


@app.get("/metrics")
def metrics():
    result = run_health_check()
    return {
        "timestamp": time.time(),
        "overall_status": result["overall_status"],
        "metrics": result["metrics"],
    }
