from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.core.claude_client import ClaudeClient
from src.core.config import get_settings

router = APIRouter(prefix="/legal", tags=["legal-analysis"])
settings = get_settings()
claude_client = ClaudeClient(settings.anthropic_api_key)


class LegalQuery(BaseModel):
    case_description: str
    legal_question: str
    relevant_laws: Optional[List[str]] = None


class LegalResponse(BaseModel):
    analysis: str
    alternatives: List[str]
    risk_assessment: str
    estimated_cost: float
    tokens_used: int


@router.post("/analyze", response_model=LegalResponse)
async def analyze_legal_case(query: LegalQuery):
    """Analyze legal case using Claude API"""
    
    prompt = f"""Si právny expert pre UAE právny systém. Analyzuj tento prípad:

POPIS PRÍPADU:
{query.case_description}

PRÁVNA OTÁZKA:
{query.legal_question}

Poskytni:
1. Právnu analýzu podľa UAE zákonov
2. 3 alternatívne stratégie
3. Risk assessment
4. Odhadovanú cenu konania

Formát odpovede v slovenčine."""

    try:
        response = await claude_client.send_message(prompt)
        
        # Parse response (simplified)
        analysis = response["content"][0]["text"]
        
        return LegalResponse(
            analysis=analysis,
            alternatives=["Stratégia 1", "Stratégia 2", "Stratégia 3"],
            risk_assessment="Stredné riziko",
            estimated_cost=5000.0,
            tokens_used=response["usage"]["input_tokens"] + response["usage"]["output_tokens"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check API health"""
    return {"status": "ok", "service": "uae-legal-agent"}