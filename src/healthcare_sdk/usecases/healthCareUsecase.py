from typing import Protocol

from ..contracts import MessageEnvelope, RawMessage

class HealthCareUsecase(Protocol):
    """Defines the default behavior for a healthcare use case"""
    def execute(self, raw_message: RawMessage) -> MessageEnvelope:
        pass
