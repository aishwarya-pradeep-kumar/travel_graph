# AI-Agent Log

Per-phase log of how AI agents helped (or didn't) on TransitGraph. Definitions
and measurement methods live in [`kpis.md`](kpis.md). Section C of that file
defines the AI-agent KPIs used here.

How to use this file:

1. **At the start of a phase** - fill in "Plan" and "Prompt strategy".
2. **As you work** - jot tasks under "Tasks" with one or two lines on what the
   agent did and where it stumbled.
3. **At the end of the phase** - fill in the KPI checklist and the retro.

---

## Phase 0 - Foundation

**Plan:** Archive the v1 prototype, write README / AGENTS / KPIs / this log,
add tooling (Makefile, env, deps, pre-commit), draft the Phase 1 plan.

**Prompt strategy:** plan-then-build. The agent first produced a plan via Plan
mode, the owner refined the use case (ops analyst + delay over time windows),
the plan was finalized, then executed top-to-bottom in Agent mode.

**Tasks:**

- _(fill in: e.g., "Archive: agent used `git mv`, hit a snag with files already
  deleted in the working tree, recovered with `git checkout HEAD --` and
  continued. Required no rework.")_
- **Phase 0 polish - Compose `.env` resolution fix.** Owner ran
  `docker compose -f deploy/phase1/docker-compose.yml ps` from repo root and got
  `required variable NEO4J_PASSWORD is missing`. Agent diagnosed the
  Compose-v2 default-project-directory rule (`.env` is loaded from the
  directory of the `-f` file, not the cwd) and proposed `--env-file .env` on
  the `up` / `down` Makefile targets plus a callout in `AGENTS.md`. Confirmed
  with `docker compose --env-file .env -f ... config`.
  - Prompt strategy: iterative (read-only project scan -> structured
    multiple-choice questions -> approval -> apply -> verify).
  - Got right: root cause and fix on first try; respected AGENTS.md "ask
    before non-trivial changes" rule by surfacing the Neo4j-auth decision
    instead of silently picking one.
  - Got wrong: briefly chased a phantom `'healthcheck' not allowed` error
    caused by piping `docker compose config` through `head -40`; not a real
    schema bug. ~1 extra tool call to disprove.
  - AI-authored vs hand-edited LOC (pre-commit): Makefile 5/5 (100% AI),
    AGENTS.md 7/7 (100% AI), this entry 100% AI.
  - Framework facts wrong: 0.
  - Owner self-rating (1-5): _<fill in>_.
- **Phase 0 polish - `make config` + PHASE-default bug fix.** Owner asked to
  add a `make config` target so manual compose sanity checks don't require
  typing `--env-file .env`. Agent added the target (plus `.PHONY` and help
  entry) mirroring `up` / `down`. Smoke test with bare `make config`
  (default `PHASE=0`) surfaced a pre-existing bug: an inline comment on
  `PHASE  ?= 0` was leaking trailing whitespace into `$(PHASE)`, so
  `[ -f deploy/phase$(PHASE)/... ]` tokenized into too many shell args and
  failed with `binary operator expected`. Fixed by moving the comment to
  its own line above the assignment. `make up` / `make down` were silently
  broken in the same way whenever called without `PHASE=N` on the CLI.
  - Prompt strategy: one-shot (apply -> verify), promoted to iterative
    when the masked bug surfaced.
  - Got right: noticed and fixed the masked bug instead of treating it as
    out-of-scope; minimum-surgical change.
  - Got wrong: nothing notable in this task.
  - AI-authored vs hand-edited LOC (pre-commit): Makefile +10/-1 (100% AI),
    this entry 100% AI.
  - Framework facts wrong: 0.
  - Owner self-rating (1-5): _<fill in>_.
- **Phase 0 polish - bad Neo4j image tag.** `make up PHASE=1` failed with
  `failed to resolve reference "docker.io/library/neo4j:5.24.0-community":
  not found`. Agent listed Docker Hub tags for the 5.24 line and confirmed
  `5.24.0` was never released - the prior author hallucinated the tag. Real
  tags on that line are `5.24.1` / `5.24.2` (and the floating `5.24` /
  `5-community`). Pinned to `5.24.2-community` for reproducibility.
  - Prompt strategy: one-shot (verify hub tags -> propose options ->
    approve -> apply).
  - Got right: verified against Docker Hub instead of guessing a different
    tag from training data.
  - Got wrong: nothing notable.
  - AI-authored vs hand-edited LOC (pre-commit): docker-compose.yml +1/-1
    (100% AI).
  - Framework facts wrong by prior agent: 1 (invented `5.24.0-community`).
  - Owner self-rating (1-5): _<fill in>_.

**KPI checklist:**

```
System KPIs measured: n/a (no application code yet)

Learning KPIs:
  - n/a for Phase 0 (no tech learned yet)
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: plan-then-build
  - Self-rating: <1-5>
```

**Retro - what worked:**

- _(fill in)_

**Retro - what didn't:**

- _(fill in)_

**Carry-forward to next phase:**

- Always verify third-party version pins (Docker image tags, PyPI package
  versions, Kafka client lines, etc.) against the actual registry before
  committing. Two factual errors in Phase 0 baseline came from agents
  picking plausible-but-nonexistent version strings from training data
  (`neo4j:5.24.0-community` was hallucinated; the missing `--env-file`
  was a Compose-rule misremember).

---

## Phase 1 - Tiny E2E (MQTT direct to Neo4j)

**Plan:** Per [`phase1_plan.md`](phase1_plan.md). Six numbered steps, each its
own commit and ideally its own AI prompt batch:

1. compose + Neo4j up (smoke test - compose file already on disk).
2. Pydantic v2 `VehiclePosition` model + parser tests.
3. Neo4j writer + integration test (writes one sample, queries it back).
4. MQTT subscriber wired to writer (TLS, reconnect, callback hand-off).
5. CLI entrypoint (`transitgraph/cli/run_phase1.py`) + smoke test.
6. KPI capture (S3 pipeline lag, U1 Cypher p95) + canonical query
   `queries/avg_delay_last_15m.cypher`.

Open questions from `phase1_plan.md` are resolved by current `.env`:
TLS=true (port 8883), `ROUTE_FILTER=550,4,9`, `NEO4J_PASSWORD=changeme`
(auth on, password from env, not disabled), no `DelaySample` retention in
Phase 1 (acceptable for the few-hour test windows; revisit in Phase 5).

**Prompt strategy:** plan-then-build (same as Phase 0). Each step gets its
own plan-mode pass before any code lands.

**Tasks:**

- _(fill in)_

**KPI checklist:**

```
System KPIs measured:
  - S3 (pipeline lag p95): <value> (target < 5 s)

Learning KPIs:
  - Tech: MQTT      | concept-explained: Y/N | minimal-example: Y/N
  - Tech: Cypher    | concept-explained: Y/N | minimal-example: Y/N
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: <one-shot|iterative|plan-then-build>
  - Self-rating: <1-5>
```

**Retro - what worked:**
**Retro - what didn't:**
**Carry-forward:**

---

## Phase 2 - Kafka decoupling

**Plan:**
**Prompt strategy:**
**Tasks:**

**KPI checklist:**

```
System KPIs measured:
  - S3 (pipeline lag p95): <value>
  - S4 (throughput): <value>

Learning KPIs:
  - Tech: Kafka     | concept-explained: Y/N | minimal-example: Y/N
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: <>
  - Self-rating: <1-5>
```

**Retro - what worked:**
**Retro - what didn't:**
**Carry-forward:**

---

## Phase 3 - PyFlink windowed delay aggregates

**Plan:**
**Prompt strategy:**
**Tasks:**

**KPI checklist:**

```
System KPIs measured:
  - S5 (window correctness vs pandas): <value>

Learning KPIs:
  - Tech: PyFlink   | concept-explained: Y/N | minimal-example: Y/N
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: <>
  - Self-rating: <1-5>
```

**Retro - what worked:**
**Retro - what didn't:**
**Carry-forward:**

---

## Phase 4 - FastAPI + Streamlit dashboard

**Plan:**
**Prompt strategy:**
**Tasks:**

**KPI checklist:**

```
System KPIs measured:
  - S1 (U1 API p95): <value>
  - S2 (U3/U4 API p95): <value>

Learning KPIs:
  - Tech: FastAPI   | concept-explained: Y/N | minimal-example: Y/N
  - Tech: Streamlit | concept-explained: Y/N | minimal-example: Y/N
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: <>
  - Self-rating: <1-5>
```

**Retro - what worked:**
**Retro - what didn't:**
**Carry-forward:**

---

## Phase 5 - GTFS validation, observability, soak

**Plan:**
**Prompt strategy:**
**Tasks:**

**KPI checklist:**

```
System KPIs measured:
  - S6 (soak uptime): <pass/fail>
  - S7 (replay correctness): <pass/fail>

Learning KPIs:
  - Tech: GTFS-static    | concept-explained: Y/N | minimal-example: Y/N
  - Tech: Observability  | concept-explained: Y/N | minimal-example: Y/N
  - Questions resolved: <n>

AI-agent KPIs:
  - % AI-authored: <%>
  - Rework rate: <%>
  - Time-to-first-working: <min> (solo estimate: <min>)
  - Factual errors: <n>
  - Prompt strategy: <>
  - Self-rating: <1-5>
```

**Retro - what worked:**
**Retro - what didn't:**
**Carry-forward:**

---

## Cross-phase trends (fill in after Phase 5)

- Did `% AI-authored` rise or fall as the codebase grew? Why?
- Did rework rate trend toward < 30%?
- Which prompt strategy gave the best time-to-first-working ratio?
- Top 3 framework/codebase facts the agent got wrong (so the owner knows
  where extra scrutiny is worth it).
- Three-sentence verdict: where AI agents helped most, helped least.
