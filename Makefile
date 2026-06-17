.PHONY: install dev api ui test benchmark lint format clean

PYTHON ?= python
VENV_PY := .venv/Scripts/python.exe
VENV_PIP := .venv/Scripts/pip.exe

# Windows-first paths; on Unix use: .venv/bin/python
ifeq ($(OS),Windows_NT)
    PY := $(if $(wildcard $(VENV_PY)),$(VENV_PY),$(PYTHON))
    PIP := $(if $(wildcard $(VENV_PIP)),$(VENV_PIP),$(PYTHON) -m pip)
else
    PY := $(if $(wildcard .venv/bin/python),.venv/bin/python,$(PYTHON))
    PIP := $(if $(wildcard .venv/bin/pip),.venv/bin/pip,$(PYTHON) -m pip)
endif

install:
	$(PYTHON) -m venv .venv
	$(PIP) install -r requirements.txt
	@if not exist .env copy .env.example .env

dev:
	$(PY) run.py

api:
	$(PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ui:
	$(PY) -m streamlit run app/ui/streamlit_app.py --server.port 8501

test:
	$(PY) -m pytest tests/ -v

benchmark:
	$(PY) -m app.tools.benchmark

lint:
	$(PY) -m ruff check app tests

format:
	$(PY) -m black app tests

clean:
	@if exist storage\\generated\\*.png del /q storage\\generated\\*.png 2>nul
	@if exist storage\\diagrams\\*.svg del /q storage\\diagrams\\*.svg 2>nul
	@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul
