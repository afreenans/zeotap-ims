from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import asyncio
import time
from datetime import datetime

signal_processor = None
metrics_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global signal_processor, metrics_task

    from .database import init_db
    from .services.signal_processor import SignalProcessor

    print("🚀 Starting Zeotap IMS Backend...")

    init_db()
    signal_processor = SignalProcessor()
    metrics_task = asyncio.create_task(signal_processor.print_metrics())

    yield

    print("🛑 Shutting down gracefully...")
    if metrics_task:
        metrics_task.cancel()


app = FastAPI(
    title="🚨 Incident Management System API",
    description="""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 15px; color: white; box-shadow: 0 10px 40px rgba(0,0,0,0.3); margin-bottom: 30px;">
    <h1 style="margin: 0; font-size: 2.5em;">🚀 Production-Grade Incident Management System</h1>
    <p style="font-size: 1.2em; margin: 10px 0 0 0;">Real-time Monitoring, Alerting & Incident Lifecycle Management</p>
</div>

---

## ⚡ Core Features

| Feature | Description |
|---------|-------------|
| **High Throughput** | 10,000+ signals/second with async processing |
| **Smart Debouncing** | 10-second aggregation windows to reduce noise |
| **Multi-tier Storage** | PostgreSQL (Work Items) + MongoDB (Signals) + Redis (Cache) |
| **State Management** | State Pattern for enforced lifecycle transitions |
| **Priority Alerting** | Strategy Pattern with P0/P1/P2 severity levels |
| **Monitoring** | Prometheus metrics + Grafana dashboards |

---

## 🏗️ System Architecture

---

## 📊 Monitoring Endpoints

- **Prometheus Metrics:** [/metrics](/metrics)
- **Grafana Dashboard:** [http://localhost:3001](http://localhost:3001)
- **Health Check:** [/health](/health)
    """,
    version="2.0.0",
    lifespan=lifespan,
    contact={
        "name": "Zeotap IMS Team",
        "email": "ims@zeotap.com"
    }
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="🚨 Incident Management System",
        version="2.0.0",
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["tags"] = [
        {
            "name": "System",
            "description": "⚙️ System health monitoring, metrics, and status endpoints"
        },
        {
            "name": "Signals",
            "description": "📡 High-throughput signal ingestion (10K signals/sec)"
        },
        {
            "name": "Incidents",
            "description": "📋 Complete incident lifecycle management"
        },
        {
            "name": "Monitoring",
            "description": "📊 Prometheus metrics and observability"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .api import incidents, signals

app.include_router(incidents.router, prefix="/api", tags=["Incidents"])
app.include_router(signals.router, prefix="/api", tags=["Signals"])


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "🚨 Incident Management System API",
        "version": "2.0.0",
        "status": "operational",
        "monitoring": {
            "metrics": "/metrics",
            "grafana": "http://localhost:3001",
            "health": "/health"
        }
    }


@app.get("/health", tags=["System"])
async def health():
    metrics_data = {
        "status": "healthy",
        "service": "zeotap-ims-backend",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if signal_processor:
        buffer_size = len(signal_processor.signal_buffer)
        metrics_data.update({
            "throughput": signal_processor.signal_counter["count"],
            "buffer_size": buffer_size,
            "buffer_capacity": 100000,
            "utilization_percent": round((buffer_size / 100000) * 100, 2)
        })

    return metrics_data


@app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
async def metrics():
    """
    Prometheus metrics endpoint
    
    Returns metrics in Prometheus exposition format.
    """
    from .metrics import get_metrics
    return get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
