"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def vp_bus_payload() -> dict[str, Any]:
    """Real captured bus VP payload (line 522, recorded 2026-05-05)."""
    return _load("vp_bus.json")


@pytest.fixture
def vp_metro_payload() -> dict[str, Any]:
    """Real captured metro VP payload (M1) with explicit nulls and a missing `jrn`."""
    return _load("vp_metro_minimal.json")
