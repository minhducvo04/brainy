# Claude Code entry point

@AGENTS.md

- Claude is the planner in the home chat; subagents get explicit models (Fable may be spent; use Opus or Sonnet).
- Shared skills: `~/Projects/kyra/.claude/skills` (`brief`, `lane-routing`, `test-impact`, `kyra-humanizer` for the submission text).

## Starting a new chat here
1. Read `STATUS.md` (board, what is verified, what needs Duc), then `docs/plans/2026-10-07-company-brain.md`.
2. You are the planner: give open packages to lanes per `CONTRIBUTING.md`, merge only after a non-author check, update `STATUS.md` after every merge.
3. Check `.env` exists by length only; never print it.
