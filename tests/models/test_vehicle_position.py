"""Unit tests for the VP payload parser (`transitgraph.models.vehicle_position`)."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any

import pytest

from transitgraph.models.vehicle_position import (
    VehiclePosition,
    VPParseError,
    parse_vp,
)


class TestParseVp:
    def test_happy_path_bus(self, vp_bus_payload: dict[str, Any]) -> None:
        vp = parse_vp(vp_bus_payload)
        assert isinstance(vp, VehiclePosition)
        assert vp.desi == "522"
        assert vp.dir == "1"
        assert vp.oper == 6
        assert vp.veh == 457
        assert vp.tst == datetime(2026, 5, 5, 14, 7, 33, 751000, tzinfo=UTC)
        assert vp.oday == date(2026, 5, 5)
        assert vp.start == "16:55"
        assert vp.route == "4522"
        assert vp.stop == 2117228
        assert vp.lat == pytest.approx(60.244598)
        assert vp.long == pytest.approx(24.808659)
        assert vp.dl == -30

    def test_tolerant_parse_metro_with_nulls(self, vp_metro_payload: dict[str, Any]) -> None:
        vp = parse_vp(vp_metro_payload)
        assert vp.desi == "M1"
        assert vp.dir == "2"
        assert vp.dl is None
        assert vp.stop is None
        assert vp.route == "31M1"

    def test_bad_timestamp_raises_typed_error(self, vp_bus_payload: dict[str, Any]) -> None:
        bad = {"VP": {**vp_bus_payload["VP"], "tst": "not-a-date"}}
        with pytest.raises(VPParseError, match="tst"):
            parse_vp(bad)

    def test_missing_vp_wrapper_raises_typed_error(self) -> None:
        with pytest.raises(VPParseError):
            parse_vp({"NotVP": {}})

    def test_accepts_bytes_input(self, vp_bus_payload: dict[str, Any]) -> None:
        raw = json.dumps(vp_bus_payload).encode("utf-8")
        vp = parse_vp(raw)
        assert vp.desi == "522"

    def test_accepts_str_input(self, vp_bus_payload: dict[str, Any]) -> None:
        vp = parse_vp(json.dumps(vp_bus_payload))
        assert vp.desi == "522"

    def test_invalid_json_raises_typed_error(self) -> None:
        with pytest.raises(VPParseError, match="invalid JSON"):
            parse_vp(b"this is not json {")
