from app.models.enums import CaseType
from app.services.safety import sanitize_summary

def generate_summary(message: str, case_type: CaseType) -> str:
    """
    Generates a one or two sentence neutral summary based on the message.
    """
    base_summary = ""
    if case_type == CaseType.phishing_or_social_engineering:
        base_summary = "Customer reports a potential phishing or social engineering attempt."
    elif case_type == CaseType.wrong_transfer:
        base_summary = "Customer reports sending money to the wrong recipient and requests recovery."
    elif case_type == CaseType.payment_failed:
        base_summary = "Customer reports a failed payment with balance deducted."
    elif case_type == CaseType.refund_request:
        base_summary = "Customer is requesting a refund for a transaction."
    else:
        # Extract a small snippet or generic message
        base_summary = "Customer has a general inquiry or issue."
        
    # We could theoretically use an LLM here if enabled via config,
    # but the rule-based safe summary is deterministic and robust.
    
    # Ensure it's safe
    safe_summary = sanitize_summary(base_summary, "Customer reported an issue that requires agent attention.")
    return safe_summary
