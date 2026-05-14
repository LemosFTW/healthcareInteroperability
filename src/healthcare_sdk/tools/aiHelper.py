from typing import Protocol

class AiHelper(Protocol):
    """Provides AI-related functionalities for the healthcare SDK"""
    def generateResponse(self, prompt: str) -> str:
        pass