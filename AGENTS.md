# AGENTS.md - Rules for AI Agents on TransitGraph

This repo is a **learning project**. The owner is using it to learn the stack
(MQTT, Kafka, PyFlink, Neo4j, FastAPI, Streamlit) and to measure how useful AI
agents are along the way. Optimize for *teaching* and *measurability*, not for
shipping the largest possible diff.

## Prime directives

1. **Phased thinking.** Never jump phases. If the current phase is "Phase 1 -
   tiny E2E (no Kafka, no Flink)", do not introduce Kafka, Flink, or any
   abstraction that anticipates them. Each phase intentionally re-touches code
   so the owner sees the *why* of each new layer.
2. **Small, reviewable diffs.** Prefer the smallest change that makes the next
   test pass or runs the next command. No mega-rewrites.
3. **Explain trade-offs in chat, not in code comments.** Comments should explain
   non-obvious intent only. Do not narrate code line-by-line in comments.
4. **Ask when ambiguous.** If the use case (U1-U4 in the README) is unclear or
   the phase scope is unclear, ask before coding.

## When to ask vs. proceed

Ask the owner before:

- Adding a new top-level dependency.
- Adding a new service to docker-compose.
- Choosing between two non-trivial library options (e.g., PyFlink Table API vs
  DataStream API).
- Changing the graph schema in `[README.md](README.md)`.
- Skipping or merging a phase.

Proceed without asking when:

- Fixing a clearly broken import, type, or test.
- Reformatting via the configured formatter.
- Adding tests for code already in the current phase's scope.

## Coding standards

- **Language:** Python 3.11+.
- **Formatter / linter:** `ruff` (and `ruff format`). No `black` separately.
- **Type hints:** required on all new public functions and module-level
  callables. Use `from __future__ import annotations`.
- **Tests:** `pytest`. Every new module gets at least one test in `tests/`
  mirroring the path. Integration tests that need Neo4j / Kafka must be
  marked with `@pytest.mark.integration` and skipped by default in CI.
- **Logging:** use `logging.getLogger(__name__)`, not `print`. Configure once
  in entrypoints.
- **Config:** all knobs (broker URL, Neo4j URI, route filter) read from env
  vars via `pydantic-settings`. Provide defaults via `[.env.example](.env.example)`.

## Phase scope (do not exceed)

| Phase | In scope | Out of scope |
| ----- | -------- | ------------ |
| 0 | docs, KPIs, tooling, AGENTS.md | any application code |
| 1 | one MQTT subscriber, direct Neo4j writes, one Cypher query | Kafka, Flink, FastAPI, dashboard |
| 2 | Kafka producer + consumer split | Flink, dashboard |
| 3 | PyFlink windowed aggregates, sink to Neo4j | dashboard |
| 4 | FastAPI endpoints, Streamlit dashboard | GTFS validation |
| 5 | GTFS-static loader, Prometheus, soak test, chaos | new features |

If the user asks for something out of the current phase's scope, **say so and
ask whether to advance the phase** instead of silently expanding scope.

## AI-agent measurement protocol

For every non-trivial task, when finishing the work, append an entry to
`[docs/ai_log.md](docs/ai_log.md)` under the current phase with:

- Prompt strategy (one-shot / iterative / plan-then-build).
- What the agent got right and wrong.
- Approximate % of the diff that was AI-authored vs hand-edited.
- Any framework or codebase fact the agent got wrong.
- Owner's self-rated prompt quality (1-5) - to be filled by the owner.

If the work was trivial (single typo fix, dependency bump), skip the log entry
but mention so in the PR/commit message.

## Things to never do

- Never add code that depends on a service not yet introduced in the current
  phase (e.g., do not import `kafka` in Phase 1).
- Never delete or modify anything under `[archive/v1/](archive/v1)`. It is the
  reference snapshot of the previous prototype.
- Never edit `[README.md](README.md)`'s "What does it answer?" or "Domain model"
  sections without the owner confirming the use case has changed.
- Never commit secrets. `.env` is in `[.gitignore](.gitignore)`.

## Useful commands (once Step 0 tooling lands)

| Command | What |
| ------- | ---- |
| `make up` | Start local services for the current phase |
| `make down` | Stop and remove containers |
| `make test` | Unit tests only |
| `make test-int` | Unit + integration tests |
| `make lint` | Ruff check + format |
| `make ingest` | Run the current phase's ingest entrypoint |

> **Note on `.env` and Docker Compose:** `make up` / `make down` pass
> `--env-file .env` because Compose looks for `.env` in the *project directory*
> (the directory of the `-f` compose file) by default, not in the current
> working directory. If you run `docker compose -f deploy/phaseN/docker-compose.yml ...`
> by hand from the repo root, add `--env-file .env` or you'll get
> `required variable ... is missing a value` errors.
