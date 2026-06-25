import re
from app.utils.constants import SENSITIVE_DATA_KEYWORDS

def check_summary_safety(summary: str) -> bool:
    """
    Returns True if the summary is safe, False if it violates the safety rule.
    Safety Rule: The agent_summary field must never ask the customer to share PIN, OTP, password, or full card number.
    """
    lower_summary = summary.lower()
    
    # Check if the summary contains words like "share", "provide", "give", "send" in proximity to sensitive keywords
    trigger_words = ["share", "provide", "give", "send", "need", "ask"]
    
    # Helper to search with word boundaries
    def has_any(words, text):
        return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)
        
    has_trigger = has_any(trigger_words, lower_summary)
    has_sensitive = has_any(SENSITIVE_DATA_KEYWORDS, lower_summary)
    
    if has_trigger and has_sensitive:
        return False
        
    # Also strictly block explicit "ask for PIN" type phrasing
    if "ask the customer" in lower_summary and has_sensitive:
        return False
        
    return True

def sanitize_summary(summary: str, default_safe_summary: str) -> str:
    """
    If the summary violates safety rules, fallback to a safe default.
    """
    if check_summary_safety(summary):
        return summary
    return default_safe_summary
