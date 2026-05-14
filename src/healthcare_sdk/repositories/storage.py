from typing import Protocol

class HealthCareStorage(Protocol):
    """Defines the default behavior for a storage repository"""
    def save(self, type: str, data: dict) -> bool:
        pass
    def connection(self) -> any:
        pass
    def read(self, type: str, query: dict) -> dict:
        pass
    def delete(self, type: str, query: dict) -> bool:
        pass
    def update(self, type: str, query: dict, data: dict) -> bool:
        pass