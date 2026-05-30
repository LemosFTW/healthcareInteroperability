"""
ATDD — Story 1.3: Validar RestController com testes de integração

Story: Epic 1 / Story 1.3
Acceptance Criteria cobertos: todos os 4 ACs da Story 1.3
"""
import pytest
from fastapi.testclient import TestClient
from healthcare_sdk.transportLayer.restController import RestController


# ---------------------------------------------------------------------------
# Fixture compartilhada
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    controller = RestController()
    return TestClient(controller.app)


# ---------------------------------------------------------------------------
# AC1: GET /health retorna HTTP 200 com body {"status": "ok"}
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_health_endpoint_returns_200_and_ok(client):
    """
    AC: Given um RestController instanciado com httpx.TestClient
        When faço GET em /health
        Then recebo HTTP 200 com body {"status": "ok"}
    """
    response = client.get("/health")

    assert response.status_code == 200, (
        f"GET /health retornou {response.status_code}, esperado 200. Body: {response.text}"
    )
    assert response.json() == {"status": "ok"}, (
        f"Body inesperado: {response.json()}"
    )


# ---------------------------------------------------------------------------
# AC2: GET /ping com rota GET registrada retorna resposta do handler
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_registered_get_route_returns_handler_response():
    """
    AC: Given um RestController com uma rota GET registrada via add_endpoint("/ping", "get", handler)
        When faço GET em /ping
        Then recebo a resposta definida pelo handler
    """
    controller = RestController()

    async def ping_handler():
        return {"pong": True}

    controller.add_endpoint("/ping", "get", ping_handler)
    client = TestClient(controller.app)

    response = client.get("/ping")

    assert response.status_code == 200, (
        f"GET /ping retornou {response.status_code}. Body: {response.text}"
    )
    assert response.json() == {"pong": True}, (
        f"Resposta inesperada: {response.json()}"
    )


# ---------------------------------------------------------------------------
# AC3: POST /echo com rota POST registrada recebe payload e retorna resposta
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_registered_post_route_receives_payload_and_returns_response():
    """
    AC: Given um RestController com uma rota POST registrada via add_endpoint("/echo", "post", handler)
        When faço POST em /echo com um payload JSON
        Then o handler recebe o payload e retorna a resposta esperada
    """
    from fastapi import Request

    controller = RestController()

    async def echo_handler(request: Request):
        body = await request.json()
        return {"echoed": body}

    controller.add_endpoint("/echo", "post", echo_handler)
    client = TestClient(controller.app)

    payload = {"message": "hello", "value": 42}
    response = client.post("/echo", json=payload)

    assert response.status_code == 200, (
        f"POST /echo retornou {response.status_code}. Body: {response.text}"
    )
    assert response.json() == {"echoed": payload}, (
        f"Resposta inesperada: {response.json()}"
    )


# ---------------------------------------------------------------------------
# AC4: add_endpoint() com método HTTP inválido lança ValueError descritivo
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_invalid_http_method_raises_value_error_with_descriptive_message():
    """
    AC: Given add_endpoint() chamado com método HTTP inválido (ex: "patch_invalido")
        When o método não é suportado
        Then ValueError é lançado com mensagem descritiva
    """
    controller = RestController()

    async def dummy():
        return {}

    with pytest.raises(ValueError, match=r"(?i)method|metodo|invalido|unsupported"):
        controller.add_endpoint("/test", "patch_invalido", dummy)
