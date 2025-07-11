@echo off
cd /d "%~dp0"
call venv_invokeai\Scripts\activate.bat
uvicorn invokeai.app.api_app:app --host 127.0.0.1 --port 9090
npause 