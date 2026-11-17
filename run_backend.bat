@echo off
cd /d %~dp0backend
uvicorn app.main:app --reload --reload-dir app --port 8000
