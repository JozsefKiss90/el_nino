@echo off
cd /d C:\Code\el_nino\voice_bridge
.venv\Scripts\uvicorn.exe voice_bridge:app --host 127.0.0.1 --port 8585
