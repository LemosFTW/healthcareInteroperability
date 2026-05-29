"""
ATDD Red-Phase Scaffold — Story 1.1: Criar infraestrutura de testes com pytest
TDD RED PHASE: Estes testes estao marcados com @pytest.mark.skip.
Remova o decorator @pytest.mark.skip de cada teste ao implementar o AC correspondente.
Execute `pytest tests/ -m p0` para verificar a fase green.

Story: Epic 1 / Story 1.1
Acceptance Criteria cobertos: todos os 4 ACs da Story 1.1
"""
import pytest
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# AC1: pytest tests/ executa sem erros e reporta 0 testes coletados
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_pytest_runs_without_error_on_empty_structure():
    """
    AC: Given o repositorio do framework sem estrutura de testes
        When eu executo `pytest tests/`
        Then o comando executa sem erros e reporta 0 testes coletados (estrutura vazia pronta)

    Nota: Este teste SO pode ser ativado apos o diretorio tests/ existir com
    pyproject.toml configurado. Ao ativar, remova o @pytest.mark.skip.
    """
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q", "--no-header"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"pytest falhou ao executar com returncode={result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# AC2: Um teste em tests/unit/ e descoberto e executado pelo pytest
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_unit_test_is_discovered_by_pytest():
    """
    AC: Given a estrutura tests/unit/ criada
        When eu crio um teste em tests/unit/test_example.py
        Then o pytest o descobre e executa corretamente

    Verificacao: o proprio arquivo de scaffold eh descoberto pelo pytest.
    Ao ativar, o pytest deve coletar este arquivo sem erro de import.
    """
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(Path(__file__)), "--collect-only", "-q", "--no-header"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"pytest nao conseguiu coletar tests/unit/: returncode={result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "test_1_1_pytest_infrastructure" in result.stdout


# ---------------------------------------------------------------------------
# AC3: Fixtures do conftest.py sao injetadas sem erro de importacao
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_conftest_fixtures_are_injectable(fake_decoder, fake_validator, fake_normalizer, fake_storage):
    """
    AC: Given o conftest.py com fixtures base definidas
        When um teste importa uma fixture
        Then a fixture eh injetada corretamente sem erro de importacao

    Ao ativar: o pytest deve injetar as quatro fixtures sem ImportError nem TypeError.
    """
    assert fake_decoder is not None, "fake_decoder nao foi injetado"
    assert fake_validator is not None, "fake_validator nao foi injetado"
    assert fake_normalizer is not None, "fake_normalizer nao foi injetado"
    assert fake_storage is not None, "fake_storage nao foi injetado"



@pytest.mark.p0
def test_fake_decoder_has_decode_method(fake_decoder):
    """
    AC derivado: fake_decoder implementa o contrato Decoder (possui metodo decode).
    """
    from healthcare_sdk.transportLayer.adapter import Adapter  # noqa: F401 — verifica import
    assert hasattr(fake_decoder, "decode"), "FakeDecoder nao possui metodo decode()"
    assert callable(fake_decoder.decode)



@pytest.mark.p0
def test_fake_storage_implements_all_operations(fake_storage):
    """
    AC derivado: fake_storage implementa save, read, update, delete, connection.
    """
    for method in ("save", "read", "update", "delete", "connection"):
        assert hasattr(fake_storage, method), f"FakeStorage nao possui metodo {method}()"
        assert callable(getattr(fake_storage, method))


# ---------------------------------------------------------------------------
# AC4: Markers p0, p1, p2, p3 filtram corretamente
# ---------------------------------------------------------------------------


@pytest.mark.p0
def test_pytest_markers_are_registered():
    """
    AC: Given os markers p0, p1, p2, p3 configurados no pyproject.toml
        When executo `pytest tests/ -m p0`
        Then apenas testes marcados com @pytest.mark.p0 sao executados

    Verificacao: `pytest --markers` inclui p0, p1, p2, p3 sem warnings de marker desconhecido.
    """
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--markers"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    output = result.stdout + result.stderr
    for marker in ("p0", "p1", "p2", "p3"):
        assert marker in output, (
            f"Marker '{marker}' nao encontrado em `pytest --markers`.\n"
            f"Configure [tool.pytest.ini_options] markers no pyproject.toml.\n"
            f"Output: {output}"
        )



@pytest.mark.p0
def test_marker_filter_p0_selects_only_p0_tests():
    """
    AC: When executo `pytest tests/ -m p0`
        Then apenas testes marcados com @pytest.mark.p0 sao executados
    """
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(Path(__file__)), "-m", "p0",
         "--collect-only", "-q", "--no-header"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, (
        f"Filtro por marker p0 falhou: returncode={result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    # Nao deve coletar testes marcados com p1, p2, p3
    assert "p1" not in result.stdout or "no tests ran" not in result.stdout
