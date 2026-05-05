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

- _(fill in)_

---

## Phase 1 - Tiny E2E (MQTT direct to Neo4j)

**Plan:** see [`phase1_plan.md`](phase1_plan.md). Pre-step before step 2:
read one real HSL `vp` payload so the Pydantic model is written from
observed data, not from docs.

**Prompt strategy:** iterative (small approved steps, each with a
verification command afterwards).

**Tasks:**

- **MQTT exploration spike + Python 3.11 venv + truststore declaration.**
  Goal: see one real HSL `vp` payload before writing the Pydantic VP
  model in step 2. Outcome: 4 real bus messages printed, payload shape
  captured, several Phase-0-baseline assumptions corrected.
  - **Setup work**:
    - `uv` installed via `pip install --user uv` (Homebrew had an
      unrelated permissions issue; `uv` sidestepped that and gave us a
      managed Python 3.11.15 in `.venv` in one shot).
    - `make install-phase1` previously failed because there was no venv
      and system Python is 3.9.6 (project requires `>=3.11`). After
      `uv venv --python 3.11`, `uv pip install -e ".[phase1,dev]"`
      installed cleanly.
    - Added `.venv/` to `.gitignore` (only `venv/`/`env/`/`ENV/` were
      listed before).
    - Added `truststore>=0.10,<1` to `pyproject.toml[phase1]` for the
      production-shaped subscriber; kept the declaration even though it
      isn't usable for *this* spike (see below).
  - **Detours hit, ordered**:
    1. Corp SSL-inspection proxy (Zscaler/Netskope-style) re-signs TLS
       chains with an internal root CA. Python's `certifi` doesn't know
       it -> `SSLCertVerificationError: self signed certificate in
       certificate chain` on `mqtt.hsl.fi:8883`.
    2. Tried `truststore.inject_into_ssl()` to use macOS Keychain.
       Hit `ssl.SSLError: 'One or more parameters passed to a function
       were not valid'` from `Security.SecTrustCreateWithCertificates`
       inside `truststore/_macos.py`. Likely a known-ish wart between
       `truststore` and `python-build-standalone` builds.
    3. Fell back to plain MQTT (port 1883). Connection succeeded; corp
       proxy lets outbound 1883 through to mqtt.hsl.fi.
    4. paho-mqtt 2.x V2 callback API: `reason_code` is a
       `paho.mqtt.reasoncodes.ReasonCode` instance and does NOT
       implement `__int__`. Used `reason_code.is_failure` instead of
       `int(reason_code) != 0`. Agent factual error.
    5. First subscription used `.env`'s
       `MQTT_TOPIC_FILTER=/hfp/v2/journey/ongoing/vp/+/+/+/550/#`, which
       got zero messages. Cause: the `<route>` segment in HSL HFP topics
       is an *internal* route id (bus 550 is `2550`, metro M1 is `31M1`,
       train K is `3001K`), not the user-facing line. Broadened to
       `vp/bus/#` and confirmed messages flow.
  - **Payload findings (informs step 2 Pydantic model)**:
    - Top-level wrapper key is `VP`.
    - `tripId` from `phase1_plan.md` step 2's required-fields list does
      NOT exist in the payload. Trip identity comes from the
      `(route, dir, oday, start)` tuple.
    - `desi` (line as displayed: "550", "M1", "K") is what the analyst
      means by "route", not the topic-segment `route`. step 2's field
      list should add `desi` and treat `route` as the internal id.
    - `acc`, `dl`, `odo`, `drst` can be `null` (esp. metro `loc:MAN`).
      Step 2's tolerant parser is the right call.
    - `dl` is in seconds, negative = early. Confirmed.
    - Extra useful fields: `tsi` (unix timestamp), `loc` (`GPS`/`MAN`/
      `DR` data-quality flag), `seq`, `occu`.
  - **Cosmetic spike bug (not fixed)**: `client.disconnect()` doesn't
    drain the in-flight read buffer, so we sometimes print
    `message N+1/N` once before exit. Real subscriber will use a guard.
  - **Carry-forward to step 4**: production-shaped subscriber needs a
    real TLS path. Either (a) extract corp CA from System Keychain to
    a gitignored PEM file and `tls_set(ca_certs=...)`, or (b) revisit
    `truststore` if upstream fixes the macOS Security-framework wart.
    Plain MQTT on 1883 is fine for the spike but not acceptable in
    production-shaped code.
  - Prompt strategy: iterative. Each detour was surfaced as a
    multiple-choice fork rather than silently chosen.
  - Got right: verified library/pkg metadata against PyPI before
    pinning (`truststore` Python requirement, `uv` install path) per
    Phase 0 carry-forward; surfaced AGENTS.md "ask before non-trivial"
    forks (TLS strategy, venv tooling, brew vs uv).
  - Got wrong: assumed paho-mqtt 2.x `reason_code` supports `int()`;
    didn't anticipate the HSL route-id quirk before subscribing (it's
    documented in `phase1_plan.md` open question 2 vaguely, but not
    explicitly).
  - AI-authored vs hand-edited LOC (pre-commit): `pyproject.toml`
    +5/-0 (100% AI), `scripts/mqtt_peek.py` +~115 (100% AI),
    `.gitignore` +1 (100% AI), `.env` +5/-2 (100% AI), `.env.example`
    +5/-2 (100% AI), this entry 100% AI.
  - Framework facts wrong by agent: 1 (paho-mqtt `int(reason_code)`).
  - Owner self-rating (1-5): _<fill in>_.
- **Step 2: Pydantic VP model + parser + tests.** Created
  `transitgraph/models/vehicle_position.py` with `VehiclePosition`
  (Pydantic v2, 8 required fields + 4 nullable per the spike-corrected
  field list), `VPMessage` (top-level `{"VP": {...}}` wrapper),
  `VPParseError(ValueError)`, and a tolerant `parse_vp(raw)` accepting
  bytes/str/dict. Tests live under `tests/models/test_vehicle_position.py`
  using captured payloads in `tests/fixtures/{vp_bus,vp_metro_minimal}.json`
  loaded via `tests/conftest.py`. 7/7 pass; ruff clean.
  - **Detours hit**:
    1. Editable install was done before `transitgraph/` package
       directory existed -> first `pytest` run got
       `ModuleNotFoundError: No module named 'transitgraph'`. Fixed by
       `uv pip install --reinstall-package transitgraph -e .` so
       setuptools relinked the package.
    2. ruff's `UP017` flagged `datetime.timezone.utc` -> swapped to
       `datetime.UTC` (3.11+).
    3. `.gitignore`'s broad `*.json` rule (intended for data dumps)
       silently swallowed the test fixtures. The first commit (a4d5540)
       *passed tests locally* but would have broken on a fresh clone.
       Caught by `git status` showing `tests/fixtures/` still
       untracked. Followup commit b86cfe5 added
       `!tests/fixtures/*.json` and the JSON files.
    4. Added a small extra test (`test_invalid_json_raises_typed_error`)
       to cover the `json.JSONDecodeError` branch of `parse_vp` since
       `phase1_plan.md` step 2's "Bad timestamp raises a typed error"
       implied the wrapping should be uniform across all parse failures.
  - **Design notes**:
    - `model_config = ConfigDict(extra="ignore")` - the wire payload
      has many fields we don't model yet (`spd`, `hdg`, `acc`, `odo`,
      `drst`, `tsi`, `jrn`, `line`, `loc`, `occu`, `seq`, ...). They
      pass through harmlessly. Step 4's subscriber and step 5's GTFS
      validation will widen the model as needed.
    - `parse_vp(raw)` accepts `bytes` directly so the eventual
      `on_message(client, userdata, msg)` callback can pass
      `msg.payload` straight in.
    - All Pydantic exceptions are wrapped in `VPParseError`. Callers
      never need to import Pydantic to handle failure paths.
  - Prompt strategy: plan-then-build. Wrote a structured proposal
    (file layout + field list + test cases + commit shape) and got
    approval before any code, per AGENTS.md.
  - Got right: corrected the step-2 plan first (commit e7730fc) so the
    code matched a corrected spec; used real captured fixtures rather
    than hand-fabricated JSON; ran ruff + pytest before each commit.
  - Got wrong: forgot to re-install the editable package after creating
    `transitgraph/` (one extra step needed); didn't proactively check
    `.gitignore` for the new fixture path before committing.
  - AI-authored vs hand-edited LOC (pre-commit):
    `transitgraph/__init__.py` +3/-0 (100% AI),
    `transitgraph/models/__init__.py` +9/-0 (100% AI),
    `transitgraph/models/vehicle_position.py` +91/-0 (100% AI),
    `tests/conftest.py` +27/-0 (100% AI),
    `tests/models/test_vehicle_position.py` +69/-0 (100% AI),
    `tests/fixtures/*.json` +52/-0 (data, not code),
    `.gitignore` +2/-0 (100% AI),
    `docs/phase1_plan.md` +16/-4 (100% AI),
    this entry 100% AI.
  - Framework facts wrong by agent: 0.
  - Owner self-rating (1-5): _<fill in>_.

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
