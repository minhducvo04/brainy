# Working on Brainy (people and agents)

Deadline: **6:00 PM PT**. Keep `main` demoable at every moment.

## Join in 3 steps
1. Clone, set up the venv and `.env` (README quick start). Never commit `.env` or paste keys in chat.
2. Read `STATUS.md`: pick an **open** package from its board and write your name next to it (commit that one-line change first so nobody doubles up).
3. Work on your own branch in your own folder:
   ```bash
   git worktree add .worktrees/<you>-<topic> -b pkg/<topic> main
   ```

## The loop
1. **Build** only the files your package names. Need another file? Ask the planner first.
2. **Verify** with the package's verify line and one real run (a command, an API call, a browser). Paste the proof line into your commit message.
3. **Open a PR** (or tell the planner the branch). Someone who did not write it checks the verify line and runs it once.
4. **Merge** to `main`, then run the demo script in `docs/plans/2026-10-07-company-brain.md`. If it breaks, fixing it beats anything new.
5. Add one line to `docs/log/README.md`: time, what merged, what was verified.

## Rules
- Never print or commit keys. Scalekit holds user tokens; every write goes through Scalekit as the acting user.
- No destructive actions without a confirmation step. Code changes go to a branch and PR, never straight to `main`.
- Commit explicit paths (`git add <files>`), never `git add -A`.
- Plain words in docs and the submission; no em dashes.
- Feature freeze at **5:15 PM**; after that only demo polish, README and `SUBMISSION.md`.

## Agents
Claude Code reads `CLAUDE.md`; Codex and Cursor read `AGENTS.md`. Give an agent one package from the board, its files, and its verify line. A builder never merges its own work.
