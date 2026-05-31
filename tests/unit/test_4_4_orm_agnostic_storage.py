"""
ATDD — Story 4.4: Storage agnóstico a ORM — implementação sem SQLAlchemy aceita

Story: Epic 4 / Story 4.4
Acceptance Criteria cobertos: todos os 3 ACs da Story 4.4

Verifica que o contrato HealthCareStorage é um Protocol puro (sem dependência de SQLAlchemy)
e que uma implementação in-memory sem nenhum ORM satisfaz o contrato e é aceita pelo SDK.
"""
import uuid
import pytest
from pathlib import Path

from healthcare_sdk.repositories.storage import HealthCareStorage
from healthcare_sdk.sdk import register_components, ComponentRegistrationError


# ---------------------------------------------------------------------------
# InMemoryStorage — implementação sem qualquer dependência de SQLAlchemy
# (simula uma implementação do usuário usando dict, arquivo, MongoDB, etc.)
# ---------------------------------------------------------------------------

class InMemoryStorage:
    """Storage puramente in-memory — zero dependências de ORM ou banco de dados."""

    def __init__(self):
        self._store: dict = {}

    def save(self, envelope) -> str:
        record_id = str(uuid.uuid4())
        self._store[record_id] = {
            "id": record_id,
            "protocol": envelope.protocol,
            "status": envelope.status,
            "errors": [{"code": e.code, "message": e.message, "stage": e.stage} for e in envelope.errors],
        }
        return record_id

    def read(self, query: dict) -> dict:
        if "id" in query:
            return self._store.get(query["id"], {})
        return {}

    def update(self, query: dict, data: dict) -> bool:
        if "id" in query and query["id"] in self._store:
            self._store[query["id"]].update(data)
            return True
        return False

    def delete(self, query: dict) -> bool:
        if "id" in query and query["id"] in self._store:
            del self._store[query["id"]]
            return True
        return False

    def connection(self):
        return None  # In-memory não precisa de conexão


# ---------------------------------------------------------------------------
# AC1: InMemoryStorage satisfaz isinstance(obj, HealthCareStorage)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_in_memory_storage_satisfies_health_care_storage_protocol():
    """
    AC: Given uma classe InMemoryStorage que implementa save, read, update, delete, connection
            sem usar SQLAlchemy
        When verifico isinstance(obj, HealthCareStorage)
        Then retorna True
    """
    storage = InMemoryStorage()

    assert isinstance(storage, HealthCareStorage), (
        "InMemoryStorage implementa todos os métodos de HealthCareStorage "
        "mas isinstance() retornou False. Verifique se HealthCareStorage é @runtime_checkable."
    )


# ---------------------------------------------------------------------------
# AC2: InMemoryStorage aceito por register_components() sem ComponentRegistrationError
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_in_memory_storage_accepted_by_register_components():
    """
    AC: Given um InMemoryStorage válido
        When passo para register_components(storages=[InMemoryStorage()])
        Then é aceito sem ComponentRegistrationError
    """
    storage = InMemoryStorage()

    try:
        result = register_components(storages=[storage])
    except ComponentRegistrationError as exc:
        pytest.fail(
            f"register_components() rejeitou InMemoryStorage válido: {exc}"
        )

    assert len(result.storages) == 1
    assert result.storages[0] is storage


# ---------------------------------------------------------------------------
# AC3: HealthCareStorage Protocol não importa SQLAlchemy
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_healthcare_storage_protocol_has_no_sqlalchemy_imports():
    """
    AC: Given InMemoryStorage sem nenhuma dependência de SQLAlchemy
        When executo os testes do framework
        Then nenhum import de SQLAlchemy é exigido para usar o contrato Storage

    Verifica estaticamente que storage.py não importa SQLAlchemy diretamente.
    """
    storage_file = (
        Path(__file__).parent.parent.parent
        / "src" / "healthcare_sdk" / "repositories" / "storage.py"
    )
    content = storage_file.read_text(encoding="utf-8")

    assert "sqlalchemy" not in content.lower(), (
        "storage.py importa SQLAlchemy, o que cria acoplamento desnecessário no contrato. "
        "O Protocol HealthCareStorage deve ser agnóstico a ORM."
    )


# ---------------------------------------------------------------------------
# Bônus: verifica que InMemoryStorage funciona corretamente ponta a ponta
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_in_memory_storage_full_crud_without_sqlalchemy(fake_storage):
    """
    AC derivado: InMemoryStorage do conftest (FakeStorage) também satisfaz o protocolo
    e todas as operações funcionam sem SQLAlchemy.
    """
    # Verifica que o FakeStorage do conftest também satisfaz o contrato
    assert isinstance(fake_storage, HealthCareStorage), (
        "FakeStorage do conftest não satisfaz HealthCareStorage Protocol"
    )

    from healthcare_sdk.contracts import RawMessage, MessageEnvelope, STATUS_STORED

    raw = RawMessage(id="test-001", protocol="fhir", raw_payload=b"{}", message_type="Patient")
    envelope = MessageEnvelope.from_raw_message(raw)
    envelope.status = STATUS_STORED

    # Save
    saved_id = fake_storage.save(envelope)
    assert saved_id is not None

    # Read
    records = fake_storage.read({"id": saved_id})
    assert records is not None

    # Update
    result = fake_storage.update({"id": saved_id}, {"status": "updated"})
    assert result is True

    # Delete
    result = fake_storage.delete({"id": saved_id})
    assert result is True

    # Connection
    conn = fake_storage.connection()
    assert conn is None  # FakeStorage retorna None para connection()
