import re
import json
import logging
from app.models.schemas import TicketRequest, TicketResponse
from app.models.enums import CaseType, Severity, Department
from app.utils.constants import PHISHING_KEYWORDS, WRONG_TRANSFER_KEYWORDS, PAYMENT_FAILED_KEYWORDS, REFUND_KEYWORDS
from app.services.summarization import generate_summary
from app.services.safety import sanitize_summary
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try importing generativeai, gracefully handle if not installed
try:
    import google.generativeai as genai
    genai_available = True
except ImportError:
    genai_available = False

if genai_available and settings.llm_enabled and settings.llm_api_key:
    genai.configure(api_key=settings.llm_api_key)

def llm_classify_ticket(request: TicketRequest) -> TicketResponse:
    """Attempts to classify the ticket using Gemini LLM."""
    prompt = f"""
    You are an expert customer support routing AI for a digital finance company.
    Read the following customer message and classify it into these exact categories.
    Return ONLY a valid JSON object matching the requested schema. Do not return markdown blocks or any other text.
    
    Ticket ID: {request.ticket_id}
    Message: "{request.message}"
    
    Categories:
    - case_type: "wrong_transfer", "payment_failed", "refund_request", "phishing_or_social_engineering", "other"
    - severity: "low", "medium", "high", "critical"
    - department: "customer_support", "dispute_resolution", "payments_ops", "fraud_risk"
    
    Rules:
    - Phishing or asking for OTP/PIN is phishing_or_social_engineering (critical, fraud_risk).
    - Wrong transfer is high severity, dispute_resolution.
    - Payment failed is high severity, payments_ops.
    - Refund request is low severity, customer_support.
    
    Return JSON format exactly like:
    {{
        "case_type": "...",
        "severity": "...",
        "department": "...",
        "agent_summary": "1-2 neutral sentences describing the issue.",
        "confidence": 0.95
    }}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    # Parse JSON
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:-3].strip()
    elif text.startswith("```"):
        text = text[3:-3].strip()
        
    data = json.loads(text)
    
    # Enforce strict parsing
    case_type = CaseType(data["case_type"])
    severity = Severity(data["severity"])
    department = Department(data["department"])
    confidence = float(data.get("confidence", 0.90))
    agent_summary = data.get("agent_summary", generate_summary(request.message, case_type))
    
    # Enforce safety
    agent_summary = sanitize_summary(agent_summary, "Customer reported an issue requiring agent attention.")
    
    # Enforce human review logic
    human_review_required = (severity == Severity.critical) or (case_type == CaseType.phishing_or_social_engineering)
    
    return TicketResponse(
        ticket_id=request.ticket_id,
        case_type=case_type,
        severity=severity,
        department=department,
        agent_summary=agent_summary,
        human_review_required=human_review_required,
        confidence=confidence
    )


def rule_based_classify_ticket(request: TicketRequest) -> TicketResponse:
    """The robust rule-based fallback classification."""
    message_lower = request.message.lower()
    
    case_type = CaseType.other
    confidence = 0.5
    
    def has_any(words, text):
        return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)
    
    if has_any(PHISHING_KEYWORDS, message_lower):
        case_type = CaseType.phishing_or_social_engineering
        confidence = 0.95
    elif has_any(WRONG_TRANSFER_KEYWORDS, message_lower):
        case_type = CaseType.wrong_transfer
        confidence = 0.90
    elif has_any(PAYMENT_FAILED_KEYWORDS, message_lower):
        case_type = CaseType.payment_failed
        confidence = 0.90
    elif has_any(REFUND_KEYWORDS, message_lower):
        case_type = CaseType.refund_request
        confidence = 0.85
        
    severity = Severity.low
    department = Department.customer_support
    
    if case_type == CaseType.phishing_or_social_engineering:
        severity = Severity.critical
        department = Department.fraud_risk
    elif case_type == CaseType.wrong_transfer:
        severity = Severity.high
        department = Department.dispute_resolution
    elif case_type == CaseType.payment_failed:
        severity = Severity.high
        department = Department.payments_ops
    elif case_type == CaseType.refund_request:
        severity = Severity.low
        department = Department.customer_support
    else:
        severity = Severity.low
        department = Department.customer_support
        
    human_review_required = (severity == Severity.critical) or (case_type == CaseType.phishing_or_social_engineering)
        
    if case_type == CaseType.other and ("urgent" in message_lower or "crash" in message_lower):
        confidence = 0.60
        
    agent_summary = generate_summary(request.message, case_type)
    
    return TicketResponse(
        ticket_id=request.ticket_id,
        case_type=case_type,
        severity=severity,
        department=department,
        agent_summary=agent_summary,
        human_review_required=human_review_required,
        confidence=confidence
    )

def classify_ticket(request: TicketRequest) -> TicketResponse:
    if genai_available and settings.llm_enabled and settings.llm_api_key:
        try:
            return llm_classify_ticket(request)
        except Exception as e:
            logger.error(f"LLM classification failed: {e}. Falling back to rules.")
            return rule_based_classify_ticket(request)
    else:
        return rule_based_classify_ticket(request)
