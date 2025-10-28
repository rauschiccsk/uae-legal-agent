"""
Test FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_case():
    """Test case analysis endpoint"""
    payload = {
        "case_description": "Property dispute in Dubai - landlord claims unpaid rent",
        "case_type": "civil",
        "jurisdiction": "Dubai Courts"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "strategies" in data
    assert "tokens_used" in data