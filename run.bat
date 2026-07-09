@echo off
title ADA Market Intelligence V1
cd /d %~dp0
if not exist .venv (
  py -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
start "" http://127.0.0.1:8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
