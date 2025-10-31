"""Claude API client with RAG integration."""

import os
from typing import List, Optional, Dict
from anthropic import Anthropic

# Try to import config, fallback to env vars
try:
    from config import settings

    USE_CONFIG = True
except ImportError:
    USE_CONFIG = False


class ClaudeClient:
    """Client pre prácu s Claude API s RAG integráciou."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializácia Claude klienta.

        Args:
            api_key: Claude API kľúč (ak nie je zadaný, použije sa z config alebo ENV)
            model: Model name (default: claude-sonnet-4-5-20250929)
        """
        # Get API key from config or env
        if api_key:
            self.api_key = api_key
        elif USE_CONFIG:
            self.api_key = settings.CLAUDE_API_KEY
        else:
            self.api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY nie je nastavený (skontroluj .env súbor)")

        self.client = Anthropic(api_key=self.api_key)

        # Get model from config or use default
        if model:
            self.model = model
        elif USE_CONFIG and hasattr(settings, 'CLAUDE_MODEL'):
            self.model = settings.CLAUDE_MODEL
        else:
            self.model = "claude-sonnet-4-5-20250929"

    def generate_response(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            max_tokens: int = 4096,
            temperature: float = 0.7
    ) -> Dict:
        """
        Generate response from Claude (generic method).

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            Dict with 'content' and 'usage' keys
        """
        try:
            # Build message
            message_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            # Add system prompt if provided
            if system_prompt:
                message_params["system"] = system_prompt

            # Call API
            message = self.client.messages.create(**message_params)

            return {
                "content": message.content[0].text,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }

        except Exception as e:
            raise Exception(f"Chyba pri volaní Claude API: {str(e)}")

    def analyze_legal_document(self, text: str, context: List[str]) -> str:
        """
        Analyzuje právny dokument s RAG kontextom.

        Args:
            text: Text dokumentu na analýzu
            context: RAG kontext - relevantné časti z databázy

        Returns:
            Analýza dokumentu v slovenčine
        """
        prompt = self._build_prompt(
            task="Analyzuj tento právny dokument a poskytni detailnú právnu analýzu.",
            text=text,
            context=context,
            instructions=[
                "Identifikuj kľúčové právne body",
                "Upozorni na potenciálne problémy alebo riziká",
                "Porovnaj s podobnými prípadmi z kontextu",
                "Odpovedaj výhradne v slovenčine"
            ]
        )

        return self._call_api(prompt)

    def ask_question(self, question: str, context: List[str]) -> str:
        """
        Odpovedá na otázku s RAG kontextom.

        Args:
            question: Otázka používateľa
            context: RAG kontext - relevantné informácie

        Returns:
            Odpoveď v slovenčine
        """
        prompt = self._build_prompt(
            task=f"Odpovedz na túto otázku: {question}",
            text="",
            context=context,
            instructions=[
                "Použi informácie z poskytnutého kontextu",
                "Buď presný a výstižný",
                "Ak kontext neobsahuje odpoveď, povedz to",
                "Odpovedaj výhradne v slovenčine"
            ]
        )

        return self._call_api(prompt)

    def summarize_document(self, text: str) -> str:
        """
        Vytvorí zhrnutie dokumentu.

        Args:
            text: Text dokumentu na zhrnutie

        Returns:
            Zhrnutie v slovenčine
        """
        prompt = self._build_prompt(
            task="Vytvor stručné a jasné zhrnutie tohto dokumentu.",
            text=text,
            context=[],
            instructions=[
                "Zachyť hlavné body a kľúčové informácie",
                "Udržuj zhrnutie jasné a zrozumiteľné",
                "Odpovedaj výhradne v slovenčine"
            ]
        )

        return self._call_api(prompt)

    def translate_to_slovak(self, text: str) -> str:
        """
        Prekladá text z arabčiny do slovenčiny.

        Args:
            text: Arabský text na preklad

        Returns:
            Preložený text v slovenčine
        """
        prompt = self._build_prompt(
            task="Prelož tento arabský text do slovenčiny.",
            text=text,
            context=[],
            instructions=[
                "Zachovaj význam a kontext originálu",
                "Použi prirodzený slovenský jazyk",
                "Pri právnych termínoch použi správnu právnu terminológiu"
            ]
        )

        return self._call_api(prompt)

    def _build_prompt(
            self,
            task: str,
            text: str,
            context: List[str],
            instructions: List[str]
    ) -> str:
        """
        Konštruuje prompt pre Claude API.

        Args:
            task: Hlavná úloha
            text: Vstupný text
            context: RAG kontext
            instructions: Špeciálne inštrukcie

        Returns:
            Skonštruovaný prompt
        """
        prompt_parts = [task, ""]

        if context:
            prompt_parts.append("RELEVANTNÝ KONTEXT:")
            for i, ctx in enumerate(context, 1):
                prompt_parts.append(f"\n[Kontext {i}]")
                prompt_parts.append(ctx)
            prompt_parts.append("")

        if text:
            prompt_parts.append("DOKUMENT:")
            prompt_parts.append(text)
            prompt_parts.append("")

        if instructions:
            prompt_parts.append("INŠTRUKCIE:")
            for instruction in instructions:
                prompt_parts.append(f"- {instruction}")

        return "\n".join(prompt_parts)

    def _call_api(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        Volá Claude API.

        Args:
            prompt: Prompt pre Claude
            max_tokens: Maximálny počet tokenov v odpovedi

        Returns:
            Odpoveď od Claude
        """
        result = self.generate_response(prompt, max_tokens=max_tokens)
        return result['content']