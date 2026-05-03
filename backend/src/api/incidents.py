from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
from datetime import datetime
from ..database import SessionLocal, WorkItem

router = APIRouter()


@router.get(
    "/incidents",
    summary="📋 List All Incidents",
    description="Retrieve incidents with optional filtering"
)
async def list_incidents(
    state: Optional[str] = Query(
        None,
        description="Filter by state",
        example="OPEN",
        enum=["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"]
    ),
    severity: Optional[str] = Query(
        None,
        description="Filter by severity",
        example="CRITICAL",
        enum=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    ),
    limit: int = Query(100, ge=1, le=1000, description="Max results")
):
    """
    # 📋 Get All Incidents
    
    **Query Parameters:**
    - `state`: Filter by OPEN, INVESTIGATING, RESOLVED, CLOSED
    - `severity`: Filter by CRITICAL, HIGH, MEDIUM, LOW
    - `limit`: Max results (1-1000)
    
    **Examples:**
    ```
    GET /api/incidents?state=OPEN
    GET /api/incidents?severity=CRITICAL
    GET /api/incidents?state=OPEN&severity=CRITICAL
    ```
    """
    db = SessionLocal()

    try:
        query = db.query(WorkItem)
        filters = []

        if state:
            query = query.filter(WorkItem.state == state)
            filters.append(f"state={state}")

        if severity:
            query = query.filter(WorkItem.severity == severity)
            filters.append(f"severity={severity}")

        items = query.order_by(WorkItem.created_at.desc()).limit(limit).all()

        now = datetime.utcnow()
        incidents = []

        for wi in items:
            age_min = int((now - wi.created_at).total_seconds() / 60)
            incidents.append({
                "id": wi.id,
                "component_id": wi.component_id,
                "severity": wi.severity,
                "state": wi.state,
                "signal_count": wi.signal_count,
                "created_at": wi.created_at.isoformat() + "Z",
                "age_minutes": age_min
            })

        return {
            "count": len(incidents),
            "filter_applied": ", ".join(filters) if filters else "none",
            "incidents": incidents,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    finally:
        db.close()


@router.get(
    "/incidents/{incident_id}",
    summary="🔍 Get Incident Details",
    description="Get complete details of a specific incident"
)
async def get_incident(
    incident_id: int = Path(..., description="Incident ID", example=12, ge=1)
):
    """
    # 🔍 Incident Details
    
    Get complete information about an incident.
    
    **Example:**
    ```
    GET /api/incidents/12
    ```
    """
    db = SessionLocal()

    try:
        wi = db.query(WorkItem).filter(WorkItem.id == incident_id).first()

        if not wi:
            raise HTTPException(404, f"Incident #{incident_id} not found")

        age_min = int((datetime.utcnow() - wi.created_at).total_seconds() / 60)

        return {
            "id": wi.id,
            "component_id": wi.component_id,
            "severity": wi.severity,
            "state": wi.state,
            "signal_count": wi.signal_count,
            "created_at": wi.created_at.isoformat() + "Z",
            "age_minutes": age_min
        }

    finally:
        db.close()


@router.patch(
    "/incidents/{incident_id}/state",
    summary="🔄 Update State",
    description="Transition incident to new state"
)
async def update_state(
    incident_id: int = Path(..., example=12),
    new_state: str = Query(
        ...,
        example="INVESTIGATING",
        enum=["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"]
    )
):
    """
    # 🔄 Update Incident State
    
    **Valid Transitions:**
    - OPEN → INVESTIGATING
    - INVESTIGATING → RESOLVED
    - RESOLVED → CLOSED (requires RCA)
    
    **Example:**
    ```
    PATCH /api/incidents/12/state?new_state=INVESTIGATING
    ```
    """
    db = SessionLocal()

    try:
        wi = db.query(WorkItem).filter(WorkItem.id == incident_id).first()

        if not wi:
            raise HTTPException(404, "Incident not found")

        valid_transitions = {
            "OPEN": ["INVESTIGATING"],
            "INVESTIGATING": ["OPEN", "RESOLVED"],
            "RESOLVED": ["INVESTIGATING", "CLOSED"],
            "CLOSED": []
        }

        if new_state not in valid_transitions.get(wi.state, []):
            raise HTTPException(
                400,
                f"Invalid: {wi.state} → {new_state}. Allowed: {valid_transitions[wi.state]}"
            )

        prev = wi.state
        wi.state = new_state
        wi.updated_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "incident_id": incident_id,
            "previous_state": prev,
            "new_state": new_state,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    finally:
        db.close()
