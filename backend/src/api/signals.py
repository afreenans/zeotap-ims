from fastapi import APIRouter, HTTPException, Path
from ..models import SignalInput

router = APIRouter()


@router.post(
    "/signals",
    summary="📡 Ingest Signal",
    description="High-throughput signal ingestion (10K/sec)"
)
async def ingest_signal(signal: SignalInput):
    """
    # 📡 Ingest Error Signal
    
    **Rate Limit:** 10,000 signals/second
    
    **Example:**
    ```json
    {
        "component_id": "RDBMS_MASTER_01",
        "error_message": "Connection timeout",
        "severity": "CRITICAL"
    }
    ```
    
    **Components:**
    - RDBMS_* → CRITICAL
    - API_* → CRITICAL
    - CACHE_* → HIGH
    - QUEUE_* → HIGH
    """
    from ..main import signal_processor

    try:
        result = await signal_processor.ingest_signal(signal.dict())
        return result
    except Exception as e:
        raise HTTPException(429, str(e))


@router.get(
    "/signals/{component_id}",
    summary="📊 Get Signals",
    description="Get all signals for a component"
)
async def get_signals(
    component_id: str = Path(..., example="CACHE_CLUSTER_01")
):
    """
    # 📊 Get Component Signals
    
    **Example:**
    ```
    GET /api/signals/CACHE_CLUSTER_01
    ```
    """
    return {
        "component_id": component_id,
        "count": 0,
        "signals": [],
        "note": "MongoDB integration coming soon"
    }
