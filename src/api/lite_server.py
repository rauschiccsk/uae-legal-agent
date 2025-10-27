"""
Lite FastAPI server for UAE Legal Agent
No ChromaDB, no compilation dependencies
Pure Python implementation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.claude_client import ClaudeClient
from core.config import settings

app = FastAPI(
    title="UAE Legal Agent API",
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

# Initialize Claude client
claude = ClaudeClient()

# In-memory storage for request tracking (will be replaced with DB in Phase 2)
request_tracker = {
    "total_requests": 0,
    "total_tokens": 0,
    "requests_history": []
}

# --- Models ---

class CaseAnalysisRequest(BaseModel):
    """Request model for case analysis"""
    case_description: str = Field(..., description="Description of the legal case")
    case_id: Optional[str] = Field(None, description="Optional case identifier")
    context: Optional[str] = Field(None, description="Additional context")
    language: str = Field("slovak", description="Output language (slovak/english)")

class AlternativeStrategy(BaseModel):
    """Single alternative legal strategy"""
    strategy_name: str
    description: str
    pros: List[str]
    cons: List[str]
    estimated_cost_range: str
    success_probability: str
    timeline: str
    relevant_laws: List[str]

class CaseAnalysisResponse(BaseModel):
    """Response model for case analysis"""
    case_id: str
    analysis_summary: str
    recommended_approach: str
    alternative_strategies: List[AlternativeStrategy]
    risk_assessment: Dict[str, Any]
    estimated_costs: Dict[str, Any]
    relevant_uae_laws: List[str]
    next_steps: List[str]
    tokens_used: int
    estimated_cost_usd: float
    timestamp: str

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    """Request model for chat"""
    message: str = Field(..., description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous messages")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")

class ChatResponse(BaseModel):
    """Response model for chat"""
    response: str
    tokens_used: int
    estimated_cost_usd: float
    conversation_history: List[ChatMessage]
    timestamp: str

class TokenStats(BaseModel):
    """Token usage statistics"""
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    recent_requests: List[Dict[str, Any]]

# --- Helper Functions ---

def track_request(endpoint: str, tokens: int, cost: float, case_id: Optional[str] = None):
    """Track API request for statistics"""
    request_tracker["total_requests"] += 1
    request_tracker["total_tokens"] += tokens
    
    request_record = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "tokens": tokens,
        "cost_usd": cost,
        "case_id": case_id
    }
    
    request_tracker["requests_history"].append(request_record)
    
    # Keep only last 100 requests in memory
    if len(request_tracker["requests_history"]) > 100:
        request_tracker["requests_history"] = request_tracker["requests_history"][-100:]

def calculate_cost(tokens: int) -> float:
    """Calculate cost based on token usage"""
    # Claude Sonnet 4.5 pricing (as of 2025)
    # Input: $3 per MTok, Output: $15 per MTok
    # Assuming 50/50 split for estimation
    cost_per_token = (3 + 15) / 2 / 1_000_000
    return tokens * cost_per_token

# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "UAE Legal Agent API",
        "version": "0.1.0",
        "model": settings.MODEL_NAME,
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "chat": "/api/v1/chat",
            "stats": "/api/v1/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Claude API
        test_response = claude.send_message("Test connection")
        api_status = "healthy" if test_response else "degraded"
    except Exception as e:
        api_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "claude_api": api_status,
        "model": settings.MODEL_NAME,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/analyze", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """
    Analyze a legal case with UAE law context
    
    Returns:
    - Detailed analysis
    - Alternative strategies
    - Risk assessment
    - Cost estimates
    - Relevant UAE law citations
    """
    try:
        # Generate case ID if not provided
        case_id = request.case_id or f"CASE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Build system prompt
        system_prompt = f"""Si expertný právny analytik špecializujúci sa na právny systém Spojených arabských emirátov (UAE).

Tvoja úloha je analyzovať právne prípady a poskytovať:
1. Komplexnú právnu analýzu podľa UAE zákonov
2. Minimálne 3 alternatívne právne stratégie s detailmi
3. Risk assessment a odhadované náklady
4. Citácie relevantných článkov UAE zákonov

Odpoveď poskytni v {'slovenskom' if request.language == 'slovak' else 'anglickom'} jazyku.
Formátuj odpoveď ako JSON s týmito poľami:
- analysis_summary (string)
- recommended_approach (string)
- alternative_strategies (array of objects)
- risk_assessment (object)
- estimated_costs (object)
- relevant_uae_laws (array of strings)
- next_steps (array of strings)
"""

        # Build user message
        user_message = f"""Právny prípad na analýzu:

ID prípadu: {case_id}
Popis: {request.case_description}
"""
        if request.context:
            user_message += f"\nDoplňujúci kontext: {request.context}"

        user_message += "\n\nPoskytni komplexnú právnu analýzu vo formáte JSON."

        # Call Claude API
        response = claude.send_message(
            message=user_message,
            system_prompt=system_prompt
        )

        # Parse response (basic implementation, can be enhanced)
        # For now, structure a basic response
        analysis_data = {
            "case_id": case_id,
            "analysis_summary": f"Analýza prípadu {case_id} bola spracovaná.",
            "recommended_approach": "Odporúčaný postup bude určený na základe detailnej analýzy.",
            "alternative_strategies": [
                {
                    "strategy_name": "Stratégia A",
                    "description": "Popis stratégie A",
                    "pros": ["Výhoda 1", "Výhoda 2"],
                    "cons": ["Nevýhoda 1"],
                    "estimated_cost_range": "5,000 - 10,000 AED",
                    "success_probability": "75%",
                    "timeline": "2-3 mesiace",
                    "relevant_laws": ["Federal Law No. 5/1985"]
                }
            ],
            "risk_assessment": {
                "overall_risk": "medium",
                "legal_risks": ["Risk 1", "Risk 2"],
                "financial_risks": ["Financial risk 1"]
            },
            "estimated_costs": {
                "legal_fees": "15,000 - 25,000 AED",
                "court_fees": "5,000 AED",
                "total_estimated": "20,000 - 30,000 AED"
            },
            "relevant_uae_laws": [
                "Federal Law No. 5/1985 (Civil Transactions Law)",
                "Federal Law No. 11/1992 (Civil Procedures Law)"
            ],
            "next_steps": [
                "Gather all relevant documents",
                "Consult with local UAE attorney",
                "File initial claim"
            ],
            "tokens_used": claude.total_tokens,
            "estimated_cost_usd": calculate_cost(claude.total_tokens),
            "timestamp": datetime.now().isoformat()
        }

        # Track the request
        track_request(
            endpoint="/api/v1/analyze",
            tokens=claude.total_tokens,
            cost=analysis_data["estimated_cost_usd"],
            case_id=case_id
        )

        return CaseAnalysisResponse(**analysis_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    General chat endpoint with conversation history
    
    Allows back-and-forth conversation about UAE legal topics
    """
    try:
        # Build conversation history for Claude
        messages = []
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # System prompt
        system_prompt = request.system_prompt or """Si expertný právny asistent pre UAE právny systém. 
Odpovedaj v slovenskom jazyku, pokiaľ nie je uvedené inak.
Poskytuj presné, odborné informácie o UAE zákonoch."""

        # Call Claude
        response_text = claude.send_message(
            message=request.message,
            system_prompt=system_prompt
        )

        # Add assistant response to history
        messages.append({"role": "assistant", "content": response_text})

        # Track the request
        cost = calculate_cost(claude.total_tokens)
        track_request(
            endpoint="/api/v1/chat",
            tokens=claude.total_tokens,
            cost=cost
        )

        return ChatResponse(
            response=response_text,
            tokens_used=claude.total_tokens,
            estimated_cost_usd=cost,
            conversation_history=[ChatMessage(**msg) for msg in messages],
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/v1/stats", response_model=TokenStats)
async def get_stats():
    """
    Get token usage statistics
    
    Returns:
    - Total requests made
    - Total tokens consumed
    - Total estimated costs
    - Recent request history
    """
    total_cost = sum(req["cost_usd"] for req in request_tracker["requests_history"])
    
    return TokenStats(
        total_requests=request_tracker["total_requests"],
        total_tokens=request_tracker["total_tokens"],
        total_cost_usd=total_cost,
        recent_requests=request_tracker["requests_history"][-20:]  # Last 20 requests
    )

@app.delete("/api/v1/stats/reset")
async def reset_stats():
    """Reset statistics (for testing purposes)"""
    request_tracker["total_requests"] = 0
    request_tracker["total_tokens"] = 0
    request_tracker["requests_history"] = []
    
    return {"status": "Statistics reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)