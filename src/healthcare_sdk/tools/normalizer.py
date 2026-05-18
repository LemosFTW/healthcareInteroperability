from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from .aiHelper import AiHelper
from ..contracts import DecodedPayload, NormalizedPayload

@runtime_checkable
class Normalizer(Protocol):
    """Defines the default behavior for a normalizer"""
    def normalizeData(self, decoded_payload: DecodedPayload) -> NormalizedPayload:
        pass

class NormalizerTemplate(ABC, Normalizer):
    """Defines the default behavior for a normalizer"""
    def __init__(self):
        self.aiHelper : AiHelper | None = None
        pass

    @abstractmethod
    def normalizeData(self, decoded_payload: DecodedPayload) -> NormalizedPayload:
        pass
