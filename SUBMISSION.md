# Brainy submission draft

**Team:** Duc Vo (Brainy). **Repo:** https://github.com/minhducvo04/brainy

**Pitch:** Cited answers to "why we picked X, who owns it, what is open" from GitHub and Slack, per user access.

## Problem

Rationale lives in PRs and Slack. People outside a channel cannot reconstruct decisions without manual search.

## Built

**Scalekit:** Per-user pulls for Slack, GitHub, Gmail, and Notion are built and unit tested. Live credentials authenticate and per-user connected accounts are created. Live Gmail sign-in is blocked because the Scalekit Gmail connection has no Google OAuth client yet; the demo uses recorded Northwind sample data.

**Cognee:** Per-user datasets, permission tags, share Alice to Bob, refusals without access.

**Respan:** Every LLM call goes through the gateway. Traces export (HTTP 200, workflow span `answer.workflow`).

## Verified today (2026-10-07, real cognee + LLM via Respan)

**Access:** Alice gets a cited answer on the Postgres migration (Carol owns it; JSONB, row locks, replication lag). Bob gets "I can't see that." After Alice shares, Bob gets the cited answer from both brains.

**Eval:** Set 1 (12 scenarios): mean **1.000**, too easy. Held-out set 2 (10 scenarios, never seen by prompt builder): baseline **0.900**. The miss is a mixed question where Bob refuses everything instead of answering the public part. We tried provenance labels on each chunk plus a stricter citation prompt: **0.877**, one scenario lost a fact, reverted. This reverted baseline is the honest result; next step is the mixed-question refusal.

## Demo and run

Alice/Bob ingest from sample data, ask migration question, share, Bob asks again; show Respan trace. README: Python 3.12, `uv venv`, `uv pip install -r requirements.txt`, `.env` from `.env.example`. Eval: `python -m brain.cli eval` plus `python -m eval.score` on set 1 or held-out set 2 in the repo.

## Gaps

Live Gmail pull waits on a Google OAuth client in Scalekit (recorded Gmail and Notion ingest works). Mixed public/private answers not fixed. Live Slack id-to-name mapping not fully verified.

Submission with Duc's approval: event PR at `submissions/brainy/SUBMISSION.md` or repo link to organizers by 6:00 PM PT.
