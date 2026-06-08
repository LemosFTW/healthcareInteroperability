"""
ATDD — Story 3.1: MessageEnvelope rastreia status e acumula erros ao longo do pipeline

Story: Epic 3 / Story 3.1
Acceptance Criteria cobertos: todos os 5 ACs da Story 3.1
"""
import pytest
from healthcare_sdk.contracts import (
    RawMessage,
    MessageEnvelope,
    ErrorDetail,
    STATUS_RECEIVED,
    STATUS_DECODED,
    STATUS_VALIDATED,
    STATUS_NORMALIZED,
    STATUS_STORED,
    STATUS_ERROR,
)


# ---------------------------------------------------------------------------
# Fixture base
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_message():
    return RawMessage(
        id="msg-001",
        protocol="hl7v2",
        raw_payload=b"MSH|...",
        message_type="ADT_A01",
    )


# ---------------------------------------------------------------------------
# AC1: Envelope criado a partir de RawMessage tem status inicial "received" e errors vazio
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_envelope_created_from_raw_message_has_received_status_and_empty_errors(raw_message):
    """
    AC: Given um MessageEnvelope criado a partir de um RawMessage
        When o envelope é criado
        Then o status inicial é "received" e a lista errors está vazia
    """
    envelope = MessageEnvelope.from_raw_message(raw_message)

    assert envelope.status == STATUS_RECEIVED, (
        f"Status inicial deveria ser '{STATUS_RECEIVED}', mas é '{envelope.status}'"
    )
    assert envelope.errors == [], (
        f"errors deveria ser [] inicialmente, mas é {envelope.errors}"
    )
    assert envelope.id == raw_message.id
    assert envelope.protocol == raw_message.protocol
    assert envelope.raw_payload == raw_message.raw_payload


# ---------------------------------------------------------------------------
# AC2: Status pode ser atualizado para qualquer valor válido do pipeline
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_envelope_status_can_be_updated_to_each_pipeline_stage(raw_message):
    """
    AC: Given um MessageEnvelope em processamento
        When atualizo o status para "decoded", "validated", "normalized" ou "stored"
        Then o status reflete o valor correto
    """
    envelope = MessageEnvelope.from_raw_message(raw_message)

    for expected_status in (STATUS_DECODED, STATUS_VALIDATED, STATUS_NORMALIZED, STATUS_STORED):
        envelope.status = expected_status
        assert envelope.status == expected_status, (
            f"Status deveria ser '{expected_status}', mas é '{envelope.status}'"
        )


# ---------------------------------------------------------------------------
# AC3: ErrorDetail adicionado a errors NÃO altera status automaticamente
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_adding_error_detail_does_not_change_status_automatically(raw_message):
    """
    AC: Given um erro ocorrendo em uma etapa do pipeline
        When crio um ErrorDetail com code, message, stage e context
        Then o ErrorDetail é adicionado a MessageEnvelope.errors
            sem alterar o status para "error" automaticamente
    """
    envelope = MessageEnvelope.from_raw_message(raw_message)
    envelope.status = STATUS_DECODED

    error = ErrorDetail(
        code="DECODE_WARN",
        message="Partial decode — missing optional field",
        stage="decode",
        context={"field": "patient_name"},
    )
    envelope.errors.append(error)

    assert envelope.status == STATUS_DECODED, (
        f"Status não deveria mudar automaticamente ao adicionar erro, "
        f"mas mudou para '{envelope.status}'"
    )
    assert len(envelope.errors) == 1
    assert envelope.errors[0].code == "DECODE_WARN"
    assert envelope.errors[0].stage == "decode"
    assert envelope.errors[0].context == {"field": "patient_name"}


# ---------------------------------------------------------------------------
# AC4: Múltiplos ErrorDetails de etapas diferentes ficam todos em errors
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_multiple_errors_from_different_stages_all_present(raw_message):
    """
    AC: Given múltiplos erros ocorrendo em etapas diferentes
        When cada um é adicionado ao envelope
        Then todos os ErrorDetail estão presentes em MessageEnvelope.errors
            com suas respectivas stage
    """
    envelope = MessageEnvelope.from_raw_message(raw_message)

    errors_to_add = [
        ErrorDetail(code="E001", message="Decode warning", stage="decode"),
        ErrorDetail(code="E002", message="Validation failed", stage="validate"),
        ErrorDetail(code="E003", message="Normalize skipped", stage="normalize"),
    ]
    for err in errors_to_add:
        envelope.errors.append(err)

    assert len(envelope.errors) == 3, (
        f"Esperados 3 erros, encontrados {len(envelope.errors)}"
    )
    stages = {e.stage for e in envelope.errors}
    assert stages == {"decode", "validate", "normalize"}, (
        f"Etapas esperadas: decode, validate, normalize. Encontradas: {stages}"
    )


# ---------------------------------------------------------------------------
# AC5: MessageEnvelope com status "error" tem errors não vazio e payloads podem ser None
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_envelope_with_error_status_has_at_least_one_error_and_nullable_payloads(raw_message):
    """
    AC: Given um MessageEnvelope com status "error"
        When inspeciono o objeto
        Then errors contém ao menos um ErrorDetail
            e decoded_payload ou normalized_payload podem ser None
    """
    envelope = MessageEnvelope.from_raw_message(raw_message)
    envelope.errors.append(
        ErrorDetail(code="FATAL", message="Unexpected decode failure", stage="decode")
    )
    envelope.status = STATUS_ERROR

    assert envelope.status == STATUS_ERROR
    assert len(envelope.errors) >= 1, "errors deveria conter ao menos um ErrorDetail"
    # payloads podem ser None quando há status de erro
    assert envelope.decoded_payload is None
    assert envelope.normalized_payload is None
