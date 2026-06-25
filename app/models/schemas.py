from pydantic import BaseModel, Field
from typing import Optional, Literal
from app.models.enums import CaseType, Severity, Department

class TicketRequest(BaseModel):
    ticket_id: str = Field(..., description="Echo this value back in the response")
    channel: Optional[Literal["app", "sms", "call_center", "merchant_portal"]] = Field(None, description="One of: app, sms, call_center, merchant_portal")
    locale: Optional[Literal["bn", "en", "mixed"]] = Field(None, description="One of: bn, en, mixed")
    message: str = Field(..., min_length=1, description="Free text customer complaint")

class TicketResponse(BaseModel):
    ticket_id: str
    case_type: CaseType
    severity: Severity
    department: Department
    agent_summary: str
    human_review_required: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
