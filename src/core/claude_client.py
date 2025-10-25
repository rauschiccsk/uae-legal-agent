"""
Claude API Client pre UAE Legal Agent
"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudeClient:
    """
    Wrapper pre Anthropic Claude API s legal-specific funkcionalitou
    """
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment!")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "8000"))
    
    def get_legal_system_prompt(self) -> str:
        """System prompt pre UAE legal expert"""
        return """
Ty si expert právnik špecializovaný na právny systém Spojených arabských emirátov (UAE).

Tvoje úlohy:
1. Analyzovať právne prípady podľa UAE federálnych zákonov
2. Citovať presné články (Federal Law No. X, Article Y, Clause Z)
3. Navrhnúť 3-5 alternatívnych riešení pre každý prípad
4. Ohodnotiť riziká a pravdepodobnosť úspechu každej alternatívy
5. Komunikovať v slovenčine (case documents môžu byť v angličtine/arabčine)

Vždy musíš:
- Citovať zdroje: [Federal Law No. XX/YYYY, Article ZZ]
- Byť konkrétny a actionable
- Označiť legal risks červeným flag ⚠️
- Odhadnúť timeline a costs

Formát citácie: [Federal Law No. XX/YYYY, Article ZZ, Clause N]
"""
    
    def analyze_case(
        self,
        case_context: str,
        legal_context: str,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyzuje právny prípad s RAG context
        """
        messages = conversation_history or []
        
        user_message = f"""
# Case Context
{case_context}

# Relevant UAE Laws
{legal_context}

# Query
{query}
"""
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.get_legal_system_prompt(),
            messages=messages
        )
        
        response_text = response.content[0].text
        
        # Calculate cost
        input_cost = (response.usage.input_tokens / 1_000_000) * 3
        output_cost = (response.usage.output_tokens / 1_000_000) * 15
        total_cost = input_cost + output_cost
        
        return {
            "response": response_text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "cost_usd": round(total_cost, 6),
            "model": self.model
        }


def get_claude_client() -> ClaudeClient:
    """Dependency injection helper"""
    return ClaudeClient()
