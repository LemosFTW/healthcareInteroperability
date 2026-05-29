"""
conftest.py — Fixtures base do Healthcare Framework SDK
Implementado como parte da Story 1.1: Criar infraestrutura de testes com pytest.

INSTRUCOES PARA O DESENVOLVEDOR (Story 1.1):
- Este arquivo define as fixtures base que todos os testes usam.
- Adicione pytest, httpx e testcontainers-python ao pyproject.toml.
- Configure os markers em pyproject.toml [tool.pytest.ini_options].
- Expanda as fixtures conforme as Stories evoluem (fake components mais ricos em Story 3.x).
"""
import pytest


# ---------------------------------------------------------------------------
# Fake Components — implementacoes minimas dos contratos para uso em testes
# ---------------------------------------------------------------------------

class FakeDecoder:
    """Fake Decoder que retorna o payload bruto como decoded_payload."""

    def decode(self, raw_message):
        return {"source": raw_message.source, "data": raw_message.data}


class FakeValidator:
    """Fake Validator que sempre aprova a mensagem."""

    def validate(self, decoded_payload):
        # Retorna objeto compativel com ValidationResult
        # Substitua por import real quando o contrato estiver estavel.
        class _Result:
            is_valid = True
            errors = []

        return _Result()


class FakeNormalizer:
    """Fake Normalizer que retorna o payload sem transformacao."""

    def normalizeData(self, decoded_payload):
        return decoded_payload


class FakeStorage:
    """Fake Storage in-memory que implementa o contrato Storage."""

    def __init__(self):
        self._store = {}

    def save(self, envelope):
        import uuid
        record_id = str(uuid.uuid4())
        self._store[record_id] = envelope
        return record_id

    def read(self, filters):
        return list(self._store.values())

    def update(self, filters, data):
        return True

    def delete(self, filters):
        return True

    def connection(self):
        return None  # In-memory nao precisa de conexao real


# ---------------------------------------------------------------------------
# Fixtures pytest
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_decoder():
    return FakeDecoder()


@pytest.fixture
def fake_validator():
    return FakeValidator()


@pytest.fixture
def fake_normalizer():
    return FakeNormalizer()


@pytest.fixture
def fake_storage():
    return FakeStorage()
