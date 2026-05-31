import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MessageLog(Base):
    __tablename__ = "message_log"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    errors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True, default=list)

    @classmethod
    def from_envelope(cls, envelope) -> "MessageLog":
        errors_data = [
            {"code": e.code, "message": e.message, "stage": e.stage, "context": e.context}
            for e in (envelope.errors or [])
        ]
        return cls(
            id=str(envelope.id) if envelope.id else str(uuid.uuid4()),
            protocol=envelope.protocol,
            status=envelope.status,
            errors=errors_data,
        )
