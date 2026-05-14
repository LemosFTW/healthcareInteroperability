from typing import Protocol

class HealthCareUsecase(Protocol):
    """Defines the default behavior for a healthcare use case"""
    def execute(self):
        pass