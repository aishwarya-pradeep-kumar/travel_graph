"""Throwaway HSL MQTT exploration spike (Phase 1, pre-step).

Connects to the Digitransit MQTT feed over plain MQTT (port 1883), subscribes
to a topic filter from `.env`, prints the first N messages as parsed JSON,
then disconnects.

NOT part of the production pipeline. The real subscriber lands in
`transitgraph/ingest/mqtt_subscriber.py` per `docs/phase1_plan.md` step 4.
This file exists so the owner can see the payload shape *before* writing
the Pydantic VP model in step 2. Move to `docs/snippets/` or delete once
step 4 lands.

Why plain MQTT (not TLS) here:
    On a corp-managed macOS laptop, an SSL-inspection proxy re-signs
    outbound TLS chains with an internal root CA. Python's bundled
    `certifi` doesn't know about it. `truststore` (which would normally
    pick up the root from macOS Keychain) currently hits an
    `errSecParam` from `SecTrustCreateWithCertificates` on
    `python-build-standalone` builds. Sidestepped here by using plain
    MQTT on 1883 - acceptable for a spike, NOT for production. The real
    subscriber will fix this properly (extract corp CA, or wait for
    truststore upstream fix). See `docs/ai_log.md` Phase 0/1 for context.

Usage:
    python3 scripts/mqtt_peek.py             # 5 messages, route 550 (.env default)
    N=10 python3 scripts/mqtt_peek.py        # 10 messages
    MQTT_TOPIC_FILTER='/hfp/v2/journey/ongoing/vp/#' \\
        python3 scripts/mqtt_peek.py         # all routes (firehose, beware)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt.hsl.fi")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))  # spike: plain MQTT
TOPIC_FILTER = os.getenv("MQTT_TOPIC_FILTER", "/hfp/v2/journey/ongoing/vp/+/+/+/550/#")
N_MESSAGES = int(os.getenv("N", "5"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("mqtt_peek")

_received = 0


def on_connect(
    client: mqtt.Client,
    userdata: Any,
    flags: dict,
    reason_code: Any,
    properties: Any,
) -> None:
    if reason_code.is_failure:
        log.error("connect failed: %s", reason_code)
        sys.exit(1)
    log.info("connected; subscribing to %s", TOPIC_FILTER)
    client.subscribe(TOPIC_FILTER, qos=0)


def on_message(
    client: mqtt.Client,
    userdata: Any,
    msg: mqtt.MQTTMessage,
) -> None:
    global _received
    _received += 1
    try:
        payload = json.loads(msg.payload)
    except json.JSONDecodeError:
        payload = msg.payload.decode("utf-8", errors="replace")

    print(f"\n--- message {_received}/{N_MESSAGES} ---")
    print(f"topic: {msg.topic}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if _received >= N_MESSAGES:
        log.info("got %d messages, disconnecting", _received)
        client.disconnect()


def main() -> None:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    client.on_connect = on_connect
    client.on_message = on_message
    # client.tls_set()   # spike: TLS disabled, see module docstring

    log.info("connecting to %s:%d (plain MQTT)...", BROKER_HOST, BROKER_PORT)
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("interrupted; disconnecting")
        client.disconnect()


if __name__ == "__main__":
    main()
