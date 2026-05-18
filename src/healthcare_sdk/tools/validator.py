from abc import ABC, abstractmethod
from typing import Protocol

from ..contracts import DecodedPayload, ValidationResult

class Validator(Protocol):
    """Defines the default behavior for a validator"""
    def validate(self, decoded_payload: DecodedPayload) -> ValidationResult:
        pass


class ValidatorTemplate(ABC, Validator):
    """Defines the default behavior for a validator"""
    def __init__(self):
        pass

    @abstractmethod
    def validate(self, decoded_payload: DecodedPayload) -> ValidationResult:
        pass