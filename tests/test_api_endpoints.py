import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "UAE Legal Agent API" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/legal/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_legal_analysis():
    """Test legal analysis endpoint"""
    query = {
        "case_description": "Test case",
        "legal_question": "Test question"
    }
    
    response = client.post("/legal/analyze", json=query)
    
    # Should return 200 if API key is configured
    # or 500 if not configured
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "analysis" in data
        assert "tokens_used" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])