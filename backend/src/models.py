from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SignalInput(BaseModel):
    component_id: str = Field(..., description="Component identifier")
    error_message: str = Field(..., description="Error description")
    error_type: str = Field(default="ERROR", description="Type of error")
    severity: str = Field(default="MEDIUM", description="Severity level")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata")

class WorkItemResponse(BaseModel):
    id: int
    component_id: str
    severity: str
    state: str
    signal_count: int
    created_at: datetime
    updated_at: datetime

class RCAInput(BaseModel):
    root_cause_category: str = Field(..., description="Category of root cause")
    fix_applied: str = Field(..., description="Fix that was applied")
    prevention_steps: str = Field(..., description="Steps to prevent recurrence")
    start_time: datetime = Field(..., description="Incident start time")
    end_time: datetime = Field(..., description="Incident end time")

class RCAResponse(BaseModel):
    id: int
    work_item_id: int
    root_cause_category: str
    fix_applied: str
    prevention_steps: str
    mttr_seconds: int
    start_time: datetime
    end_time: datetime
