@echo off
TITLE ParkNest
python -m app/main.py
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload