# BizIntel AI

BizIntel AI is an evidence-backed business analytics platform. The current local-demo slice provides deterministic KPI calculations, conservative SQL validation, workspace-isolated TXT/CSV ingestion, lexical evidence retrieval, bounded single/supervisor workflow modes, an auditable investigation report API, and a React investigation workspace.

## Current status

The workspace was empty when implementation began. PostgreSQL, Docker, Ollama, and Python web dependencies are not currently installed or available in this environment. The application dependency contract is defined in `pyproject.toml`. Local demo storage is intentionally in-memory and must be replaced with PostgreSQL/pgvector before production use.

## Local setup (PowerShell)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
uvicorn apps.api.main:app --reload
pytest
```

`npm.cmd` can be used rather than `npm` on this machine because PowerShell script execution blocks `npm.ps1`.

Run the web client in a second PowerShell window:

```powershell
Set-Location apps\web
npm.cmd install
npm.cmd run dev
```

## Safety baseline

The analytics SQL guard accepts a single read-only `SELECT` or `WITH` statement only. It is a first-line policy check, not a replacement for the dedicated database role planned for Phase 1 database provisioning.
