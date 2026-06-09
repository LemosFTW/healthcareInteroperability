from typing import Any, Dict

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from .base import Base
from .messageLog import MessageLog
from .storage import HealthCareStorage
from ..contracts import MessageEnvelope


class PostgreSqlStorage:
    """SQLAlchemy-backed storage. Accepts any SQLAlchemy engine (PostgreSQL, SQLite, etc.)."""

    def __init__(self, engine: Engine):
        self._engine = engine
        Base.metadata.create_all(engine)

    def connection(self) -> Session:
        return Session(self._engine)

    def save(self, envelope: MessageEnvelope) -> str:
        with Session(self._engine) as session:
            log = MessageLog.from_envelope(envelope)
            session.add(log)
            session.commit()
            session.refresh(log)
            return log.id

    def read(self, query: Dict[str, Any]) -> Dict[str, Any]:
        with Session(self._engine) as session:
            if "id" in query:
                log = session.get(MessageLog, query["id"])
                if log is None:
                    return {}
                return {
                    "id": log.id,
                    "protocol": log.protocol,
                    "status": log.status,
                    "created_at": log.created_at,
                    "updated_at": log.updated_at,
                    "errors": log.errors,
                }
        return {}

    def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
        with Session(self._engine) as session:
            if "id" in query:
                log = session.get(MessageLog, query["id"])
                if log is None:
                    return False
                for key, value in data.items():
                    if hasattr(log, key):
                        setattr(log, key, value)
                session.commit()
                return True
        return False

    def delete(self, query: Dict[str, Any]) -> bool:
        with Session(self._engine) as session:
            if "id" in query:
                log = session.get(MessageLog, query["id"])
                if log is None:
                    return False
                session.delete(log)
                session.commit()
                return True
        return False
