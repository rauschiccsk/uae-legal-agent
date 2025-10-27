"""
UAE Legal Agent - Lite Server
Pure Python ASGI server without compilation dependencies
"""

import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.claude_client import ClaudeClient
from src.core.config import get_settings

# Initialize
app = FastAPI(
    title="UAE Legal Agent",
    description="AI-powered legal analysis for UAE law",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client
settings = get_settings()
claude = ClaudeClient()


# Models
class CaseAnalysisRequest(BaseModel):
    case_description: str
    relevant_laws: Optional[list[str]] = None
    client_goal: Optional[str] = None


class CaseAnalysisResponse(BaseModel):
    analysis: str
    strategies: list[str]
    risks: list[str]
    estimated_cost: str
    tokens_used: int
    model: str


class HealthResponse(BaseModel):
    status: str
    api_connected: bool
    model: str


# Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "UAE Legal Agent",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test API connection
        test_response = await asyncio.to_thread(
            claude.send_message,
            "Hello"
        )
        api_connected = bool(test_response)
    except Exception:
        api_connected = False
    
    return HealthResponse(
        status="healthy" if api_connected else "degraded",
        api_connected=api_connected,
        model=settings.MODEL_NAME
    )


@app.post("/api/v1/analyze", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """
    Analyze legal case with UAE law context
    
    Example request:
    {
        "case_description": "Client wants to terminate employment contract early...",
        "relevant_laws": ["UAE Labor Law Federal Decree No. 33 of 2021"],
        "client_goal": "Minimize penalties and maintain good standing"
    }
    """
    try:
        # Build context-aware prompt
        prompt = f"""Analyzuj tento právny prípad podľa UAE zákonov:

POPIS PRÍPADU:
{request.case_description}

RELEVANTNÉ ZÁKONY:
{chr(10).join(request.relevant_laws) if request.relevant_laws else 'Všeobecné UAE zákony'}

CIEĽ KLIENTA:
{request.client_goal or 'Optimálne riešenie'}

POŽADOVANÉ VÝSTUPY:
1. Právna analýza situácie
2. 3-5 alternatívnych stratégií
3. Risk assessment pre každú stratégiu
4. Odhadované náklady
5. Citácie relevantných článkov zákonov

Odpovedaj v SLOVENSKOM jazyku, štruktúrovane a profesionálne."""

        # Call Claude
        response = await asyncio.to_thread(
            claude.send_message,
            prompt
        )
        
        # Parse response (basic parsing - enhance in Phase 2)
        analysis_text = response["content"][0]["text"]
        
        # Extract sections (simple heuristic)
        strategies = _extract_strategies(analysis_text)
        risks = _extract_risks(analysis_text)
        cost = _extract_cost(analysis_text)
        
        return CaseAnalysisResponse(
            analysis=analysis_text,
            strategies=strategies,
            risks=risks,
            estimated_cost=cost,
            tokens_used=response["usage"]["total_tokens"],
            model=response["model"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_stats():
    """Get API usage statistics"""
    return {
        "total_requests": 0,  # TODO: Implement tracking
        "total_tokens": 0,
        "estimated_cost": 0.0,
        "model": settings.MODEL_NAME
    }


# Helper functions
def _extract_strategies(text: str) -> list[str]:
    """Extract strategies from analysis text"""
    # Simple heuristic - look for numbered lists
    strategies = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(line.startswith(f"{i}.") for i in range(1, 10)):
            strategies.append(line)
    return strategies[:5] if strategies else ["Stratégia nebola extrahovaná"]


def _extract_risks(text: str) -> list[str]:
    """Extract risks from analysis text"""
    risks = []
    lines = text.split('\n')
    in_risk_section = False
    for line in lines:
        line_lower = line.lower()
        if 'risk' in line_lower or 'rizik' in line_lower:
            in_risk_section = True
        if in_risk_section and any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
            risks.append(line.strip())
    return risks[:5] if risks else ["Risk assessment pending"]


def _extract_cost(text: str) -> str:
    """Extract cost estimate from analysis text"""
    # Look for AED mentions
    import re
    aed_pattern = r'AED\s*[\d,]+'
    matches = re.findall(aed_pattern, text)
    return matches[0] if matches else "Cost estimate pending"


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting UAE Legal Agent Lite Server...")
    print("📝 API Docs: http://localhost:8002/docs")
    uvicorn.run(app, host="0.0.0.0", port=8002)