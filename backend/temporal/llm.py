from typing import Protocol

from backend.temporal.models import ReasoningContext, TemporalAnalysis
from backend.temporal.prompts.builder import TemporalPromptBuilder
from backend.temporal.prompts.parser import TemporalResponseParser
from backend.temporal.exceptions import TemporalReasoningError
from backend.services.llm_service import call_openrouter

class LLMProvider(Protocol):
    async def generate(self, prompt: str, model_name: str) -> str | None:
        """Generates a response from the LLM given a prompt and a model name."""
        ...

class OpenRouterLLMProvider:
    """Concrete implementation of LLMProvider using the existing OpenRouter service."""
    async def generate(self, prompt: str, model_name: str) -> str | None:
        return await call_openrouter(
            prompt=prompt,
            model=model_name,
            call_type="temporal_reasoning"
        )

class TemporalLLM:
    """
    Orchestrates the prompt-building, LLM-calling, and JSON-parsing steps
    for temporal reasoning.
    """
    def __init__(self, llm_provider: LLMProvider):
        self._provider = llm_provider
        self._builder = TemporalPromptBuilder()
        self._parser = TemporalResponseParser()
        
    async def analyze(self, context: ReasoningContext) -> TemporalAnalysis:
        prompt = self._builder.build(context.comparison)
        
        response_text = await self._provider.generate(prompt, context.model_name)
        if not response_text:
            raise TemporalReasoningError("LLM provider failed to return a response (timeout or exhaustion).")
            
        analysis = self._parser.parse(response_text, context.comparison.company_name)
        return analysis
