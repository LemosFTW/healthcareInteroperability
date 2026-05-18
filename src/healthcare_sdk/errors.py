from typing import Any, Dict, Optional


class SdkError(Exception):
    def __init__(self, code: str, message: str, stage: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.stage = stage
        self.context = context or {}


class DecodeError(SdkError):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(code="decode_error", message=message, stage="decode", context=context)


class ValidationError(SdkError):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(code="validation_error", message=message, stage="validate", context=context)


class NormalizationError(SdkError):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(code="normalization_error", message=message, stage="normalize", context=context)


class StorageError(SdkError):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(code="storage_error", message=message, stage="store", context=context)
