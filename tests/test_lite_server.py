"""
Test suite for Lite Server
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.lite_server import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "UAE Legal Agent" in response.json()["service"]


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "api_connected" in data


def test_analyze_case():
    """Test case analysis endpoint"""
    request_data = {
        "case_description": "Client wants to terminate employment contract 6 months before end date. Contract is for 2 years, started Jan 2024.",
        "relevant_laws": ["UAE Labor Law Federal Decree No. 33 of 2021"],
        "client_goal": "Minimize penalties"
    }
    
    response = client.post("/api/v1/analyze", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis" in data
    assert "strategies" in data
    assert "tokens_used" in data
    assert data["tokens_used"] > 0


def test_stats():
    """Test stats endpoint"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    assert "model" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])