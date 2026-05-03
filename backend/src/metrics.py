from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi import Response

# Clear any existing metrics
REGISTRY._collector_to_names.clear()
REGISTRY._names_to_collectors.clear()

# Define metrics
signals_total = Counter(
    'ims_signals_total',
    'Total signals ingested',
    registry=REGISTRY
)

incidents_total = Counter(
    'ims_incidents_total',
    'Total incidents created',
    registry=REGISTRY
)

buffer_size = Gauge(
    'ims_buffer_size',
    'Current signal buffer size',
    registry=REGISTRY
)

active_incidents_count = Gauge(
    'ims_active_incidents',
    'Number of active incidents',
    registry=REGISTRY
)

def get_metrics():
    """Return Prometheus metrics"""
    return Response(
        generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )
