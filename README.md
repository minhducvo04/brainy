# Brainy

A Company Brain for engineering teams: ask "why did we pick X, who owns it, what is still open?" and get an answer stitched from GitHub and Slack, with citations, showing each person only what they are allowed to see.

Built at "Build a Company Brain" (cognee + Scalekit + Respan), SF Tech Week, 2026-10-07.

```text
Scalekit (per-user pulls: Slack, GitHub)  ->  cognee (per-user datasets, node_set provenance)
        ->  agent (recall + cited answer via Respan gateway)  ->  Slack post as the user
        ->  eval (12 scenarios, independent scorer, before/after)
```

## Quick start (5 minutes)

```bash
git clone <this repo> brainy && cd brainy
uv venv --python 3.12 && uv pip install -r requirements.txt
cp .env.example .env          # fill in RESPAN_API_KEY (+ LLM/EMBEDDING keys) and the three SCALEKIT_* values
```

Run on the recorded sample data (no Slack or GitHub account needed):

```bash
.venv/bin/python -m brain.cli ingest --user alice --github sample_data/github.json --slack sample_data/slack.json --channels eng,general
.venv/bin/python -m brain.cli ingest --user bob --slack sample_data/slack.json --channels general
.venv/bin/python -m brain.cli ask --user alice "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli ask --user bob   "Why did we switch to Postgres and who owns the migration?"   # I can't see that.
.venv/bin/python -m brain.cli share --owner alice --to bob
.venv/bin/python -m brain.cli ask --user bob   "Why did we switch to Postgres and who owns the migration?"   # now answered
```

Evaluate:

```bash
.venv/bin/python -m brain.cli eval --scenarios scenarios/scenarios.json --out runs/baseline.json
.venv/bin/python -m eval.score --answers runs/baseline.json
.venv/bin/python -m eval.score --compare runs/baseline.json runs/improved.json
```

Live data instead of samples (needs Scalekit connections named `slack` and `github`):

```bash
.venv/bin/python -m brain.cli pull --user alice@acme.com --slack-channels eng,general --github-repo owner/name --save
.venv/bin/python -m brain.cli post --user alice@acme.com --to "#eng" --text "brief" --dry-run
```

## Demo (3 minutes)

Run from the repo root after setting up the keys in Quick start.

1. **Reset.** Run `bash scripts/reset_demo.sh`, then the two sample `ingest` commands
   in Quick start. The reset script is coming in another package; this step is
   pending until it lands. Show how PRs and Slack threads feed the brain.
2. **Ask as alice.** Look for a cited answer with the migration reason and owner.
3. **Ask as bob, share, ask again.** Before sharing, expect exactly
   "I can't see that." After sharing, expect an answer citing the shared sources.

```bash
.venv/bin/python -m brain.cli ask --user alice "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli share --owner alice --to bob
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
```

4. **Optional Gmail + Notion.** Once those packages and their fictional samples
   are loaded for alice, ask the search question. Look for citations to the email
   and page, including the reason and open work.

```bash
.venv/bin/python -m brain.cli ask --user alice "Why did we pick Typesense for search and what is still open?"
```

5. **Preview a Slack post as alice through Scalekit.** Replace the text below with
   the cited answer. This dry run shows the intended post without sending it.

```bash
.venv/bin/python -m brain.cli post --user alice --to "#eng" --text "Paste the cited answer here" --dry-run
```

6. **Show Respan traces and eval before/after.** Open the answer traces in Respan.
   Keep the baseline from before the improvement, run the improved version, then
   compare the same scenarios. Mean scores: before **TBD**, after **TBD**. Report
   improvement only after the measured after mean exceeds the before mean.

```bash
.venv/bin/python -m brain.cli eval --scenarios scenarios/scenarios.json --out runs/improved.json
.venv/bin/python -m eval.score --compare runs/baseline.json runs/improved.json
```

## Layout

| Path | What |
|---|---|
| `brain/pull.py`, `brain/act.py` | Scalekit per-user pulls and the Slack post (as the user, never a bot token) |
| `brain/records.py`, `brain/memory.py` | remember() text format, node_set tags, per-user datasets, share, forget |
| `brain/agent.py` | recall, cited answer through the Respan gateway, refusal when it cannot see |
| `eval/score.py`, `scenarios/` | independent scorer (fact match, sources, leak = 0) and 12 scenarios |
| `sample_data/` | fictional Northwind Labs pulls so judges can run without our accounts |

Team workflow: [CONTRIBUTING.md](CONTRIBUTING.md). New teammate or agent: [docs/TEAMMATE-SETUP.md](docs/TEAMMATE-SETUP.md). Live status: [STATUS.md](STATUS.md). Event rules: [docs/event.md](docs/event.md).
