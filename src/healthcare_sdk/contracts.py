from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


RawPayload = Union[str, bytes]
DecodedPayload = Dict[str, Any]
NormalizedPayload = Dict[str, Any]

STATUS_RECEIVED = "received"
STATUS_DECODED = "decoded"
STATUS_VALIDATED = "validated"
STATUS_NORMALIZED = "normalized"
STATUS_STORED = "stored"
STATUS_ERROR = "error"


@dataclass
class RawMessage:
    id: str
    protocol: str
    raw_payload: RawPayload
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_type: Optional[str] = None


@dataclass
class ErrorDetail:
    code: str
    message: str
    stage: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class MessageEnvelope:
    id: str
    protocol: str
    message_type: str
    raw_payload: RawPayload
    decoded_payload: Optional[DecodedPayload] = None
    normalized_payload: Optional[NormalizedPayload] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[ErrorDetail] = field(default_factory=list)
    status: str = STATUS_RECEIVED


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ErrorDetail] = field(default_factory=list)
