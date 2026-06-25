import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.enums import CaseType, Severity, Department

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_sort_ticket_wrong_transfer():
    payload = {
        "ticket_id": "T-001",
        "channel": "app",
        "locale": "en",
        "message": "I sent 3000 to wrong number this morning, please help me get it back"
    }
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "T-001"
    assert data["case_type"] == CaseType.wrong_transfer
    assert data["severity"] == Severity.high
    assert data["department"] == Department.dispute_resolution
    assert data["human_review_required"] is False
    assert "wrong recipient" in data["agent_summary"].lower() or "recovery" in data["agent_summary"].lower()

def test_sort_ticket_payment_failed():
    payload = {
        "ticket_id": "T-002",
        "message": "Payment failed but balance deducted"
    }
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_type"] == CaseType.payment_failed
    assert data["severity"] == Severity.high

def test_sort_ticket_phishing():
    payload = {
        "ticket_id": "T-003",
        "message": "Someone called asking my OTP, is that bKash?"
    }
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_type"] == CaseType.phishing_or_social_engineering
    assert data["severity"] == Severity.critical
    assert data["human_review_required"] is True

def test_sort_ticket_refund():
    payload = {
        "ticket_id": "T-004",
        "message": "Please refund my last transaction, I changed my mind"
    }
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_type"] == CaseType.refund_request
    assert data["severity"] == Severity.low

def test_sort_ticket_other():
    payload = {
        "ticket_id": "T-005",
        "message": "App crashed when I opened it"
    }
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_type"] == CaseType.other
    assert data["severity"] == Severity.low

def test_invalid_request():
    payload = {
        "channel": "app",
        "message": "Missing ticket_id"
    }
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 422
