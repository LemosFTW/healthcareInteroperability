"""
ATDD — Story 2.3: Registrar componentes válidos e rejeitar inválidos via register_components()

Story: Epic 2 / Story 2.3
Acceptance Criteria cobertos: todos os 4 ACs da Story 2.3
"""
import pytest
from healthcare_sdk.sdk import register_components, SdkComponents, ComponentRegistrationError
from healthcare_sdk.contracts import RawMessage, MessageEnvelope, ValidationResult


# ---------------------------------------------------------------------------
# Implementações válidas (satisfazem todos os Protocols)
# ---------------------------------------------------------------------------

class ValidAdapter:
    def executeServer(self, port: int = 8000):
        pass
    def receive(self) -> RawMessage:
        return RawMessage(id="1", protocol="rest", raw_payload=b"")


class ValidDecoder:
    def decode(self, raw_message: RawMessage) -> dict:
        return {}


class ValidValidator:
    def validate(self, decoded_payload: dict) -> ValidationResult:
        return ValidationResult(is_valid=True)


class ValidNormalizer:
    def normalizeData(self, decoded_payload: dict) -> dict:
        return decoded_payload


class ValidAiHelper:
    def generateResponse(self, prompt: str) -> str:
        return "ok"


class ValidStorage:
    def save(self, envelope) -> str:
        return "id-1"
    def connection(self):
        return None
    def read(self, query: dict) -> dict:
        return {}
    def delete(self, query: dict) -> bool:
        return True
    def update(self, query: dict, data: dict) -> bool:
        return True


class ValidUsecase:
    def execute(self, raw_message: RawMessage) -> MessageEnvelope:
        return MessageEnvelope(
            id="1", protocol="rest", message_type="test", raw_payload=b""
        )


# ---------------------------------------------------------------------------
# Implementações inválidas
# ---------------------------------------------------------------------------

class InvalidAdapter:
    """Não implementa executeServer() nem receive()."""
    pass


class InvalidDecoder:
    """Não implementa decode()."""
    pass


class EmptyClass:
    pass


# ---------------------------------------------------------------------------
# AC1: Conjunto completo de componentes válidos é aceito e retorna SdkComponents
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_valid_components_are_accepted_and_return_sdk_components():
    """
    AC: Given um conjunto de componentes válidos (implementam corretamente todos os Protocols)
        When chamo register_components(adapters=[...], decoders=[...], ...)
        Then retorna um objeto SdkComponents sem lançar exceção
    """
    result = register_components(
        adapters=[ValidAdapter()],
        decoders=[ValidDecoder()],
        validators=[ValidValidator()],
        normalizers=[ValidNormalizer()],
        aihelpers=[ValidAiHelper()],
        storages=[ValidStorage()],
        usecases=[ValidUsecase()],
    )

    assert isinstance(result, SdkComponents), (
        f"register_components() deveria retornar SdkComponents, retornou {type(result)}"
    )
    assert len(result.adapters) == 1
    assert len(result.decoders) == 1
    assert len(result.validators) == 1
    assert len(result.normalizers) == 1
    assert len(result.storages) == 1


# ---------------------------------------------------------------------------
# AC2: Adapter inválido lança ComponentRegistrationError com mensagem identificando o componente
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_invalid_adapter_raises_component_registration_error():
    """
    AC: Given um adapter que não implementa executeServer() ou receive()
        When passo para register_components(adapters=[invalid_adapter])
        Then ComponentRegistrationError é lançado com mensagem identificando o componente inválido
    """
    with pytest.raises(ComponentRegistrationError) as exc_info:
        register_components(adapters=[InvalidAdapter()])

    error_msg = str(exc_info.value).lower()
    assert "adapter" in error_msg, (
        f"Mensagem de erro deveria mencionar 'adapter', mas foi: {exc_info.value!r}"
    )


# ---------------------------------------------------------------------------
# AC3: Decoder inválido lança ComponentRegistrationError
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_invalid_decoder_raises_component_registration_error():
    """
    AC: Given um decoder que não implementa decode()
        When passo para register_components(decoders=[invalid_decoder])
        Then ComponentRegistrationError é lançado
    """
    with pytest.raises(ComponentRegistrationError):
        register_components(decoders=[InvalidDecoder()])


# ---------------------------------------------------------------------------
# AC4: Listas vazias para componentes opcionais são aceitas sem erro
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_empty_optional_lists_are_accepted_without_error():
    """
    AC: Given register_components() chamado com listas vazias para componentes opcionais
        When pelo menos os componentes obrigatórios são válidos
        Then o registro é aceito sem erro

    Todos os parâmetros são opcionais em register_components(), então uma chamada
    completamente vazia também deve ser aceita.
    """
    result = register_components()

    assert isinstance(result, SdkComponents)
    assert result.adapters == []
    assert result.decoders == []
    assert result.validators == []
    assert result.normalizers == []
    assert result.storages == []


@pytest.mark.p0
def test_partial_valid_components_with_empty_optionals_accepted():
    """
    AC derivado: apenas um subset de tipos registrados, restante vazio — aceito sem erro.
    """
    result = register_components(
        adapters=[ValidAdapter()],
        decoders=[ValidDecoder()],
    )

    assert len(result.adapters) == 1
    assert len(result.decoders) == 1
    assert result.validators == []
    assert result.normalizers == []
