"""
ATDD — Story 2.1: Verificar Protocols em runtime via isinstance()

Story: Epic 2 / Story 2.1
Acceptance Criteria cobertos: todos os 5 ACs da Story 2.1

Verifica que Decoder, Validator, Normalizer e AiHelper são @runtime_checkable Protocols
e que isinstance() retorna True para implementações corretas e False para classes vazias.
"""
import pytest
from healthcare_sdk.tools.decoder import Decoder
from healthcare_sdk.tools.validator import Validator
from healthcare_sdk.tools.normalizer import Normalizer
from healthcare_sdk.tools.aiHelper import AiHelper


# ---------------------------------------------------------------------------
# Implementações externas mínimas (simulam código do implementador)
# ---------------------------------------------------------------------------

class ConcreteDecoder:
    def decode(self, raw_message):
        return {"data": raw_message}


class ConcreteValidator:
    def validate(self, decoded_payload):
        from healthcare_sdk.contracts import ValidationResult
        return ValidationResult(is_valid=True)


class ConcreteNormalizer:
    def normalizeData(self, decoded_payload):
        return decoded_payload


class ConcreteAiHelper:
    def generateResponse(self, prompt: str) -> str:
        return f"response to: {prompt}"


class EmptyClass:
    """Classe sem nenhum dos métodos exigidos pelos Protocols."""
    pass


# ---------------------------------------------------------------------------
# AC1: Classe com decode() satisfaz isinstance(obj, Decoder)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_class_with_decode_satisfies_decoder_protocol():
    """
    AC: Given uma classe que implementa decode(raw_message) corretamente
        When verifico isinstance(obj, Decoder)
        Then retorna True
    """
    obj = ConcreteDecoder()
    assert isinstance(obj, Decoder), (
        "ConcreteDecoder implementa decode() mas isinstance(obj, Decoder) retornou False. "
        "Verifique se Decoder está decorado com @runtime_checkable."
    )


# ---------------------------------------------------------------------------
# AC2: Classe com validate() satisfaz isinstance(obj, Validator)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_class_with_validate_satisfies_validator_protocol():
    """
    AC: Given uma classe que implementa validate(decoded_payload) corretamente
        When verifico isinstance(obj, Validator)
        Then retorna True
    """
    obj = ConcreteValidator()
    assert isinstance(obj, Validator), (
        "ConcreteValidator implementa validate() mas isinstance(obj, Validator) retornou False."
    )


# ---------------------------------------------------------------------------
# AC3: Classe com normalizeData() satisfaz isinstance(obj, Normalizer)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_class_with_normalizedata_satisfies_normalizer_protocol():
    """
    AC: Given uma classe que implementa normalizeData(decoded_payload) corretamente
        When verifico isinstance(obj, Normalizer)
        Then retorna True
    """
    obj = ConcreteNormalizer()
    assert isinstance(obj, Normalizer), (
        "ConcreteNormalizer implementa normalizeData() mas isinstance(obj, Normalizer) retornou False."
    )


# ---------------------------------------------------------------------------
# AC4: Classe com generateResponse() satisfaz isinstance(obj, AiHelper)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_class_with_generateresponse_satisfies_aihelper_protocol():
    """
    AC: Given uma classe que implementa generateResponse(prompt) corretamente
        When verifico isinstance(obj, AiHelper)
        Then retorna True
    """
    obj = ConcreteAiHelper()
    assert isinstance(obj, AiHelper), (
        "ConcreteAiHelper implementa generateResponse() mas isinstance(obj, AiHelper) retornou False."
    )


# ---------------------------------------------------------------------------
# AC5: Classe vazia retorna False para todos os Protocols
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_empty_class_fails_isinstance_for_all_protocols():
    """
    AC: Given uma classe sem nenhum dos métodos exigidos
        When verifico isinstance(obj, Decoder) ou qualquer outro Protocol
        Then retorna False
    """
    obj = EmptyClass()
    assert not isinstance(obj, Decoder), "EmptyClass não deveria satisfazer Decoder"
    assert not isinstance(obj, Validator), "EmptyClass não deveria satisfazer Validator"
    assert not isinstance(obj, Normalizer), "EmptyClass não deveria satisfazer Normalizer"
    assert not isinstance(obj, AiHelper), "EmptyClass não deveria satisfazer AiHelper"
