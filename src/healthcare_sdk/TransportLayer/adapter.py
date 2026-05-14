from typing import Protocol

class Adapter(Protocol):
    """Defines the default behavior for a transport layer adapter"""
    def executeServer(self, port: int = 8000):
        pass
