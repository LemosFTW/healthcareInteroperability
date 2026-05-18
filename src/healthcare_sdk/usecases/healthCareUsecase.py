from typing import Protocol, runtime_checkable

from ..contracts import MessageEnvelope, RawMessage

@runtime_checkable
class HealthCareUsecase(Protocol):
    """Defines the default behavior for a healthcare use case"""
    def execute(self, raw_message: RawMessage) -> MessageEnvelope:
        pass
