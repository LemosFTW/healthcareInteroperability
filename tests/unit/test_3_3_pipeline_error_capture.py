"""
ATDD — Story 3.3: Pipeline captura erros por etapa sem interromper o fluxo

Story: Epic 3 / Story 3.3
Acceptance Criteria cobertos: todos os 4 ACs da Story 3.3

Verifica que DefaultHealthCareUsecase captura exceções e resultados de validação inválidos,
registrando ErrorDetail no envelope sem propagar a exceção ao chamador.
"""
import pytest
from healthcare_sdk.contracts import (
    RawMessage,
    MessageEnvelope,
    ErrorDetail,
    ValidationResult,
    STATUS_DECODED,
    STATUS_ERROR,
)
from healthcare_sdk.errors import DecodeError, StorageError
from healthcare_sdk.usecases.defaultHealthCareUsecase import DefaultHealthCareUsecase


# ---------------------------------------------------------------------------
# Helpers compartilhados
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_message():
    return RawMessage(id="m-err", protocol="hl7v2", raw_payload=b"MSH|...", message_type="ADT")


class PassValidator:
    def validate(self, decoded_payload):
        return ValidationResult(is_valid=True)


class PassNormalizer:
    def normalizeData(self, decoded_payload):
        return decoded_payload


class PassStorage:
    def save(self, envelope) -> str: return "id-ok"
    def connection(self): return None
    def read(self, q): return {}
    def delete(self, q): return True
    def update(self, q, d): return True


class PassDecoder:
    def decode(self, raw_message):
        return {"data": "ok"}


# ---------------------------------------------------------------------------
# AC1: DecodeError é capturado — envelope tem stage="decode" e status="error"
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_decode_error_captured_with_decode_stage_and_error_status(raw_message):
    """
    AC: Given um Decoder que lança DecodeError ao processar a mensagem
        When o DefaultHealthCareUsecase executa
        Then o erro é capturado, adicionado a MessageEnvelope.errors com stage="decode",
             e o status é definido como "error"
    """
    class FailingDecoder:
        def decode(self, raw_message):
            raise DecodeError("Cannot parse HL7 message", context={"raw": str(raw_message.raw_payload)})

    usecase = DefaultHealthCareUsecase(
        decoder=FailingDecoder(),
        validator=PassValidator(),
        normalizer=PassNormalizer(),
        storage=PassStorage(),
    )

    result = usecase.execute(raw_message)

    assert result.status == STATUS_ERROR, f"Status esperado 'error', got '{result.status}'"
    assert len(result.errors) >= 1, "Deve haver pelo menos um ErrorDetail em errors"

    decode_errors = [e for e in result.errors if e.stage == "decode"]
    assert decode_errors, f"Nenhum ErrorDetail com stage='decode' encontrado. errors={result.errors}"
    assert decode_errors[0].code == "decode_error"
    assert "Cannot parse" in decode_errors[0].message


# ---------------------------------------------------------------------------
# AC2: ValidationResult(is_valid=False) — erros adicionados com stage="validate"
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_invalid_validation_result_errors_added_with_validate_stage(raw_message):
    """
    AC: Given um Validator que retorna ValidationResult(is_valid=False, errors=[...])
        When o DefaultHealthCareUsecase executa
        Then os erros de validação são adicionados ao MessageEnvelope.errors com stage="validate"
    """
    class FailingValidator:
        def validate(self, decoded_payload):
            return ValidationResult(
                is_valid=False,
                errors=[
                    ErrorDetail(code="V001", message="Missing patient ID", stage="validate"),
                    ErrorDetail(code="V002", message="Invalid date format", stage="validate"),
                ],
            )

    usecase = DefaultHealthCareUsecase(
        decoder=PassDecoder(),
        validator=FailingValidator(),
        normalizer=PassNormalizer(),
        storage=PassStorage(),
    )

    result = usecase.execute(raw_message)

    validate_errors = [e for e in result.errors if e.stage == "validate"]
    assert len(validate_errors) >= 1, (
        f"Esperados erros com stage='validate', encontrados: {[e.stage for e in result.errors]}"
    )
    codes = {e.code for e in validate_errors}
    assert "V001" in codes and "V002" in codes


# ---------------------------------------------------------------------------
# AC3: StorageError é capturado — envelope tem stage="store" e status="error"
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_storage_error_captured_with_store_stage_and_error_status(raw_message):
    """
    AC: Given um Storage que lança StorageError ao salvar
        When o DefaultHealthCareUsecase executa
        Then o erro é capturado e adicionado ao envelope com stage="store" e status "error"
    """
    class FailingStorage:
        def save(self, envelope) -> str:
            raise StorageError("Database connection lost")
        def connection(self): return None
        def read(self, q): return {}
        def delete(self, q): return True
        def update(self, q, d): return True

    usecase = DefaultHealthCareUsecase(
        decoder=PassDecoder(),
        validator=PassValidator(),
        normalizer=PassNormalizer(),
        storage=FailingStorage(),
    )

    result = usecase.execute(raw_message)

    assert result.status == STATUS_ERROR, f"Status esperado 'error', got '{result.status}'"
    store_errors = [e for e in result.errors if e.stage == "store"]
    assert store_errors, f"Nenhum ErrorDetail com stage='store' encontrado. errors={result.errors}"
    assert store_errors[0].code == "storage_error"
    assert "Database connection lost" in store_errors[0].message


# ---------------------------------------------------------------------------
# AC4: Envelope retornado tem ErrorDetail com code, message e stage preenchidos
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_returned_envelope_error_detail_has_code_message_and_stage(raw_message):
    """
    AC: Given um MessageEnvelope com status "error" após falha no pipeline
        When inspeciono o envelope retornado por execute()
        Then errors contém o ErrorDetail da etapa que falhou
             com code, message e stage preenchidos
    """
    class FailingDecoder:
        def decode(self, raw_message):
            raise DecodeError("Unsupported encoding", context={"hint": "UTF-8 expected"})

    usecase = DefaultHealthCareUsecase(
        decoder=FailingDecoder(),
        validator=PassValidator(),
        normalizer=PassNormalizer(),
        storage=PassStorage(),
    )

    result = usecase.execute(raw_message)

    assert len(result.errors) >= 1
    error = result.errors[0]

    assert error.code, f"ErrorDetail.code está vazio: {error!r}"
    assert error.message, f"ErrorDetail.message está vazio: {error!r}"
    assert error.stage, f"ErrorDetail.stage está vazio: {error!r}"
    assert error.stage == "decode"
    assert error.code == "decode_error"
    assert "Unsupported encoding" in error.message
