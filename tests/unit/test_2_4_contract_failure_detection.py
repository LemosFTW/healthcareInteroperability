"""
ATDD — Story 2.4: Garantir detecção de falhas de contrato na inicialização

Story: Epic 2 / Story 2.4
Acceptance Criteria cobertos: todos os 3 ACs da Story 2.4

Verifica que register_components() detecta violações de contrato na inicialização,
incluindo componentes com nome de método correto mas aridade incompatível com o Protocol.
"""
import pytest
from healthcare_sdk.sdk import register_components, ComponentRegistrationError
from healthcare_sdk.contracts import RawMessage, MessageEnvelope, ValidationResult


# ---------------------------------------------------------------------------
# Componentes com nome correto mas assinatura incompatível (aridade errada)
# ---------------------------------------------------------------------------

class DecoderMissingRawMessage:
    """decode() sem o parâmetro raw_message — assinatura incompatível com Decoder."""
    def decode(self):  # Protocol exige decode(self, raw_message)
        return {}


class ValidatorMissingPayload:
    """validate() sem o parâmetro decoded_payload — assinatura incompatível com Validator."""
    def validate(self):  # Protocol exige validate(self, decoded_payload)
        return ValidationResult(is_valid=True)


class NormalizerMissingPayload:
    """normalizeData() sem parâmetro — assinatura incompatível com Normalizer."""
    def normalizeData(self):  # Protocol exige normalizeData(self, decoded_payload)
        return {}


# ---------------------------------------------------------------------------
# Componentes válidos completos para AC2 e AC3
# ---------------------------------------------------------------------------

class CorrectDecoder:
    def decode(self, raw_message: RawMessage) -> dict:
        return {"data": str(raw_message.raw_payload)}


class CorrectValidator:
    def validate(self, decoded_payload: dict) -> ValidationResult:
        return ValidationResult(is_valid=True)


class CorrectNormalizer:
    def normalizeData(self, decoded_payload: dict) -> dict:
        return decoded_payload


class CorrectAdapter:
    def executeServer(self, port: int = 8000):
        pass
    def receive(self) -> RawMessage:
        return RawMessage(id="1", protocol="rest", raw_payload=b"test")


# ---------------------------------------------------------------------------
# AC1: Componente com método correto mas assinatura incompatível lança
#       ComponentRegistrationError ANTES de qualquer processamento de mensagem
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_decoder_with_wrong_arity_raises_registration_error():
    """
    AC: Given um componente com nome de método correto mas assinatura diferente do Protocol
        When passo para register_components()
        Then ComponentRegistrationError é lançado antes de qualquer processamento de mensagem
    """
    with pytest.raises(ComponentRegistrationError):
        register_components(decoders=[DecoderMissingRawMessage()])


@pytest.mark.p0
def test_validator_with_wrong_arity_raises_registration_error():
    """
    AC1 (validator): validate() sem decoded_payload deve falhar na inicialização.
    """
    with pytest.raises(ComponentRegistrationError):
        register_components(validators=[ValidatorMissingPayload()])


@pytest.mark.p0
def test_normalizer_with_wrong_arity_raises_registration_error():
    """
    AC1 (normalizer): normalizeData() sem decoded_payload deve falhar na inicialização.
    """
    with pytest.raises(ComponentRegistrationError):
        register_components(normalizers=[NormalizerMissingPayload()])


# ---------------------------------------------------------------------------
# AC2: Mensagem de erro indica o componente problemático e o contrato esperado
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_registration_error_message_identifies_component_and_contract():
    """
    AC: Given um componente inválido registrado
        When o erro é lançado
        Then a mensagem de erro indica o componente problemático e o contrato esperado
    """
    with pytest.raises(ComponentRegistrationError) as exc_info:
        register_components(decoders=[DecoderMissingRawMessage()])

    error_msg = str(exc_info.value)
    assert "decode" in error_msg.lower() or "decoder" in error_msg.lower(), (
        f"Mensagem de erro deveria identificar 'decode' ou 'Decoder', mas foi: {error_msg!r}"
    )


# ---------------------------------------------------------------------------
# AC3: Componentes válidos registrados não geram exceção de contrato ao processar mensagem
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_valid_components_produce_no_contract_errors_during_processing():
    """
    AC: Given todos os componentes válidos registrados com sucesso
        When o sistema processa uma mensagem posteriormente
        Then nenhuma exceção de contrato ocorre em tempo de processamento
        (falhas são de lógica, não de contrato)
    """
    result = register_components(
        adapters=[CorrectAdapter()],
        decoders=[CorrectDecoder()],
        validators=[CorrectValidator()],
        normalizers=[CorrectNormalizer()],
    )

    raw_msg = RawMessage(id="msg-1", protocol="rest", raw_payload=b"hello")

    # Processa a mensagem através dos componentes registrados — sem erro de contrato
    try:
        decoded = result.decoders[0].decode(raw_msg)
        validation = result.validators[0].validate(decoded)
        normalized = result.normalizers[0].normalizeData(decoded)
    except TypeError as exc:
        pytest.fail(
            f"Componente válido lançou TypeError (erro de contrato) durante processamento: {exc}"
        )
    except AttributeError as exc:
        pytest.fail(
            f"Componente válido lançou AttributeError (erro de contrato) durante processamento: {exc}"
        )

    assert validation.is_valid is True
    assert normalized == decoded
