"""
ATDD — Story 4.6: Verificar conformidade com Clean Architecture

Story: Epic 4 / Story 4.6
Acceptance Criteria cobertos: todos os 4 ACs da Story 4.6

Implementa um verificador de arquitetura baseado em AST que detecta violações
de dependência entre as camadas do SDK sem depender de ferramentas externas.

Regras documentadas em pyproject.toml ([tool.importlinter.contracts]).
Dependency direction (inner → outer):
  contracts → tools → usecases → repositories
                                → transportLayer
  errors: utility layer, importável por todos
  sdk.py: composition root, pode importar tudo

Violations detectadas:
  - tools importando de repositories, usecases ou transportLayer
  - contracts importando de qualquer camada SDK
  - usecases importando de repositories ou transportLayer
  - transportLayer importando de repositories
"""
import ast
import textwrap
import pytest
from pathlib import Path
from typing import List, NamedTuple


# ---------------------------------------------------------------------------
# Verificador de arquitetura baseado em AST
# ---------------------------------------------------------------------------

SDK_ROOT = Path(__file__).parent.parent.parent / "src" / "healthcare_sdk"

SDK_PACKAGE = "healthcare_sdk"

# Regras: camada → módulos que ela NÃO pode importar
FORBIDDEN_RULES: dict[str, list[str]] = {
    "contracts": [
        "healthcare_sdk.tools",
        "healthcare_sdk.usecases",
        "healthcare_sdk.repositories",
        "healthcare_sdk.transportLayer",
    ],
    "tools": [
        "healthcare_sdk.usecases",
        "healthcare_sdk.repositories",
        "healthcare_sdk.transportLayer",
    ],
    "usecases": [
        "healthcare_sdk.repositories",
        "healthcare_sdk.transportLayer",
    ],
    "transportLayer": [
        "healthcare_sdk.repositories",
    ],
}

# sdk.py and errors.py are excluded (composition root and utility)
EXCLUDED_FILES = {"sdk.py", "app.py"}


class Violation(NamedTuple):
    file: str
    line: int
    imported: str
    rule: str


def _get_imports(filepath: Path) -> list[tuple[int, str]]:
    """Return (lineno, module_name) for all imports in a Python file."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # Resolve relative imports by computing absolute name
                if node.level and node.level > 0:
                    # relative import: figure out the package
                    rel_parts = filepath.relative_to(SDK_ROOT)
                    pkg_parts = list(rel_parts.parts[:-node.level])
                    absolute = ".".join([SDK_PACKAGE] + pkg_parts + [node.module]) if pkg_parts else f"{SDK_PACKAGE}.{node.module}"
                    results.append((node.lineno, absolute))
                else:
                    results.append((node.lineno, node.module))
    return results


def _layer_of(filepath: Path, source_root: Path) -> str | None:
    """Return the layer name (folder) of a source file, or None if not in a layer."""
    try:
        rel = filepath.relative_to(source_root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) == 1:
        return None  # top-level file (sdk.py, contracts.py, errors.py, app.py)
    return parts[0]  # 'tools', 'usecases', 'repositories', 'transportLayer'


def _check_file(filepath: Path, source_root: Path) -> list[Violation]:
    if filepath.name in EXCLUDED_FILES:
        return []
    layer = _layer_of(filepath, source_root)
    # For top-level files named contracts.py treat them as their own layer
    if layer is None:
        stem = filepath.stem
        if stem == "contracts":
            layer = "contracts"
        else:
            return []  # errors.py, __init__.py etc. — skip
    rules = FORBIDDEN_RULES.get(layer, [])
    if not rules:
        return []
    violations = []
    for lineno, imported in _get_imports(filepath):
        for forbidden in rules:
            if imported == forbidden or imported.startswith(forbidden + "."):
                try:
                    rel = str(filepath.relative_to(source_root.parent))
                except ValueError:
                    rel = str(filepath)
                violations.append(Violation(file=rel, line=lineno, imported=imported, rule=f"{layer} must not import {forbidden}"))
    return violations


def check_architecture(source_root: Path = SDK_ROOT) -> list[Violation]:
    """Scan all .py files and return architecture violations."""
    violations = []
    for py_file in source_root.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        violations.extend(_check_file(py_file, source_root))
    return violations


# ---------------------------------------------------------------------------
# AC1 + AC4: Nenhuma violação no código atual — relatório confirma conformidade
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_current_codebase_has_no_architecture_violations():
    """
    AC: Given as regras de dependência definidas: contracts ← tools ← usecases ← repositories ← transportLayer
        When executo a verificação de imports
        Then nenhuma violação é encontrada
    """
    violations = check_architecture()

    if violations:
        report = "\n".join(f"  {v.file}:{v.line} — {v.imported!r} violates: {v.rule}" for v in violations)
        pytest.fail(f"Violações de arquitetura detectadas:\n{report}")


@pytest.mark.p0
def test_all_sdk_modules_verified_and_report_confirms_compliance():
    """
    AC: Given todos os módulos de src/healthcare_sdk/ verificados
        When nenhuma violação existe
        Then o teste passa e o relatório confirma conformidade com Clean Architecture
    """
    py_files = [f for f in SDK_ROOT.rglob("*.py") if "__pycache__" not in f.parts]
    assert len(py_files) > 0, "Nenhum arquivo .py encontrado em src/healthcare_sdk/"

    violations = check_architecture()
    assert violations == [], (
        f"{len(violations)} violação(ões) encontrada(s). "
        "O relatório acima contém os detalhes."
    )


# ---------------------------------------------------------------------------
# AC2: Violação intencional é detectada com arquivo e linha de origem
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_intentional_violation_in_tools_layer_is_detected(tmp_path):
    """
    AC: Given uma violação intencional introduzida (ex: tools/decoder.py importando de repositories/)
        When executo a verificação de imports
        Then o teste falha indicando a violação com o arquivo e linha de origem
    """
    # Create a synthetic tools/ file with a forbidden import
    tools_dir = tmp_path / "healthcare_sdk" / "tools"
    tools_dir.mkdir(parents=True)
    violating_file = tools_dir / "bad_decoder.py"
    violating_file.write_text(textwrap.dedent("""\
        from healthcare_sdk.repositories import PostgreSqlStorage  # VIOLATION
        from healthcare_sdk.contracts import RawMessage            # OK

        class BadDecoder:
            def decode(self, raw_message):
                return {}
    """), encoding="utf-8")

    synthetic_root = tmp_path / "healthcare_sdk"
    violations = check_architecture(source_root=synthetic_root)

    assert len(violations) >= 1, (
        "A violação intencional em tools/bad_decoder.py não foi detectada. "
        "O verificador de arquitetura deve detectar imports proibidos."
    )

    repository_violations = [v for v in violations if "repositories" in v.imported]
    assert repository_violations, (
        f"Violação de repositories não encontrada. Violações detectadas: {violations}"
    )
    assert repository_violations[0].line == 1, (
        f"Número de linha incorreto: esperado 1, got {repository_violations[0].line}"
    )


# ---------------------------------------------------------------------------
# AC3: Regras documentadas em pyproject.toml sob [tool.importlinter.contracts]
# ---------------------------------------------------------------------------

@pytest.mark.p0
def test_architecture_rules_documented_in_pyproject_toml():
    """
    AC: Given as regras de arquitetura documentadas em pyproject.toml ou arquivo de configuração
        When um novo desenvolvedor adiciona um import que viola a arquitetura
        Then o teste de arquitetura falha no PR antes do merge

    Verifica que a seção [tool.importlinter] existe no pyproject.toml com as regras definidas.
    """
    pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    assert "[tool.importlinter]" in content, (
        "pyproject.toml não contém seção [tool.importlinter]. "
        "As regras de arquitetura devem ser documentadas lá."
    )
    assert "forbidden" in content, (
        "Nenhuma regra 'forbidden' encontrada em [tool.importlinter]. "
        "Configure contratos de dependência proibida."
    )
    # Verifica que as camadas principais estão cobertas
    for layer in ("tools", "usecases", "transportLayer"):
        assert layer in content, (
            f"Camada '{layer}' não referenciada nas regras de arquitetura do pyproject.toml."
        )
