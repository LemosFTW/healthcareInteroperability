from typing import Protocol
from ..contracts import RawMessage

class Adapter(Protocol):
    """Defines the default behavior for a transport layer adapter"""
    def executeServer(self, port: int = 8000):
        pass

    def receive(self) -> RawMessage:
        pass
