"""
ATDD — Story 4.1: Implementar Base SQLAlchemy e entidade MessageLog

Story: Epic 4 / Story 4.1
Acceptance Criteria cobertos: todos os 3 ACs da Story 4.1

Verifica que a Base declarativa SQLAlchemy está disponível em healthcare_sdk.repositories,
que MessageLog cria a tabela correta e que um envelope pode ser persistido nela.
"""
import json
import uuid
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


# ---------------------------------------------------------------------------
# AC1: Base importável de healthcare_sdk.repositories — usado para entidade customizada
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="TODO: implement Base")
@pytest.mark.p0
def test_base_is_importable_from_repositories():
    """
    AC: Given a Base declarativa SQLAlchemy disponível em healthcare_sdk.repositories
        When importo e uso Base em uma classe de entidade customizada
        Then a entidade é reconhecida pelo SQLAlchemy sem erro
    """
    from healthcare_sdk.repositories import Base

    class CustomEntity(Base):
        __tablename__ = "custom_entity_test"
        from sqlalchemy import Column, String
        id = Column(String, primary_key=True)
        name = Column(String)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "custom_entity_test" in tables, (
        f"Tabela 'custom_entity_test' não foi criada. Tabelas: {tables}"
    )


# ---------------------------------------------------------------------------
# AC2: MessageLog tem os campos corretos e tabela é criada no SQLite in-memory
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="TODO: implement messagelog and Base")
@pytest.mark.p0
def test_message_log_table_created_with_all_required_fields():
    """
    AC: Given a entidade MessageLog com campos id (UUID), protocol (str), status (str),
            created_at (datetime), updated_at (datetime), errors (JSON)
        When executo Base.metadata.create_all(engine) com banco SQLite in-memory
        Then a tabela message_log é criada com todos os campos corretos
    """
    from healthcare_sdk.repositories import Base
    from healthcare_sdk.repositories.messageLog import MessageLog

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    assert "message_log" in inspector.get_table_names(), (
        "Tabela 'message_log' não foi criada"
    )

    columns = {col["name"] for col in inspector.get_columns("message_log")}
    required = {"id", "protocol", "status", "created_at", "updated_at", "errors"}
    assert required.issubset(columns), (
        f"Campos obrigatórios faltando: {required - columns}. Colunas encontradas: {columns}"
    )


# ---------------------------------------------------------------------------
# AC3: MessageEnvelope processado pode ser persistido no MessageLog
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="TODO: implement messagelog and Base")
@pytest.mark.p0
def test_message_envelope_data_persisted_in_message_log():
    """
    AC: Given um MessageEnvelope processado pelo pipeline
        When persisto os dados no MessageLog
        Then todos os campos são preenchidos corretamente incluindo o JSON de erros
    """
    from healthcare_sdk.repositories import Base
    from healthcare_sdk.repositories.messageLog import MessageLog
    from healthcare_sdk.contracts import (
        MessageEnvelope,
        ErrorDetail,
        RawMessage,
        STATUS_STORED,
    )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    # Simula um envelope processado pelo pipeline
    raw_msg = RawMessage(id="env-001", protocol="hl7v2", raw_payload=b"MSH|...", message_type="ADT")
    envelope = MessageEnvelope.from_raw_message(raw_msg)
    envelope.status = STATUS_STORED
    envelope.errors = [
        ErrorDetail(code="W001", message="Non-critical warning", stage="normalize"),
    ]

    with Session(engine) as session:
        log = MessageLog.from_envelope(envelope)
        session.add(log)
        session.commit()
        log_id = log.id

    # Recuperar e verificar
    with Session(engine) as session:
        retrieved = session.get(MessageLog, log_id)

    assert retrieved is not None
    assert retrieved.protocol == "hl7v2"
    assert retrieved.status == STATUS_STORED
    assert retrieved.created_at is not None
    assert retrieved.updated_at is not None

    # errors devem ser serializados como JSON
    errors_data = retrieved.errors
    if isinstance(errors_data, str):
        errors_data = json.loads(errors_data)
    assert isinstance(errors_data, list), f"errors deveria ser uma lista, got: {type(errors_data)}"
    assert len(errors_data) == 1
    assert errors_data[0]["code"] == "W001"
