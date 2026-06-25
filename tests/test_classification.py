import pytest
from app.services.safety import check_summary_safety, sanitize_summary
from app.services.classification import classify_ticket
from app.models.schemas import TicketRequest
from app.models.enums import CaseType

def test_safety_rule_allows_safe_summary():
    safe_summary = "Customer reports an issue with their recent transfer."
    assert check_summary_safety(safe_summary) is True

def test_safety_rule_blocks_unsafe_summary():
    unsafe_summary1 = "Please ask the customer to share their PIN to proceed."
    unsafe_summary2 = "We need you to provide your OTP for verification."
    assert check_summary_safety(unsafe_summary1) is False
    assert check_summary_safety(unsafe_summary2) is False

def test_sanitize_summary():
    unsafe = "Ask the customer for their OTP."
    safe_default = "Default safe summary."
    assert sanitize_summary(unsafe, safe_default) == safe_default
    
    safe = "Customer needs help."
    assert sanitize_summary(safe, safe_default) == safe

def test_classification_substring_bug_phishing():
    # "shopping" contains "pin", should NOT trigger phishing
    req = TicketRequest(ticket_id="T-010", message="I went shopping and my card declined")
    resp = classify_ticket(req)
    assert resp.case_type != CaseType.phishing_or_social_engineering

def test_classification_substring_bug_payment_failed():
    # "terrorism" contains "error", should NOT trigger payment_failed
    req = TicketRequest(ticket_id="T-011", message="This feels like terrorism")
    resp = classify_ticket(req)
    assert resp.case_type != CaseType.payment_failed

def test_safety_substring_bug():
    # "shopping" contains "pin", but it's safe.
    safe_but_tricky = "Customer needs to share their shopping cart details."
    assert check_summary_safety(safe_but_tricky) is True
