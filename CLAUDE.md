# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

An AI agent that helps analysts find US airports where renovation is most profitable, based on increased flight and passenger capacity. It answers questions in a chat, ranks airports with deterministic scoring, and cites the data behind every number.

- Design decisions: [`docs/DECISIONS.md`](docs/DECISIONS.md). Design document: `docs/DESIGN.md`.

## Stack

Python 3.12 · FastAPI · OpenAI SDK (any OpenAI-compatible LLM) · pytest · uv · ruff | React · TypeScript · Vite · Tailwind | Docker Compose.

## Layout

```
apps/api/app/
  main.py              # wiring, /health
  common/tables.py     # reads the committed data tables
  modules/
    <domain>/          # airports, rankings, live_status: no LLM imports, only the files each needs (D-015)
      service.py           # business rules; may read another module's repository
      repository.py        # the only layer that reads data (tables or the FAA feed)
      schemas.py           # Pydantic models: what services and tools return
    rankings/kpi.py    # the pure KPI math
    chat/              # agent loop (runs tools, checks the answer), tools, citations, LLM
apps/api/scripts/      # offline data snapshot builders (D-009)
apps/api/data/         # committed snapshots
apps/web/src/          # feature folders, one folder per component (D-016)
```

## Workflow

- **The developer owns the code; Claude proposes.** Every design decision is presented as a multiple-choice question with 4 options and Claude's recommendation marked. The developer decides. Neither side is a yes-man: push back with reasons.
- Each question shows the estimated lines per option, the running line total, and the hours left.
- Design decisions are recorded in `docs/DECISIONS.md`. Tooling and housekeeping choices are not.
- Changes land in chunks of about 3 files or 150 lines, then stop for review with 1–3 questions that check the developer can explain the chunk.
- The simplest correct solution always: standard library and framework features first, no speculative abstractions.
- Claude writes all the code; the developer reviews, decides and asks for explanations.
- Verify before calling a chunk done: `ruff check`, `ruff format --check`, the tests.

## Conventions

- **Numbers come from code, never from the LLM.** Tools return computed values with their source and "as of" date.
- **Comments:** zero by default. Every Python file opens with a one-line docstring stating its role. A comment only for a non-obvious invariant or workaround.
- **Python style:** type hints and return types on every function; `UPPER_CASE` constants at the top; `_` prefix for private helpers.
- **Structure:** services return Pydantic schemas, never loose dicts. Each function stays at one level of abstraction. Pure math lives in its own file next to the service.
- **Errors:** never fail silently, never substitute a fallback that hides a bug. Unknown inputs are reported back, never dropped.
- **Secrets** come from environment variables only; `.env.example` documents every variable.
- **Commits:** Conventional Commits with the area as scope (`feat(airports): …`). AI-assisted commits carry a `Co-Authored-By: Claude` trailer.
