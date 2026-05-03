from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Counters
signals_ingested_total = Counter(
    'ims_signals_ingested_total',
    'Total number of signals ingested',
    ['component_type', 'severity']
)

incidents_created_total = Counter(
    'ims_incidents_created_total',
    'Total number of incidents created',
    ['severity', 'component_type']
)

state_transitions_total = Counter(
    'ims_state_transitions_total',
    'Total state transitions',
    ['from_state', 'to_state']
)

api_requests_total = Counter(
    'ims_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# Gauges
active_incidents = Gauge(
    'ims_active_incidents',
    'Number of active incidents',
    ['state', 'severity']
)

signal_buffer_size = Gauge(
    'ims_signal_buffer_size',
    'Current size of signal buffer'
)

signal_processing_rate = Gauge(
    'ims_signal_processing_rate',
    'Signals processed per second'
)

# Histograms
signal_processing_duration = Histogram(
    'ims_signal_processing_duration_seconds',
    'Time to process a signal',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

api_response_time = Histogram(
    'ims_api_response_time_seconds',
    'API response time',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)


def get_component_type(component_id: str) -> str:
    """Extract component type from ID"""
    if "RDBMS" in component_id:
        return "rdbms"
    elif "API" in component_id:
        return "api"
    elif "CACHE" in component_id:
        return "cache"
    elif "QUEUE" in component_id:
        return "queue"
    elif "NOSQL" in component_id:
        return "nosql"
    return "other"


def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
