from typing import Any, Dict, Protocol

from ..contracts import MessageEnvelope

class HealthCareStorage(Protocol):
    """Defines the default behavior for a storage repository"""
    def save(self, envelope: MessageEnvelope) -> str:
        pass
    def connection(self) -> Any:
        pass
    def read(self, query: Dict[str, Any]) -> Dict[str, Any]:
        pass
    def delete(self, query: Dict[str, Any]) -> bool:
        pass
    def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
        pass
