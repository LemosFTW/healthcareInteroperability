"""
ATDD — Story 3.2: Implementar DefaultHealthCareUsecase como orchestrator built-in

Story: Epic 3 / Story 3.2
Acceptance Criteria cobertos: todos os 5 ACs da Story 3.2

Verifica que DefaultHealthCareUsecase orquestra decode→validate→normalize→store,
atualizando o status do envelope em cada etapa antes de chamar o componente seguinte.
"""
import pytest
from healthcare_sdk.contracts import (
    MessageEnvelope,
    RawMessage,
    ValidationResult,
    STATUS_DECODED,
    STATUS_VALIDATED,
    STATUS_NORMALIZED,
    STATUS_STORED,
)
from healthcare_sdk.usecases import HealthCareUsecase


# ---------------------------------------------------------------------------
# Fakes simples para o happy path
# ---------------------------------------------------------------------------

class FakeDecoder:
    def decode(self, raw_message):
        return {"data": raw_message.raw_payload.decode() if isinstance(raw_message.raw_payload, bytes) else raw_message.raw_payload}


class FakeValidator:
    def validate(self, decoded_payload):
        return ValidationResult(is_valid=True)


class FakeNormalizer:
    def normalizeData(self, decoded_payload):
        return {**decoded_payload, "normalized": True}


class FakeStorage:
    def __init__(self):
        self.saved = []

    def save(self, envelope) -> str:
        self.saved.append(envelope)
        return "saved-id-1"

    def connection(self):
        return None

    def read(self, query):
        return {}

    def delete(self, query):
        return True

    def update(self, query, data):
        return True


@pytest.fixture
def raw_message():
    return RawMessage(id="m-001", protocol="hl7v2", raw_payload=b"MSH|...", message_type="ADT")


@pytest.fixture
def fake_components():
    return FakeDecoder(), FakeValidator(), FakeNormalizer(), FakeStorage()


# ---------------------------------------------------------------------------
# AC1: execute() com fakes válidos retorna envelope com status "stored" e errors vazio
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_execute_full_pipeline_returns_stored_envelope_with_no_errors(raw_message, fake_components):
    """
    AC: Given um DefaultHealthCareUsecase configurado com Decoder, Validator, Normalizer e Storage válidos
        When chamo execute(raw_message)
        Then retorna um MessageEnvelope com status "stored" e errors vazio
    """
    from healthcare_sdk.usecases.defaultHealthCareUsecase import DefaultHealthCareUsecase

    decoder, validator, normalizer, storage = fake_components
    usecase = DefaultHealthCareUsecase(decoder=decoder, validator=validator, normalizer=normalizer, storage=storage)

    result = usecase.execute(raw_message)

    assert isinstance(result, MessageEnvelope)
    assert result.status == STATUS_STORED, f"Expected 'stored', got '{result.status}'"
    assert result.errors == [], f"Expected no errors, got {result.errors}"


# ---------------------------------------------------------------------------
# AC2: status = "decoded" é definido ANTES de chamar o validator
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_status_is_decoded_before_validator_is_called(monkeypatch, raw_message, fake_components):
    """
    AC: Given o DefaultHealthCareUsecase em execução
        When a etapa de decode é concluída com sucesso
        Then MessageEnvelope.status é atualizado para "decoded" antes de chamar o validator
    """
    from healthcare_sdk.usecases.defaultHealthCareUsecase import DefaultHealthCareUsecase

    decoder, _, normalizer, storage = fake_components
    envelope_holder = []

    # Intercept from_raw_message to capture the envelope reference
    original = MessageEnvelope.from_raw_message.__func__

    def patched(cls, raw_msg):
        env = original(cls, raw_msg)
        envelope_holder.append(env)
        return env

    monkeypatch.setattr(MessageEnvelope, "from_raw_message", classmethod(patched))

    status_when_validate_called = []

    class SpyValidator:
        def validate(self, decoded_payload):
            if envelope_holder:
                status_when_validate_called.append(envelope_holder[0].status)
            return ValidationResult(is_valid=True)

    usecase = DefaultHealthCareUsecase(
        decoder=decoder,
        validator=SpyValidator(),
        normalizer=normalizer,
        storage=storage,
    )
    usecase.execute(raw_message)

    assert status_when_validate_called == [STATUS_DECODED], (
        f"Status quando validator foi chamado: {status_when_validate_called}, esperado ['{STATUS_DECODED}']"
    )


# ---------------------------------------------------------------------------
# AC3: status = "validated" é definido ANTES de chamar o normalizer
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_status_is_validated_before_normalizer_is_called(monkeypatch, raw_message, fake_components):
    """
    AC: Given o DefaultHealthCareUsecase em execução
        When a etapa de validate é concluída com sucesso
        Then MessageEnvelope.status é atualizado para "validated" antes de chamar o normalizer
    """
    from healthcare_sdk.usecases.defaultHealthCareUsecase import DefaultHealthCareUsecase

    decoder, validator, _, storage = fake_components
    envelope_holder = []

    original = MessageEnvelope.from_raw_message.__func__

    def patched(cls, raw_msg):
        env = original(cls, raw_msg)
        envelope_holder.append(env)
        return env

    monkeypatch.setattr(MessageEnvelope, "from_raw_message", classmethod(patched))

    status_when_normalize_called = []

    class SpyNormalizer:
        def normalizeData(self, decoded_payload):
            if envelope_holder:
                status_when_normalize_called.append(envelope_holder[0].status)
            return decoded_payload

    usecase = DefaultHealthCareUsecase(
        decoder=decoder,
        validator=validator,
        normalizer=SpyNormalizer(),
        storage=storage,
    )
    usecase.execute(raw_message)

    assert status_when_normalize_called == [STATUS_VALIDATED], (
        f"Status quando normalizer foi chamado: {status_when_normalize_called}, esperado ['{STATUS_VALIDATED}']"
    )


# ---------------------------------------------------------------------------
# AC4: status = "normalized" é definido ANTES de chamar o storage
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_status_is_normalized_before_storage_is_called(raw_message, fake_components):
    """
    AC: Given o DefaultHealthCareUsecase em execução
        When a etapa de normalize é concluída com sucesso
        Then MessageEnvelope.status é atualizado para "normalized" antes de chamar o storage
    """
    from healthcare_sdk.usecases.defaultHealthCareUsecase import DefaultHealthCareUsecase

    decoder, validator, normalizer, _ = fake_components
    status_when_save_called = []

    class SpyStorage:
        def save(self, envelope) -> str:
            status_when_save_called.append(envelope.status)
            return "id-1"
        def connection(self): return None
        def read(self, q): return {}
        def delete(self, q): return True
        def update(self, q, d): return True

    usecase = DefaultHealthCareUsecase(
        decoder=decoder,
        validator=validator,
        normalizer=normalizer,
        storage=SpyStorage(),
    )
    usecase.execute(raw_message)

    assert status_when_save_called == [STATUS_NORMALIZED], (
        f"Status quando storage.save() foi chamado: {status_when_save_called}, esperado ['{STATUS_NORMALIZED}']"
    )


# ---------------------------------------------------------------------------
# AC5: isinstance(DefaultHealthCareUsecase(...), HealthCareUsecase) retorna True
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_default_usecase_satisfies_healthcare_usecase_protocol(fake_components):
    """
    AC: Given o DefaultHealthCareUsecase registrado via register_components(usecases=[...])
        When verifico isinstance(obj, HealthCareUsecase)
        Then retorna True
    """
    from healthcare_sdk.usecases.defaultHealthCareUsecase import DefaultHealthCareUsecase
    from healthcare_sdk.sdk import register_components

    decoder, validator, normalizer, storage = fake_components
    usecase = DefaultHealthCareUsecase(decoder=decoder, validator=validator, normalizer=normalizer, storage=storage)

    assert isinstance(usecase, HealthCareUsecase), (
        "DefaultHealthCareUsecase não satisfaz isinstance(obj, HealthCareUsecase). "
        "Certifique-se de que implementa execute(self, raw_message)."
    )

    # Também verifica aceitação em register_components()
    result = register_components(usecases=[usecase])
    assert len(result.usecases) == 1
