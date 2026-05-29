"""
ATDD Red-Phase Scaffold — Story 1.2: Isolar instancias do RestController por teste
TDD RED PHASE: Estes testes estao marcados com @pytest.mark.skip.
Remova o decorator @pytest.mark.skip de cada teste ao implementar o AC correspondente.
Execute `pytest tests/ -m p0 -v` para verificar a fase green.

Story: Epic 1 / Story 1.2
Problema raiz: `app = FastAPI()` no nivel de modulo em restController.py faz com que
todas as instancias de RestController compartilhem o mesmo objeto FastAPI.
Solucao: mover `self.app = FastAPI()` para dentro do `__init__` da classe.

Acceptance Criteria cobertos: todos os 3 ACs da Story 1.2
"""
import pytest


# ---------------------------------------------------------------------------
# AC1: Duas instancias de RestController possuem apps FastAPI independentes
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_two_rest_controller_instances_have_independent_apps():
    """
    AC: Given o RestController com app = FastAPI() movido para dentro do __init__
        When instancio dois RestController() separados
        Then cada um possui seu proprio objeto app FastAPI independente

    Falhara enquanto app = FastAPI() estiver no nivel de modulo (variavel compartilhada).
    """
    from healthcare_sdk.transportLayer.restController import RestController

    controller_a = RestController()
    controller_b = RestController()

    assert controller_a.app is not controller_b.app, (
        "RestController compartilha o mesmo objeto app FastAPI entre instancias. "
        "Mova `self.app = FastAPI()` para dentro do __init__ para isolar instancias."
    )


# ---------------------------------------------------------------------------
# AC2: Rotas de instancias separadas nao se contaminam
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_routes_do_not_cross_pollinate_between_instances():
    """
    AC: Given dois RestController instanciados no mesmo teste
        When adiciono /rota-a no primeiro e /rota-b no segundo via add_endpoint()
        Then o primeiro so tem /rota-a e o segundo so tem /rota-b

    Falhara enquanto os dois controllers compartilharem o mesmo objeto app.
    """
    from healthcare_sdk.transportLayer.restController import RestController

    async def handler_a():
        return {"controller": "a"}

    async def handler_b():
        return {"controller": "b"}

    controller_a = RestController()
    controller_b = RestController()

    controller_a.add_endpoint("/rota-a", "get", handler_a)
    controller_b.add_endpoint("/rota-b", "get", handler_b)

    routes_a = {route.path for route in controller_a.app.routes}
    routes_b = {route.path for route in controller_b.app.routes}

    assert "/rota-a" in routes_a, "controller_a nao possui /rota-a"
    assert "/rota-b" not in routes_a, (
        "controller_a foi contaminado com /rota-b de controller_b — "
        "os dois compartilham o mesmo app FastAPI."
    )
    assert "/rota-b" in routes_b, "controller_b nao possui /rota-b"
    assert "/rota-a" not in routes_b, (
        "controller_b foi contaminado com /rota-a de controller_a — "
        "os dois compartilham o mesmo app FastAPI."
    )


# ---------------------------------------------------------------------------
# AC3: Rota /health retorna 200 apos mover app para __init__
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_health_route_returns_200_after_refactor():
    """
    AC: Given a rota /health que era decorada com @app.get no nivel de modulo
        When instancio um RestController
        Then a rota /health retorna {"status": "ok"} com HTTP 200

    Verifica que mover app para __init__ nao quebra a rota /health.
    Requer httpx instalado: pip install httpx

    Falhara se /health nao for registrada na instancia local do app.
    """
    import httpx
    from fastapi.testclient import TestClient
    from healthcare_sdk.transportLayer.restController import RestController

    controller = RestController()
    client = TestClient(controller.app)

    response = client.get("/health")

    assert response.status_code == 200, (
        f"GET /health retornou {response.status_code}, esperado 200. "
        f"Body: {response.text}"
    )
    assert response.json() == {"status": "ok"}, (
        f"Body inesperado: {response.json()}"
    )


# ---------------------------------------------------------------------------
# Teste de regressao: add_endpoint() com metodo invalido lanca ValueError
# (Derivado do AC da Story 1.3 — incluido aqui para cobrir o contrato de erro)
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_add_endpoint_with_invalid_method_raises_value_error():
    """
    AC (Story 1.3 derivado): Given add_endpoint() chamado com metodo HTTP invalido
        When o metodo nao e suportado
        Then ValueError e lancado com mensagem descritiva
    """
    from healthcare_sdk.transportLayer.restController import RestController

    controller = RestController()

    async def dummy_handler():
        return {}

    with pytest.raises(ValueError, match=r"(?i)method|metodo|invalido|unsupported"):
        controller.add_endpoint("/test", "patch_invalido", dummy_handler)
