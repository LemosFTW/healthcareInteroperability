from abc import ABC, abstractmethod

class ValidatorTemplate(ABC):
    """Defines the default behavior for a validator"""
    def __init__(self):
        pass

    @abstractmethod
    def validate(self, type: str, data: dict) -> bool:
        pass