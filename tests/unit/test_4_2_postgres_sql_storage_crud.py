"""
ATDD — Story 4.2: PostgreSqlStorage com operações CRUD completas

Story: Epic 4 / Story 4.2
Acceptance Criteria cobertos: todos os 5 ACs da Story 4.2

Usa SQLite in-memory como backend para testar todas as operações CRUD
sem depender de um servidor PostgreSQL real.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from healthcare_sdk.repositories import Base
from healthcare_sdk.repositories.postgreSqlStorage import PostgreSqlStorage
from healthcare_sdk.contracts import MessageEnvelope, RawMessage, STATUS_STORED, STATUS_DECODED


# ---------------------------------------------------------------------------
# Fixture: engine SQLite in-memory + storage instanciado
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def storage(engine):
    return PostgreSqlStorage(engine=engine)


@pytest.fixture
def sample_envelope():
    raw = RawMessage(id="env-crud-01", protocol="hl7v2", raw_payload=b"MSH|...", message_type="ADT")
    env = MessageEnvelope.from_raw_message(raw)
    env.status = STATUS_STORED
    return env


# ---------------------------------------------------------------------------
# AC1: save(envelope) persiste e retorna id não-nulo
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_save_persists_envelope_and_returns_non_null_id(storage, sample_envelope):
    """
    AC: Given um PostgreSqlStorage conectado a um banco SQLite in-memory via fixture
        When chamo save(envelope)
        Then o envelope é persistido e retorna um id não-nulo
    """
    log_id = storage.save(sample_envelope)

    assert log_id is not None, "save() deveria retornar um id não-nulo"
    assert isinstance(log_id, str) and len(log_id) > 0, f"id inválido: {log_id!r}"


# ---------------------------------------------------------------------------
# AC2: read({"id": log_id}) retorna o registro correto
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_read_by_id_returns_correct_record(storage, sample_envelope):
    """
    AC: Given um MessageLog previamente salvo
        When chamo read({"id": log_id})
        Then retorna o registro correto
    """
    log_id = storage.save(sample_envelope)

    record = storage.read({"id": log_id})

    assert record is not None, "read() não deveria retornar None para um id válido"
    assert record["id"] == log_id
    assert record["protocol"] == "hl7v2"
    assert record["status"] == STATUS_STORED


# ---------------------------------------------------------------------------
# AC3: update({"id": log_id}, {"status": "stored"}) atualiza e retorna True
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_update_status_field_returns_true_and_persists(storage, sample_envelope):
    """
    AC: Given um MessageLog previamente salvo
        When chamo update({"id": log_id}, {"status": "stored"})
        Then o campo status é atualizado e retorna True
    """
    sample_envelope.status = STATUS_DECODED
    log_id = storage.save(sample_envelope)

    result = storage.update({"id": log_id}, {"status": STATUS_STORED})

    assert result is True, f"update() deveria retornar True, retornou {result!r}"

    updated = storage.read({"id": log_id})
    assert updated["status"] == STATUS_STORED, (
        f"Status não foi atualizado: {updated['status']!r}"
    )


# ---------------------------------------------------------------------------
# AC4: delete({"id": log_id}) remove o registro e retorna True
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_delete_removes_record_and_returns_true(storage, sample_envelope):
    """
    AC: Given um MessageLog previamente salvo
        When chamo delete({"id": log_id})
        Then o registro é removido e retorna True
    """
    log_id = storage.save(sample_envelope)

    result = storage.delete({"id": log_id})

    assert result is True, f"delete() deveria retornar True, retornou {result!r}"

    record = storage.read({"id": log_id})
    assert record is None or record == {}, (
        f"Registro não foi removido após delete(): {record}"
    )


# ---------------------------------------------------------------------------
# AC5: connection() retorna sessão ativa sem lançar exceção
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_connection_returns_active_session_without_exception(storage):
    """
    AC: Given um PostgreSqlStorage instanciado
        When chamo connection()
        Then retorna a sessão ativa do banco sem lançar exceção
    """
    session = storage.connection()

    assert session is not None, "connection() não deveria retornar None"
    # Verifica que a sessão está funcional fazendo uma consulta simples
    try:
        from sqlalchemy import text
        session.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.fail(f"connection() retornou sessão não funcional: {exc}")
    finally:
        session.close()
