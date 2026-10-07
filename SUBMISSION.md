# Brainy — submission draft

**Team:** Duc Vo (Brainy). **Repo:** https://github.com/minhducvo04/brainy

**One-line pitch:** Ask why the team chose something, who owns it, and what is still open; get a cited answer from GitHub and Slack, scoped to what each person may see.

## Problem

Decisions and rationale scatter across PRs, issues, and Slack threads. People outside a channel or repo cannot reconstruct the story without manual search or repeated questions.

## What it does

**Scalekit (pull and act):** Ingest or live-pull Slack and GitHub per user. Alice uses both apps (eng channels plus repo); Bob uses Slack #general only. Posts back to Slack run as the acting user via Scalekit, not a shared bot token.

**Cognee (remember):** Each user has their own dataset. Ingested items are remembered with `node_set` tags for source, channel, and owner. Recall powers answers with citations; missing access yields a plain refusal. Alice can share her dataset with Bob.

**Respan (gateway, trace, eval):** LLM calls go through the Respan gateway. Agent `ask` is set up for tracing. Twelve scenarios in `scenarios/scenarios.json` are scored by an independent Python scorer (required facts, required sources, zero score on leaks). Baseline and improved runs are wired; numeric scores are **TBD** until keys are in place and package 4 lands.

## 3-minute demo

1. Problem: archaeology across GitHub and Slack.
2. Ingest sample data (or live pull) as Alice and Bob; note different doc counts per user.
3. Alice asks: "Why did we switch to Postgres and who owns the migration?" Answer cites a PR and a thread.
4. Bob asks the same: "I can't see that." Alice shares; Bob asks again and gets the answer.
5. Agent posts a short brief to Alice's Slack through Scalekit (dry-run or live).
6. Eval: baseline mean **TBD**, describe the tagging or prompt change, improved mean **TBD**; Respan trace links **TBD**.

## How to run

From the README quick start: Python 3.12, `uv venv`, `uv pip install -r requirements.txt`, copy `.env.example` to `.env` (Respan key, LLM/embedding keys, three Scalekit values). Judges without our accounts use `sample_data/`:

```bash
.venv/bin/python -m brain.cli ingest --user alice --github sample_data/github.json --slack sample_data/slack.json --channels eng,general
.venv/bin/python -m brain.cli ingest --user bob --slack sample_data/slack.json --channels general
.venv/bin/python -m brain.cli ask --user alice "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli share --owner alice --to bob
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
```

Eval: `brain.cli eval` then `python -m eval.score` (see README). Live pull: `brain.cli pull` with Scalekit connections `slack` and `github`.

## What is verified

**Verified without API keys:** CLI ingest on sample JSON; Alice 17 docs, Bob 4; Bob refused before share in the keyless path; eval writes 12 rows and the scorer reads them; Respan tracing code merged (live trace not checked).

**Not verified yet:** Real cognee graph and LLM answers with production keys; live Scalekit pulls and Slack post as user; Respan trace URL in the UI; eval baseline and improved means (**TBD**); before/after improvement merge; live Slack user id to display name mapping in the wild.
