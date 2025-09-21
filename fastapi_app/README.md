"* 2025-08-08: 重构并优化了 FastAPI 服务的启动流程，修复了多个弃用警告，并增强了 WebSocket 的日志监控能力。" 
* 2025-08-08: 为 FastAPI 应用配置 CORS，允许来自 `http://localhost:19100` 的跨源请求。
FastAPI helpers for Windows PowerShell

This folder contains small PowerShell helper scripts to create a local virtual
environment and run the API or Web UI on Windows.

Scripts:

- `start_api.ps1` — create/activate `.venv`, install `requirements.txt`, and start FastAPI (uvicorn).
- `start_webui.ps1` — create/activate `.venv`, install `requirements.txt`, and run `webui.py`.
- `start_all.ps1` — run both `start_api.ps1` and `start_webui.ps1` as background jobs.

Usage:

```powershell
cd fastapi_app
.\start_api.ps1
# or
.\start_webui.ps1
```

Notes:
- The scripts will create a `.venv` directory at the repository root if one
	does not exist and will attempt to install packages listed in `requirements.txt`.
- For a reproducible environment, consider using `requirements-lock.txt` after
	creating the venv.

Additional helper for full environment (Python 3.11)

If you want a venv that matches the original pinned environment (including `numba`), use the repository-level helper:

```powershell
.\scripts\setup_venv_py311.ps1
# or pass a specific interpreter path:
.\scripts\setup_venv_py311.ps1 -PythonCmd 'C:\\Program Files\\Python311\\python.exe'
```

This script finds or uses the provided Python 3.11 interpreter, creates `.venv`, installs `requirements.txt`, writes `requirements-lock.txt`, and runs a quick smoke test.