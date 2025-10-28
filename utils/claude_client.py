import os
from typing import List, Optional
from anthropic import Anthropic


class ClaudeClient:
    """Client pre prácu s Claude API s RAG integráciou."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializácia Claude klienta.
        
        Args:
            api_key: Anthropic API kľúč (ak nie je zadaný, použije sa ANTHROPIC_API_KEY z ENV)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY nie je nastavený")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
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
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            raise Exception(f"Chyba pri volaní Claude API: {str(e)}")