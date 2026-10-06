from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generates a simple text response."""
        pass

    @abstractmethod
    async def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]]) -> dict:
        """Generates a response and optionally decides to call a tool."""
        pass