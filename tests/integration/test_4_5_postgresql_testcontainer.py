"""
ATDD — Story 4.5: Integração PostgreSQL validada com testcontainer em CI

Story: Epic 4 / Story 4.5
Acceptance Criteria cobertos: todos os 3 ACs da Story 4.5
Marker: p2 — executa em nightly/CI (requer Docker)

Estes testes iniciam um container PostgreSQL real via testcontainers,
verificam que todas as tabelas são criadas e que o CRUD do PostgreSqlStorage
funciona contra um banco real. O container é destruído automaticamente ao final.

Os testes são pulados automaticamente se o Docker não estiver disponível.
"""
import pytest

# ---------------------------------------------------------------------------
# Skip se Docker não estiver disponível
# ---------------------------------------------------------------------------

def _docker_available() -> bool:
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.p2

requires_docker = pytest.mark.skipif(
    not _docker_available(),
    reason="Docker não disponível — testes de integração requerem Docker em execução",
)


# ---------------------------------------------------------------------------
# Fixture: PostgreSQL via testcontainer (escopo de módulo para performance)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pg_engine():
    """Inicia um container PostgreSQL real, cria as tabelas e retorna o engine."""
    from testcontainers.postgres import PostgresContainer
    from sqlalchemy import create_engine
    from healthcare_sdk.repositories import Base

    with PostgresContainer("postgres:15-alpine") as pg:
        engine = create_engine(pg.get_connection_url())
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)


@pytest.fixture
def pg_storage(pg_engine):
    from healthcare_sdk.repositories.postgreSqlStorage import PostgreSqlStorage
    return PostgreSqlStorage(engine=pg_engine)


@pytest.fixture
def pg_envelope():
    from healthcare_sdk.contracts import RawMessage, MessageEnvelope, STATUS_STORED, ErrorDetail
    raw = RawMessage(id="pg-test-01", protocol="hl7v2", raw_payload=b"MSH|...", message_type="ADT")
    env = MessageEnvelope.from_raw_message(raw)
    env.status = STATUS_STORED
    env.errors = [ErrorDetail(code="I001", message="Info log", stage="normalize")]
    return env


# ---------------------------------------------------------------------------
# AC1: Container PostgreSQL iniciado, testes executados, container destruído ao final
#      (verificado pela própria execução dos testes com o fixture de escopo module)
# ---------------------------------------------------------------------------

@requires_docker
def test_postgresql_container_starts_and_accepts_connections(pg_engine):
    """
    AC: Given testcontainers-python configurado no pyproject.toml
        When executo pytest tests/integration/ -m p2 no ambiente CI
        Then um container PostgreSQL é iniciado automaticamente,
             os testes rodam e o container é destruído ao final
    """
    from sqlalchemy import text
    with pg_engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()

    assert version is not None
    assert "PostgreSQL" in version, f"Versão inesperada: {version}"


# ---------------------------------------------------------------------------
# AC2: save, read, update, delete funcionam contra PostgreSQL real
# ---------------------------------------------------------------------------

@requires_docker
def test_save_read_update_delete_against_real_postgresql(pg_storage, pg_envelope):
    """
    AC: Given o PostgreSqlStorage conectado ao PostgreSQL via testcontainer
        When executo as operações save, read, update, delete
        Then todas retornam os resultados esperados com dados persistidos no PostgreSQL real
    """
    # Save
    log_id = pg_storage.save(pg_envelope)
    assert log_id is not None and isinstance(log_id, str)

    # Read
    record = pg_storage.read({"id": log_id})
    assert record is not None and record != {}
    assert record["protocol"] == "hl7v2"
    assert record["status"] == "stored"

    # Update
    updated = pg_storage.update({"id": log_id}, {"status": "archived"})
    assert updated is True
    refreshed = pg_storage.read({"id": log_id})
    assert refreshed["status"] == "archived"

    # Delete
    deleted = pg_storage.delete({"id": log_id})
    assert deleted is True
    gone = pg_storage.read({"id": log_id})
    assert gone == {} or gone is None


# ---------------------------------------------------------------------------
# AC3: Base.metadata.create_all() cria message_log no PostgreSQL real
# ---------------------------------------------------------------------------

@requires_docker
def test_base_metadata_creates_message_log_in_postgresql(pg_engine):
    """
    AC: Given o testcontainer PostgreSQL em execução
        When chamo Base.metadata.create_all(engine)
        Then todas as tabelas (incluindo message_log) são criadas corretamente no PostgreSQL
    """
    from sqlalchemy import inspect as sa_inspect

    inspector = sa_inspect(pg_engine)
    tables = inspector.get_table_names()

    assert "message_log" in tables, (
        f"Tabela 'message_log' não foi criada no PostgreSQL. Tabelas: {tables}"
    )

    columns = {col["name"] for col in inspector.get_columns("message_log")}
    required = {"id", "protocol", "status", "created_at", "updated_at", "errors"}
    assert required.issubset(columns), (
        f"Campos obrigatórios faltando no PostgreSQL: {required - columns}"
    )
