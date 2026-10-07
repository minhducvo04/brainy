# Brainy submission draft

**Team:** Duc Vo (Brainy). **Repo:** https://github.com/minhducvo04/brainy

**Pitch:** Cited answers to "why we picked X, who owns it, what is open" from GitHub and Slack, per user access.

## Problem

Rationale lives in PRs and Slack. People outside a channel cannot reconstruct decisions without manual search.

## Built; live behavior not verified

**Scalekit:** Per-user Slack and GitHub pull; write-back (e.g. Slack post) as that user, not a bot. Demo users: Alice (GitHub + Slack #eng and #general); Bob (Slack #general only).

**Cognee:** Per-user datasets; `node_set` tags for source, channel, owner; share from Alice to Bob; refusals when recall lacks permission.

**Respan:** LLM via gateway; `ask` tracing code; 12 scenarios scored in Python (facts, sources, leak = 0). Baseline and improved means **TBD**.

Flow: Scalekit pull → Cognee permanent graph → permission-filtered recall → Respan-traced answer → Python scores. No session memory.

## Planned 3-minute demo (not rehearsed)

1. Problem: scattered decisions.
2. Ingest or pull as Alice and Bob; different memory size.
3. Alice asks the Postgres migration question; answer cites PR + thread.
4. Bob: "I can't see that." Share; Bob gets the same answer.
5. Brief to Alice's Slack via Scalekit (dry-run or live).
6. Eval before/after: means **TBD**; Respan links **TBD**.

## How to run

README quick start: Python 3.12, `uv venv`, `uv pip install -r requirements.txt`, `.env` from `.env.example` (Respan, LLM/embedding, Scalekit). Sample data:

```bash
.venv/bin/python -m brain.cli ingest --user alice --github sample_data/github.json --slack sample_data/slack.json --channels eng,general
.venv/bin/python -m brain.cli ingest --user bob --slack sample_data/slack.json --channels general
.venv/bin/python -m brain.cli ask --user alice "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli share --owner alice --to bob
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
```

Eval: `python -m brain.cli eval --scenarios scenarios/scenarios.json --out runs/baseline.json`, then `python -m eval.score --answers runs/baseline.json`. Use the venv Python. Change and improved score: **TBD**. Live pull needs Scalekit `slack` and `github` connections.

## What is verified

**Recorded in STATUS.md, with keys absent:** Sample ingest; Alice 17 docs, Bob 4; Bob refused pre-share in keyless path; eval outputs 12 rows; scorer runs; tracing code merged (no live trace).

**Not verified:** Real cognee + LLM answers; live Scalekit pull/post; Respan UI trace; eval baseline/improved scores (**TBD**); improvement package; live Slack id-to-name mapping.

Submission: with Duc's approval, open the event PR at `submissions/brainy/SUBMISSION.md` or give the repo link to an organizer by 6:00 PM PT.
