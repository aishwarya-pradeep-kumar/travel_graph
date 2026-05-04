# KPIs - TransitGraph

Three categories. Every phase ends with a KPI checkpoint: fill in the table at
the end of the phase's section in [`ai_log.md`](ai_log.md).

---

## A. System KPIs

Driven by the four use cases in [`../README.md`](../README.md). All targets
assume a single laptop running everything in docker-compose.

| ID | KPI | Target | How to measure | First phase it applies |
| -- | --- | ------ | -------------- | ---------------------- |
| S1 | API p95 latency for U1 ("current rolling delay per route") | < 500 ms | `wrk` or `hey`, 60 s warm run, 50 concurrent clients against `/routes/top-delayed` | 4 |
| S2 | API p95 latency for U3/U4 (historical breakdowns) | < 2 s | same harness against `/routes/{id}/delay/history` | 4 |
| S3 | Pipeline lag - MQTT publish to Neo4j write | p95 < 5 s | record `tst` from MQTT payload, compare to `now()` at write time, log per message; aggregate in a 5-min window | 1 |
| S4 | Sustained throughput | >= 100 msg/s | `kafka-producer-perf-test` for the broker leg; for E2E, count Neo4j writes/sec over a 5-min window | 2 |
| S5 | Window correctness vs offline recompute | within 1% of pandas baseline on the same Kafka offset range | export raw events from Kafka to parquet, recompute the same windowed delay stats in pandas, diff per `(route, window)` row | 3 |
| S6 | Soak uptime | 10-min run with zero unhandled exceptions | `make soak`; tail logs; grep for `ERROR`/`Traceback`; assert count == 0 | 5 |
| S7 | Replay correctness after consumer kill | identical Neo4j state vs no-kill run | run scenario A (no kill) and B (kill consumer mid-run, restart from earliest); diff Cypher counts of `(:DelaySample)` per `(route, minute)` | 5 |

### Per-use-case query budget

| Use case | Cypher (Phase 1-3) target p95 | API (Phase 4+) target p95 |
| -------- | ----------------------------- | ------------------------- |
| U1 - current rolling delay | < 200 ms | < 500 ms |
| U2 - top-10 worst routes | < 200 ms | < 500 ms |
| U3 - single-route deep dive | < 800 ms | < 2 s |
| U4 - 8 h shift retro | < 1.5 s | < 2 s |

---

## B. Learning KPIs

One row per technology. The "explain in 5 sentences" test is self-administered:
write the explanation in [`ai_log.md`](ai_log.md) and judge it later.

| Tech | Concept owner must explain | Minimal example built without copy-paste? | First phase covered |
| ---- | -------------------------- | ----------------------------------------- | ------------------- |
| MQTT | QoS levels, retained messages, topic wildcards | hand-write a subscriber to one topic | 1 |
| Cypher / Neo4j | `MERGE` vs `CREATE`, indexes, parameterized queries | write a parametric `MERGE` for a domain node | 1 |
| Kafka | partitions, offsets, consumer groups, at-least-once | run producer + consumer, observe rebalancing | 2 |
| PyFlink | event time vs processing time, watermarks, allowed lateness | a tumbling-window job that emits to stdout | 3 |
| FastAPI | dependency injection, Pydantic models, async endpoints | one endpoint with an injected dependency | 4 |
| Streamlit | session state, caching, layout primitives | a single-page app reading from FastAPI | 4 |
| GTFS-static | feed structure (`stop_times`, `trips`, `calendar`) | parse a feed and answer "scheduled time at stop X for trip Y" | 5 |
| Observability | metrics vs logs vs traces, Prometheus pull model | expose `/metrics` and chart one counter | 5 |

### Aggregate learning KPIs (per phase)

- Number of conceptual questions resolved (logged in `ai_log.md`).
- Tech coverage so far: `techs touched / techs in stack`.

---

## C. AI-Agent Effectiveness KPIs

Recorded per phase in [`ai_log.md`](ai_log.md).

| KPI | How measured | Target / direction |
| --- | ------------ | ------------------ |
| % AI-authored LOC | `git diff` between AI's first proposal commit and the final phase commit. AI-authored = lines unchanged from proposal; hand-edited = lines changed or added | trend, not target |
| Rework rate | (lines changed by hand after AI proposal) / (lines AI proposed) | < 30% |
| Time-to-first-working-version (with AI) | wall-clock from first prompt to first green test | record both this and the owner's solo estimate |
| AI factual errors | count of times the agent stated something incorrect about the codebase or framework, then was corrected | trend down |
| Prompt strategy | one-shot / iterative / plan-then-build | note which worked best per phase |
| Owner prompt-quality self-rating | 1-5 with one-line note | trend up |

### How to capture "AI-authored vs hand-edited" reliably

1. When starting an AI-driven task, ask the agent to commit its first proposal
   verbatim on a branch like `phaseN/ai-proposal/<task>`.
2. Hand-edit on top in further commits on the same branch.
3. At end of phase, run:

   ```bash
   git diff --stat phaseN/ai-proposal/<task>..phaseN/main -- '*.py'
   ```

   The insertions/deletions are the rework volume. Divide by the proposal's
   total LOC for the rework rate.

---

## Per-phase KPI checklist (copy into each `ai_log.md` entry)

```
System KPIs measured:
  - S?: <value> (target <target>) [pass/fail]

Learning KPIs:
  - Tech: <name> | concept-explained: Y/N | minimal-example: Y/N
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: <one-shot|iterative|plan-then-build>
  - Self-rating: <1-5>
```
