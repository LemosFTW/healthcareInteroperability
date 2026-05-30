"""
ATDD — Story 1.4: Verificar extensibilidade do contrato Adapter

Story: Epic 1 / Story 1.4
Acceptance Criteria cobertos: todos os 3 ACs da Story 1.4

Verifica que o contrato Adapter é um Protocol runtime_checkable,
permitindo implementações externas sem herança do framework.
"""
import pytest
from healthcare_sdk.transportLayer.adapter import Adapter
from healthcare_sdk.contracts import RawMessage
from healthcare_sdk.sdk import register_components, ComponentRegistrationError


# ---------------------------------------------------------------------------
# Implementações externas (simulam código do implementador fora de healthcare_sdk)
# ---------------------------------------------------------------------------

class FakeMllpAdapter:
    """Adapter MLLP externo — implementa executeServer() e receive() sem herdar do framework."""

    def executeServer(self, port: int = 2575):
        pass

    def receive(self) -> RawMessage:
        return RawMessage(id="mllp-1", protocol="mllp", raw_payload=b"MSH|...")


class AdapterMissingReceive:
    """Implementação incompleta — só possui executeServer(), sem receive()."""

    def executeServer(self, port: int = 8000):
        pass


# ---------------------------------------------------------------------------
# AC1: FakeMllpAdapter externo satisfaz isinstance(obj, Adapter) sem herança
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_external_adapter_satisfies_protocol_without_inheritance():
    """
    AC: Given uma classe FakeMllpAdapter que implementa executeServer() e receive()
            fora do pacote healthcare_sdk
        When verifico isinstance(FakeMllpAdapter(), Adapter)
        Then retorna True sem precisar herdar de nenhuma classe do framework
    """
    adapter = FakeMllpAdapter()

    assert not issubclass(FakeMllpAdapter, object.__class__) or True, "sanity"
    # Confirma que não herda de Adapter diretamente
    assert Adapter not in FakeMllpAdapter.__bases__, (
        "FakeMllpAdapter não deveria herdar explicitamente de Adapter para este teste"
    )
    assert isinstance(adapter, Adapter), (
        "FakeMllpAdapter implementa executeServer() e receive() mas isinstance() retornou False. "
        "Verifique se Adapter está decorado com @runtime_checkable."
    )


# ---------------------------------------------------------------------------
# AC2: FakeMllpAdapter válido é aceito por register_components() sem exceção
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_valid_external_adapter_accepted_by_register_components():
    """
    AC: Given um FakeMllpAdapter válido criado externamente
        When passo para register_components(adapters=[FakeMllpAdapter()])
        Then é aceito sem ComponentRegistrationError
    """
    adapter = FakeMllpAdapter()

    try:
        result = register_components(adapters=[adapter])
    except ComponentRegistrationError as exc:
        pytest.fail(
            f"register_components() rejeitou FakeMllpAdapter válido: {exc}"
        )

    assert len(result.adapters) == 1
    assert result.adapters[0] is adapter


# ---------------------------------------------------------------------------
# AC3: Classe sem receive() retorna False em isinstance(obj, Adapter)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_incomplete_adapter_fails_isinstance_check():
    """
    AC: Given uma classe que implementa apenas executeServer() mas não receive()
        When verifico isinstance(obj, Adapter)
        Then retorna False, confirmando que o contrato é verificado corretamente
    """
    incomplete = AdapterMissingReceive()

    assert not isinstance(incomplete, Adapter), (
        "AdapterMissingReceive não implementa receive() mas isinstance() retornou True. "
        "O Protocol Adapter deve exigir ambos executeServer() e receive()."
    )


@pytest.mark.p0
def test_incomplete_adapter_rejected_by_register_components():
    """
    AC derivado: incompleteAdapter sem receive() lança ComponentRegistrationError em register_components()
    """
    incomplete = AdapterMissingReceive()

    with pytest.raises(ComponentRegistrationError):
        register_components(adapters=[incomplete])
