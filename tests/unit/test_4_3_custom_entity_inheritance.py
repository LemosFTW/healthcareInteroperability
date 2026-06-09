"""
ATDD — Story 4.3: Implementador define entidade customizada herdando Base

Story: Epic 4 / Story 4.3
Acceptance Criteria cobertos: todos os 3 ACs da Story 4.3

Verifica que implementadores podem criar entidades de domínio herdando Base do framework,
coexistindo com MessageLog sem conflito e sem modificar nenhum arquivo em src/healthcare_sdk/.

A classe PatientRecord é definida aqui dentro do arquivo de teste, simulando código
que pertenceria ao repositório do implementador — completamente fora de healthcare_sdk.
"""
import uuid
import pytest
from sqlalchemy import create_engine, inspect, String
from sqlalchemy.orm import Session, Mapped, mapped_column

from healthcare_sdk.repositories import Base
from healthcare_sdk.repositories.messageLog import MessageLog
from healthcare_sdk.contracts import RawMessage, MessageEnvelope, STATUS_STORED


# ---------------------------------------------------------------------------
# Entidade customizada definida FORA do pacote healthcare_sdk
# (simula o repositório do implementador)
# ---------------------------------------------------------------------------

class PatientRecord(Base):
    """Entidade de domínio do implementador — definida fora de healthcare_sdk."""
    __tablename__ = "patient_record"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    birth_date: Mapped[str] = mapped_column(String, nullable=True)
    medical_record_number: Mapped[str] = mapped_column(String, nullable=True)


# ---------------------------------------------------------------------------
# Fixture: engine isolado por teste (cria + destrói tabelas)
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


# ---------------------------------------------------------------------------
# AC1: Base.metadata.create_all() cria AMBAS as tabelas — message_log E patient_record
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_both_message_log_and_patient_record_tables_created(engine):
    """
    AC: Given uma classe PatientRecord(Base) definida fora do pacote healthcare_sdk
        When executo Base.metadata.create_all(engine)
        Then tanto a tabela message_log quanto a tabela patient_record são criadas sem erro
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "message_log" in tables, (
        f"Tabela 'message_log' não foi criada. Tabelas: {tables}"
    )
    assert "patient_record" in tables, (
        f"Tabela 'patient_record' não foi criada. Tabelas: {tables}"
    )


# ---------------------------------------------------------------------------
# AC2: PatientRecord é persistido e lido corretamente sem interferir no MessageLog
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_custom_entity_persisted_and_read_without_message_log_interference(engine):
    """
    AC: Given a entidade customizada criada com campos próprios
        When persisto e leio um registro via sessão SQLAlchemy
        Then os dados são recuperados corretamente sem interferência do MessageLog
    """
    patient_id = str(uuid.uuid4())

    # Persist a PatientRecord
    with Session(engine) as session:
        patient = PatientRecord(
            id=patient_id,
            name="João da Silva",
            birth_date="1985-03-15",
            medical_record_number="MRN-12345",
        )
        session.add(patient)
        session.commit()

    # Also persist a MessageLog to prove there's no interference
    raw = RawMessage(id="env-x01", protocol="hl7v2", raw_payload=b"MSH|...", message_type="ADT")
    envelope = MessageEnvelope.from_raw_message(raw)
    envelope.status = STATUS_STORED
    with Session(engine) as session:
        log = MessageLog.from_envelope(envelope)
        session.add(log)
        session.commit()

    # Read the PatientRecord back and verify data integrity
    with Session(engine) as session:
        retrieved = session.get(PatientRecord, patient_id)

    assert retrieved is not None, "PatientRecord não foi encontrado após persistência"
    assert retrieved.name == "João da Silva"
    assert retrieved.birth_date == "1985-03-15"
    assert retrieved.medical_record_number == "MRN-12345"

    # Verify the MessageLog wasn't corrupted
    with Session(engine) as session:
        from sqlalchemy import select
        count = session.execute(select(MessageLog)).scalars().all()
    assert len(count) == 1, "MessageLog não deveria ser afetado pela operação em PatientRecord"


# ---------------------------------------------------------------------------
# AC3: Nenhum arquivo em src/healthcare_sdk/ referencia PatientRecord
# ---------------------------------------------------------------------------

@pytest.mark.p1
def test_healthcare_sdk_source_files_do_not_reference_patient_record():
    """
    AC: Given o framework sem nenhuma referência à entidade customizada do implementador
        When o implementador adiciona sua entidade em seu repositório separado
        Then nenhum arquivo dentro de src/healthcare_sdk/ precisa ser modificado

    Verifica estaticamente que não há referência a 'PatientRecord' ou 'patient_record'
    em nenhum arquivo de src/healthcare_sdk/.
    """
    import os
    from pathlib import Path

    sdk_src = Path(__file__).parent.parent.parent / "src" / "healthcare_sdk"
    violations = []

    for py_file in sdk_src.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        if "PatientRecord" in content or "patient_record" in content:
            violations.append(str(py_file.relative_to(sdk_src.parent.parent)))

    assert not violations, (
        f"Arquivos do SDK referenciam a entidade customizada do implementador: {violations}. "
        "O framework não deve conhecer entidades externas."
    )
