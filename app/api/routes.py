from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import TicketRequest, TicketResponse
from app.services.classification import classify_ticket

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Return a simple service health response.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/sort-ticket", response_model=TicketResponse)
def sort_ticket(request: TicketRequest):
    """
    Accept one CRM ticket and return a structured classification.
    """
    response = classify_ticket(request)
    return response
