from typing import Protocol, runtime_checkable

from ..contracts import RawMessage, DecodedPayload


@runtime_checkable
class Decoder(Protocol):
    """Defines the default behavior for a decoder"""
    def decode(self, raw_message: RawMessage) -> DecodedPayload:
        pass
