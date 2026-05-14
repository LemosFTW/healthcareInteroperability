from abc import ABC, abstractmethod
from typing import Protocol

class Normalizer(Protocol):
    """Defines the default behavior for a normalizer"""
    def normalizeData(self, type: str, data: dict) -> dict:
        pass

class NormalizerTemplate(ABC, Normalizer):
    """Defines the default behavior for a normalizer"""
    def __init__(self):
        self.aiHelper = None
        pass

    @abstractmethod
    def normalizeData(self, type: str, data: dict) -> dict:
        pass