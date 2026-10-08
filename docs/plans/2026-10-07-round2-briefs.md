# Round 2 briefs (16:05 PT; feature freeze 17:15, deadline 18:00)

Each lane: work in `~/Projects/hackathon`, read `AGENTS.md` and `CONTRIBUTING.md` first and say so in your first reply.
Make your own worktree: `git worktree add .worktrees/<lane>-<topic> -b pkg/<topic> main`.
Commit explicit paths only, never push, never merge, never read or print `.env` (check by running code, not by reading it).
Hand back: branch, commit sha, verify output line, what is NOT verified. Under 150 words.
Tests run with `PYTHONPATH=. .venv/bin/pytest -q` (shared venv at `~/Projects/hackathon/.venv`).

## Codex Sol lane 0 (default model, medium): package 5, live seed + pull
Goal: put the fictional Northwind decisions from `sample_data/` into a real Slack workspace and a real public GitHub repo, then pull them back through Scalekit as alice and bob.
- Files: new `scripts/seed_demo.py`, `sample_data/recorded/` (pulled output). Do not edit `brain/`.
- `scripts/seed_demo.py --dry-run` prints every post and issue it would create from `sample_data/slack.json` and `sample_data/github.json`; without `--dry-run` it asks y/N before each target. Slack posts go through `brain.act` (Scalekit, as the user). GitHub: issues only, through Scalekit if a create tool exists, else `gh issue create` on repo `minhducvo04/brainy-demo-data` (Duc approved public for made-up data; the planner creates the repo).
- Everything is made up. No real names, no real company.
- Verify: dry run output, then (needs Scalekit `slack` and `github` connections) `python -m brain.cli pull ... --save` for alice prints counts and one saved file shows names, not Slack ids. Live steps: say NOT verified if connections are missing.

## Codex Sol lane 1 (default model, medium): package 8, Gmail + Notion pull
Goal: the brain also learns from one email (Gmail) and one Notion page, through Scalekit as the user, with citations like `[gmail | subject | from]` and `[notion | page title]`.
- Files: `brain/pull.py`, `brain/records.py`, `brain/cli.py`, new `tests/test_gmail_notion.py`. Nothing else.
- Pull through the same `actions.execute_tool` path as Slack/GitHub. Find the real Scalekit tool names for Gmail (list/fetch messages, query by subject) and Notion (search + page content) from the Scalekit docs; mark any name you could not confirm with `# not seen live`.
- Records: tags `source:gmail`, `source:notion`, `owner:<user>`; one record per email, one per page.
- CLI: `pull` gets `--gmail-query` and `--notion-query`; `ingest` gets `--gmail` and `--notion` json paths.
- Verify: unit test with faked tool responses (email and page in, records with tags and citation labels out); existing tests still pass. Live pull NOT verified until Duc connects `gmail` and `notion` in Scalekit.

## Codex Astra lane 2 (default model, high): reviewer
Review each hand-back the planner sends you (packages 5, 8, and Claude/Cursor packages). You never review your own work; you have none this round.
For each: read the diff (`git diff main...<branch>`), run its verify line once, run the test command. Verdict: `merge` or `fix-first: <list>`. Small fixes: commit on the author's branch with a note. Add one lesson line per package to `docs/log/README.md` only when the planner asks.

## Cursor (headless, composer-2.5, low): package 7, SUBMISSION.md draft
Run by the planner with `cursor-agent -p`. Brief is in the command.

## Claude subagents (dispatched by the planner)
- Package 2 baseline eval: Sonnet, medium, after package 1 passes.
- Package 4 improvement: Opus, medium, after package 2 and after package 8 merges (both touch `brain/records.py`).
