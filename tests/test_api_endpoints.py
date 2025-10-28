"""
API endpoint tests for UAE Legal Agent
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_case_endpoint():
    """Test case analysis endpoint"""
    case_data = {
        "case_title": "Test Case",
        "case_description": "A simple test case for API validation",
        "relevant_laws": ["Federal Law No. 5 of 1985"],
        "client_goals": ["Test goal"]
    }
    
    response = client.post("/api/v1/analyze", json=case_data)
    assert response.status_code == 200
    assert "analysis" in response.json()


def test_invalid_case_data():
    """Test validation with invalid data"""
    invalid_data = {
        "case_title": "",
        "case_description": "Missing title"
    }
    
    response = client.post("/api/v1/analyze", json=invalid_data)
    assert response.status_code == 422