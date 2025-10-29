"""Claude API wrapper modul pre UAE legal analysis."""

import logging
import time
from typing import Dict, List, Optional, Any
from anthropic import Anthropic, APIError, RateLimitError, APIConnectionError
from utils.config import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """Claude API client pre UAE legal analysis."""
    
    def __init__(self, config: Settings):
        """
        Inicializuje Claude client.
        
        Args:
            config: Settings objekt s konfiguráciou
            
        Raises:
            ValueError: Ak chýba API key
        """
        if not hasattr(config, 'anthropic_api_key') or not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required in config")
        
        self.config = config
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 8000
        
        logger.info(f"ClaudeClient inicializovaný: model={self.model}, max_tokens={self.max_tokens}")
    
    def get_legal_system_prompt(self) -> str:
        """
        Vráti system prompt pre UAE legal expert.
        
        Returns:
            System prompt string
        """
        return """Si expert na právo Spojených Arabských Emirátov (UAE) s hlbokými znalosťami federálnych zákonov, emirátových predpisov a judikatúry.

TVOJA ÚLOHA:
- Analyzuj právne prípady v kontexte UAE legislatívy
- Poskytuj presné odpovede založené na aktuálnych zákonoch
- Cituj zdroje vo formáte: [Federal Law No. X/YYYY, Article Z]
- Vždy odpovedaj v slovenčine

ŠTRUKTÚRA ANALÝZY:
1. Zhrnutie situácie
2. Aplikovateľné zákony a články
3. Právna analýza
4. Odporúčania a riziká
5. Ďalšie kroky

PRAVIDLÁ:
- Používaj presné citácie zákonov
- Uvádzaj príklady z judikatúry ak sú relevantné
- Jasne rozlišuj fakty od právnej interpretácie
- Upozorni na riziká a alternatívy
- Slovenský jazyk vo všetkých odpovediach"""
    
    def analyze_legal_case(
        self,
        case_context: str,
        legal_context: str,
        query: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Analyzuje právny prípad pomocou Claude API.
        
        Args:
            case_context: Kontext prípadu
            legal_context: Relevantné UAE zákony a predpisy
            query: Otázka na analýzu
            history: Voliteľná história konverzácie
            
        Returns:
            Dict s response, token_usage, cost, model
        """
        logger.info("Spúšťam analýzu právneho prípadu")
        
        # Priprav správy
        messages = []
        
        # Pridaj históriu ak existuje
        if history:
            messages.extend(history)
        
        # Pridaj aktuálny dotaz
        user_message = f"""KONTEXT PRÍPADU:
{case_context}

RELEVANTNÉ UAE ZÁKONY:
{legal_context}

OTÁZKA:
{query}"""
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        system_prompt = self.get_legal_system_prompt()
        
        result = self._call_claude_api(
            messages=messages,
            system=system_prompt,
            max_tokens=self.max_tokens
        )
        
        logger.info(f"Analýza dokončená: tokens={result['token_usage']['total']}, cost=${result['cost']:.6f}")
        
        return result
    
    def generate_alternatives(
        self,
        case_summary: str,
        legal_context: str
    ) -> Dict[str, Any]:
        """
        Generuje alternatívne právne stratégie.
        
        Args:
            case_summary: Zhrnutie prípadu
            legal_context: Právny kontext
            
        Returns:
            Dict so strukturovanými alternatívami
        """
        logger.info("Generujem alternatívne stratégie")
        
        prompt = f"""Na základe nasledujúceho prípadu vygeneruj 3-5 alternatívnych právnych stratégií:

PRÍPAD:
{case_summary}

PRÁVNY KONTEXT:
{legal_context}

Pre každú alternatívu uveď:
1. Názov stratégie
2. Popis postupu
3. Hodnotenie rizika (Low/Medium/High)
4. Odhadovaný časový harmonogram
5. Nákladové implikácie
6. Výhody a nevýhody

Formátuj odpoveď jasne a štruktúrovane v slovenčine."""
        
        messages = [{"role": "user", "content": prompt}]
        system_prompt = self.get_legal_system_prompt()
        
        result = self._call_claude_api(
            messages=messages,
            system=system_prompt,
            max_tokens=self.max_tokens
        )
        
        logger.info(f"Alternatívy vygenerované: tokens={result['token_usage']['total']}")
        
        return result
    
    def _call_claude_api(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 8000
    ) -> Dict[str, Any]:
        """
        Interná funkcia pre volanie Claude API s retry mechanikou.
        
        Args:
            messages: Zoznam správ
            system: System prompt
            max_tokens: Maximálny počet tokenov
            
        Returns:
            Dict s response, token_usage, cost, model
            
        Raises:
            APIError: Po vyčerpaní retry pokusov
        """
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"API call attempt {attempt + 1}/{max_retries}")
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=messages
                )
                
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                total_tokens = input_tokens + output_tokens
                
                cost = self.calculate_cost(input_tokens, output_tokens)
                
                result = {
                    "response": response.content[0].text,
                    "token_usage": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": total_tokens
                    },
                    "cost": cost,
                    "model": self.model
                }
                
                logger.info(
                    f"API call successful: input={input_tokens}, output={output_tokens}, cost=${cost:.6f}"
                )
                
                return result
                
            except RateLimitError as e:
                logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries exceeded for rate limit")
                    raise
                    
            except APIConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries exceeded for connection error")
                    raise
                    
            except APIError as e:
                logger.error(f"API error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1 and e.status_code >= 500:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Server error, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error("Non-retryable API error or max retries exceeded")
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error: {type(e).__name__}: {e}")
                raise
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Vypočíta náklady pre Claude Sonnet 4.5.
        
        Pricing:
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        
        Args:
            input_tokens: Počet input tokenov
            output_tokens: Počet output tokenov
            
        Returns:
            Celková cena v USD
        """
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost
        
        return total_cost