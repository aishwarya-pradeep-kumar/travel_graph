# TransitGraph

Real-time **route-delay analytics** on the Helsinki Digitransit MQTT feed, modeled as a streaming graph, built for a transit **operations analyst**.

This repository is also a deliberate **learning project**: the system is rebuilt in phases so each piece of the stack (MQTT, Kafka, stream processing, graph DB, FastAPI) can be learned in isolation, with AI-agent collaboration tracked as a measured experiment.

---

## What does it answer?

> "How has a route's delay behaved over the last N minutes / hours?"

Concrete user stories for the analyst persona:

| ID | Story | Window |
| -- | ----- | ------ |
| U1 | Live route delay monitor (p50, p95 per route) | rolling 5 / 15 / 60 min |
| U2 | Top-10 worst-offender routes with trend vs prior window | operational |
| U3 | Single-route deep dive (per-minute, per-direction, per-stop) | last 1 h |
| U4 | Shift retrospective (consistently late routes, where delay accumulates) | last 8 h |

## Architecture (target)

```
Digitransit MQTT  -->  Kafka (vp-raw)  -->  PyFlink windowed aggregates  -->  Neo4j  -->  FastAPI  -->  Streamlit
```

We do **not** build all of this on day one. See [Phases](#phases).

## Domain model

```
(Vehicle) -[OPERATING]-> (Trip) -[OF_ROUTE]-> (Route)
                          |
                          +-[SERVES]-> (Stop)
                          +-[OBSERVED_IN]-> (TimeWindow)

(Route) -[HAS_DELAY_IN]-> (TimeWindow {bucket, sizeMinutes,
                                       count, p50, p95, mean, maxStopId})
```

## Tech stack

| Layer | Choice | Why |
| ----- | ------ | --- |
| Ingest | `paho-mqtt` (Python) | Native HSL MQTT client |
| Broker | Apache Kafka | Decouple ingest from compute, enable replay |
| Stream processing | PyFlink | Event-time windowing + watermarks for delay aggregates |
| Graph DB | Neo4j | Cypher fits the analyst's relationship queries |
| API | FastAPI | Backs U1-U4 |
| Dashboard | Streamlit | Fastest path to a usable analyst UI |
| Schedule data | GTFS-static (HSL) | Independent validation of `dl` field |

## Phases

| Phase | Goal | Key tech learned |
| ----- | ---- | ---------------- |
| 0 | Foundation: KPIs, AI-agent log, tooling | repo hygiene |
| 1 | Tiny E2E - capture `dl` directly into Neo4j (no Kafka, no Flink) | MQTT, Cypher MERGE |
| 2 | Insert Kafka between ingest and Neo4j | partitions, offsets, replay |
| 3 | PyFlink windowed delay aggregates per route | event time, watermarks |
| 4 | FastAPI + Streamlit dashboard for U1-U4 | API design, viz |
| 5 | GTFS validation, observability, soak test | batch joins, Prometheus |

Each phase ships something the analyst could actually use, and each ends with an AI-agent retro in [`docs/ai_log.md`](docs/ai_log.md).

## KPIs

Three categories, defined in [`docs/kpis.md`](docs/kpis.md):

- **System KPIs** - latency for U1-U4, pipeline lag, throughput, correctness.
- **Learning KPIs** - per-tech mastery checks, conceptual questions resolved.
- **AI-agent effectiveness KPIs** - % AI-authored, rework rate, time-to-first-working-version, factual error count.

## Repository layout

```
.
├── AGENTS.md            # rules for AI agents on this repo
├── README.md            # this file
├── Makefile             # one-command tasks (make up, make test, ...)
├── docs/
│   ├── kpis.md          # KPI definitions and how each is measured
│   ├── ai_log.md        # per-phase AI-agent retro
│   └── phase1_plan.md   # detailed Phase 1 plan (created last in Step 0)
├── archive/
│   └── v1/              # original prototype, kept for reference
└── (src/, tests/, etc. arrive in Phase 1)
```

## Status

Phase 0 (foundation) is in progress. No application code exists yet outside `archive/v1/`. See [`docs/phase1_plan.md`](docs/phase1_plan.md) for what comes next.

## Data source

[Digitransit MQTT API - vehicle positions](https://digitransit.fi/en/developers/apis/4-realtime-api/vehicle-positions/). Topic structure:

```
/hfp/v2/journey/ongoing/vp/<mode>/<operator>/<vehicle>/<route>/<dir>/<headsign>/<start>/<next_stop>/<geohash>/<sid>
```

The payload's `dl` field (delay in seconds vs schedule) is the primary signal.
