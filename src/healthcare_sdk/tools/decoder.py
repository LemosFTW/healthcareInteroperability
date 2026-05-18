from typing import Protocol

from ..contracts import RawMessage, DecodedPayload


class Decoder(Protocol):
    """Defines the default behavior for a decoder"""
    def decode(self, raw_message: RawMessage) -> DecodedPayload:
        pass
