from typing import Protocol, runtime_checkable

@runtime_checkable
class AiHelper(Protocol):
    """Provides AI-related functionalities for the healthcare SDK"""
    def generateResponse(self, prompt: str) -> str:
        pass
