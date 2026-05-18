from typing import Protocol, runtime_checkable
from ..contracts import RawMessage

@runtime_checkable
class Adapter(Protocol):
    """Defines the default behavior for a transport layer adapter"""
    def executeServer(self, port: int = 8000):
        pass

    def receive(self) -> RawMessage:
        pass
