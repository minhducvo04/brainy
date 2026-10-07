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

On a Mac with Apple Silicon, also run the Ladybug fix below.

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

## macOS (Apple Silicon): Ladybug fix

On macOS arm64, cognee 1.6.3 uses ladybug 0.19.0 as its graph database. The ladybug wheel does not include its C library, so the first `cognee.remember` fails with `MigrationError: Relational DB Migrations failed`. The log in `~/.cognee/logs` says `Could not find lbug C API shared library`. The library also needs Homebrew OpenSSL 3.

Run this from the repo root after `uv pip install -r requirements.txt`:

```bash
brew install openssl@3
LIB=.venv/lib/python3.12/site-packages/.cache/lbug-prebuilt/lib
mkdir -p "$LIB"
curl -sSL https://github.com/LadybugDB/ladybug/releases/download/v0.19.0/liblbug-osx-arm64.tar.gz | tar -xz -C "$LIB"
.venv/bin/python -c "import ladybug._lbug_capi"   # no error = fixed
```

Notes:
- Recreating `.venv` removes the fix. Run it again.
- cognee stores its data inside `.venv` (`site-packages/cognee/.cognee_system`). Recreating `.venv` also wipes ingested data. Re-run the ingest commands.

## Layout

| Path | What |
|---|---|
| `brain/pull.py`, `brain/act.py` | Scalekit per-user pulls and the Slack post (as the user, never a bot token) |
| `brain/records.py`, `brain/memory.py` | remember() text format, node_set tags, per-user datasets, share, forget |
| `brain/agent.py` | recall, cited answer through the Respan gateway, refusal when it cannot see |
| `eval/score.py`, `scenarios/` | independent scorer (fact match, sources, leak = 0) and 12 scenarios |
| `sample_data/` | fictional Northwind Labs pulls so judges can run without our accounts |

Team workflow: [CONTRIBUTING.md](CONTRIBUTING.md). New teammate or agent: [docs/TEAMMATE-SETUP.md](docs/TEAMMATE-SETUP.md). Live status: [STATUS.md](STATUS.md). Event rules: [docs/event.md](docs/event.md).
