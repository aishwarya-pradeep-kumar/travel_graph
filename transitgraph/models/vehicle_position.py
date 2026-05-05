"""Pydantic model + parser for the HSL HFP `vp` (vehicle position) payload.

Real payload shape captured from the wire by `scripts/mqtt_peek.py`:

    {
      "VP": {
        "desi": "550",
        "dir": "1",
        "oper": 22,
        "veh": 1234,
        "tst": "2026-05-05T14:03:01.256Z",
        "oday": "2026-05-05",
        "start": "08:00",
        "route": "2550",
        "stop": null,
        "lat": 60.18,
        "long": 24.83,
        "dl": -10,
        "...":  "other fields ignored in Phase 1 (spd, hdg, acc, odo, drst, ...)"
      }
    }

The wire `route` is HSL's *internal* route id (e.g. "2550" for the
user-facing line "550"); the analyst-facing display line is `desi`.
Trip identity is the `(route, dir, oday, start)` tuple - there is no
`tripId` field in the payload.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError


class VPParseError(ValueError):
    """Raised when a `vp` payload cannot be parsed into a VehiclePosition."""


class VehiclePosition(BaseModel):
    """One vehicle-position event from the HSL HFP feed."""

    model_config = ConfigDict(extra="ignore")

    desi: str
    dir: str
    oper: int
    veh: int
    tst: datetime
    oday: date
    start: str
    route: str

    stop: int | None = None
    lat: float | None = None
    long: float | None = None
    dl: int | None = None


class VPMessage(BaseModel):
    """Top-level `vp` MQTT payload wrapper."""

    model_config = ConfigDict(extra="ignore")

    VP: VehiclePosition


def parse_vp(raw: bytes | str | dict[str, Any]) -> VehiclePosition:
    """Parse a raw HFP `vp` MQTT payload into a `VehiclePosition`.

    Args:
        raw: payload as `bytes` (e.g. `paho.mqtt.MQTTMessage.payload`),
            `str` (already-decoded JSON), or `dict` (already-parsed).

    Returns:
        A validated `VehiclePosition`.

    Raises:
        VPParseError: malformed JSON, missing `VP` wrapper, or any field
            validation failure (e.g. unparseable `tst`).
    """
    if isinstance(raw, (bytes, str)):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise VPParseError(f"invalid JSON: {exc}") from exc
    else:
        data = raw

    try:
        return VPMessage.model_validate(data).VP
    except ValidationError as exc:
        raise VPParseError(str(exc)) from exc
