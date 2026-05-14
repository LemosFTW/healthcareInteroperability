# HealthCare Interoperability framework

Small SDK project to host interoperability services and adapters.

## Folder Architecture

```text
documentation/
└─ frameworkClassDiagram.png
src/
└─ healthcare_sdk/
   ├─ app.py
   ├─ __init__.py
   ├─ transportLayer/
   │  ├─ adapter.py
   │  ├─ restController.py
   │  └─ __init__.py
   ├─ repositories/
   │  ├─ postgreSqlStorage.py
   │  ├─ storage.py
   │  └─ __init__.py
   ├─ usecases/
   │  ├─ healthCareUsecase.py
   │  └─ __init__.py
   └─ tools/
      ├─ aiHelper.py
      ├─ decoder.py
      ├─ normalizer.py
      ├─ validator.py
      └─ __init__.py
```

## Proposed Class Diagram

![Framework class diagram](documentation/frameworkClassDiagram.png)

Folder responsibilities:

- transportLayer/: Transport adapters and server launchers (e.g., REST, HL7 over MLLP). 
- repositories/: Database providers and external data sources used by implementations.
- usecases/: Application use cases and orchestration logic.
- tools/: Shared helpers for decoding, validation, and normalization.

## Setup (uv)

```powershell
uv venv
uv add fastapi uvicorn
```

## Run

```powershell
$env:PYTHONPATH = "src"
python -m healthcare_sdk.app
```

Then open: http://127.0.0.1:8000/health
