# Teammate setup (give this file to your coding agent)

You are a coding agent joining team Brainy at the "Build a Company Brain" hackathon (deadline 6:00 PM PT, freeze 5:15 PM). Use your own tools, models and skills; follow the shared rules below so we all work the same way.

## 1. Set up (about 5 minutes)
1. Clone the repo the owner shared and enter it.
2. Python 3.12 environment: `uv venv --python 3.12 && uv pip install -r requirements.txt` (or `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`).
3. `cp .env.example .env`, then ask your human to fill in the keys. Never print, commit or paste `.env` contents; check a key by its length only.
4. Read, in order: `AGENTS.md` (rules), `CONTRIBUTING.md` (workflow), `STATUS.md` (board), `docs/plans/2026-10-07-company-brain.md` (demo script and packages), `docs/event.md` (judging).
5. Smoke test without keys: `.venv/bin/python -m brain.cli --help` and `.venv/bin/python -m pytest tests -q`. Report both result lines to your human.

## 2. Pick work
1. In `STATUS.md`, choose one open package that fits your human's request. Write their name in Owner, commit only that line, push it, so nobody doubles up.
2. Make your own folder and branch: `git worktree add .worktrees/<name>-<topic> -b pkg/<topic> main`.

## 3. Build, verify, hand over
1. Change only the files your package names. Need another file: ask the team first.
2. Run the package's verify line and one real run; put the proof line in the commit message. Commit explicit paths, never `git add -A`.
3. Push the branch and open a PR to `main`. Someone else reviews and merges; never merge your own work.
4. After a merge, update `STATUS.md` (state column) and add one line to `docs/log/README.md`.

## 4. Rules that never bend
- Keys stay in `.env`; Scalekit holds user tokens; every write goes through Scalekit as the acting user.
- No destructive actions without a confirmation step; no force push; no history rewrite on shared branches.
- Nothing is submitted or posted publicly without the owner's yes.
- Say what is not verified before what works.

## 5. Optional
- The event's `cognee-hackathon-feedback` skill is in `.claude/skills/`; its checkpoint hook is off. Turn it on only if your human wants it.
- `CLAUDE.md` mentions the owner's private skill library; skip that line, use your own skills.
