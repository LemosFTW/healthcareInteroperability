"""
ATDD — Story 2.2: Usar NormalizerTemplate e ValidatorTemplate como base para implementações

Story: Epic 2 / Story 2.2
Acceptance Criteria cobertos: todos os 4 ACs da Story 2.2

Verifica que NormalizerTemplate e ValidatorTemplate funcionam como ABCs que:
- Forçam TypeError ao instanciar subclasses sem implementar métodos abstratos
- Satisfazem isinstance() com seus respectivos Protocols após implementação
- Expõem self.aiHelper = None por padrão no NormalizerTemplate
"""
import pytest
from healthcare_sdk.tools.normalizer import Normalizer, NormalizerTemplate
from healthcare_sdk.tools.validator import Validator, ValidatorTemplate


# ---------------------------------------------------------------------------
# AC1: Subclasse de NormalizerTemplate sem normalizeData() lança TypeError
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_normalizer_template_subclass_without_method_raises_type_error():
    """
    AC: Given uma classe que herda de NormalizerTemplate sem implementar normalizeData()
        When tento instanciar essa classe
        Then Python lança TypeError indicando que o método abstrato não foi implementado
    """
    class IncompleteNormalizer(NormalizerTemplate):
        pass  # normalizeData() não implementado

    with pytest.raises(TypeError, match=r"(?i)abstract|normalizeData"):
        IncompleteNormalizer()


# ---------------------------------------------------------------------------
# AC2: Subclasse de NormalizerTemplate com normalizeData() satisfaz isinstance(obj, Normalizer)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_complete_normalizer_template_subclass_satisfies_normalizer_protocol():
    """
    AC: Given uma classe que herda de NormalizerTemplate e implementa normalizeData()
        When instancio e verifico isinstance(obj, Normalizer)
        Then retorna True
    """
    class ConcreteNormalizer(NormalizerTemplate):
        def normalizeData(self, decoded_payload):
            return decoded_payload

    obj = ConcreteNormalizer()
    assert isinstance(obj, Normalizer), (
        "ConcreteNormalizer(NormalizerTemplate) com normalizeData() implementado "
        "não satisfaz isinstance(obj, Normalizer)."
    )


# ---------------------------------------------------------------------------
# AC3: Subclasse de ValidatorTemplate com validate() satisfaz isinstance(obj, Validator)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_complete_validator_template_subclass_satisfies_validator_protocol():
    """
    AC: Given uma classe que herda de ValidatorTemplate e implementa validate()
        When instancio e verifico isinstance(obj, Validator)
        Then retorna True
    """
    from healthcare_sdk.contracts import ValidationResult

    class ConcreteValidator(ValidatorTemplate):
        def validate(self, decoded_payload):
            return ValidationResult(is_valid=True)

    obj = ConcreteValidator()
    assert isinstance(obj, Validator), (
        "ConcreteValidator(ValidatorTemplate) com validate() implementado "
        "não satisfaz isinstance(obj, Validator)."
    )


# ---------------------------------------------------------------------------
# AC4: NormalizerTemplate expõe self.aiHelper = None por padrão
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_normalizer_template_has_ai_helper_none_by_default():
    """
    AC: Given NormalizerTemplate com atributo self.aiHelper
        When instancio qualquer subclasse de NormalizerTemplate
        Then self.aiHelper existe e é None por padrão, podendo ser atribuído externamente
    """
    class ConcreteNormalizer(NormalizerTemplate):
        def normalizeData(self, decoded_payload):
            return decoded_payload

    obj = ConcreteNormalizer()

    assert hasattr(obj, "aiHelper"), (
        "NormalizerTemplate não expõe self.aiHelper — o atributo deve ser definido no __init__."
    )
    assert obj.aiHelper is None, (
        f"self.aiHelper deveria ser None por padrão, mas é {obj.aiHelper!r}."
    )

    # Confirma que pode ser atribuído externamente
    class FakeAiHelper:
        def generateResponse(self, prompt: str) -> str:
            return "ok"

    fake_ai = FakeAiHelper()
    obj.aiHelper = fake_ai
    assert obj.aiHelper is fake_ai, "self.aiHelper deve aceitar atribuição externa."


# ---------------------------------------------------------------------------
# Regressão: ValidatorTemplate sem validate() também lança TypeError
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_validator_template_subclass_without_method_raises_type_error():
    """
    Regressão: ValidatorTemplate também deve forçar implementação de validate().
    """
    class IncompleteValidator(ValidatorTemplate):
        pass  # validate() não implementado

    with pytest.raises(TypeError, match=r"(?i)abstract|validate"):
        IncompleteValidator()
