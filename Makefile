.PHONY: help install install-phase1 install-phase2 install-phase3 install-phase4 install-phase5 \
        lint format test test-int up down config ingest clean

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip
# Default phase for `make up` / `make down` / `make config`. Override on CLI:
#   make up PHASE=1
PHASE  ?= 0

help:
	@echo "TransitGraph - Make targets"
	@echo ""
	@echo "  install            Dev tools only (Phase 0 default)."
	@echo "  install-phase1     Phase 1 runtime deps (paho-mqtt, neo4j) + dev."
	@echo "  install-phase2     Phase 2 (adds Kafka)."
	@echo "  install-phase3     Phase 3 (adds PyFlink)."
	@echo "  install-phase4     Phase 4 (adds FastAPI + Streamlit)."
	@echo "  install-phase5     Phase 5 (adds GTFS + observability)."
	@echo ""
	@echo "  lint               Ruff check."
	@echo "  format             Ruff format (writes)."
	@echo "  test               Unit tests only."
	@echo "  test-int           Unit + integration tests (needs services up)."
	@echo ""
	@echo "  up PHASE=N         Bring up the docker-compose stack for phase N."
	@echo "  down PHASE=N       Tear down phase N's stack."
	@echo "  config PHASE=N     Render phase N's resolved compose config (sanity check)."
	@echo "  ingest             Run the current phase's ingest entrypoint."
	@echo "  clean              Remove caches and build artifacts."

# ----- install -----

install:
	$(PIP) install -e ".[dev]"
	pre-commit install

install-phase1:
	$(PIP) install -e ".[phase1,dev]"
	pre-commit install

install-phase2:
	$(PIP) install -e ".[phase2,dev]"
	pre-commit install

install-phase3:
	$(PIP) install -e ".[phase3,dev]"
	pre-commit install

install-phase4:
	$(PIP) install -e ".[phase4,dev]"
	pre-commit install

install-phase5:
	$(PIP) install -e ".[phase5,dev]"
	pre-commit install

# ----- quality -----

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	pytest -m "not integration"

test-int:
	pytest

# ----- runtime -----

# Each phase will own a compose file under deploy/phase<N>/docker-compose.yml.
# Phase 0 has no services; `make up` is a no-op until Phase 1.
# Compose looks for `.env` in the project directory (= dir of the -f file)
# by default, not in the cwd. We pass `--env-file .env` so the project root's
# .env is always used, regardless of which phase's compose file we point at.
up:
	@if [ -f deploy/phase$(PHASE)/docker-compose.yml ]; then \
	    docker compose --env-file .env -f deploy/phase$(PHASE)/docker-compose.yml up -d; \
	else \
	    echo "No docker-compose for phase $(PHASE) yet. Nothing to do."; \
	fi

down:
	@if [ -f deploy/phase$(PHASE)/docker-compose.yml ]; then \
	    docker compose --env-file .env -f deploy/phase$(PHASE)/docker-compose.yml down -v; \
	else \
	    echo "No docker-compose for phase $(PHASE) yet. Nothing to do."; \
	fi

config:
	@if [ -f deploy/phase$(PHASE)/docker-compose.yml ]; then \
	    docker compose --env-file .env -f deploy/phase$(PHASE)/docker-compose.yml config; \
	else \
	    echo "No docker-compose for phase $(PHASE) yet. Nothing to do."; \
	fi

ingest:
	@echo "Phase 0 has no ingest. Run after Phase 1 lands."

# ----- housekeeping -----

clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \
	    -o -name .mypy_cache -o -name '*.egg-info' \) -prune -exec rm -rf {} +
