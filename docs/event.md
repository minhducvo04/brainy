# Event

- Name: Build a Company Brain, SF Tech Week (cognee + Scalekit + Respan)
- Date: Wednesday 2026-10-07, Pacific Time
- Hacking: 3:00 PM. **Submission deadline: 6:00 PM.** Finalist demos 6:15 PM, awards 7:00 PM.
- Source kit: https://github.com/topoteretes/cognee-hackathons/tree/main/cognee-companybrain-scalekit-respan-hackathon-2026-10-07 (copied into `docs/event/`, `examples/`, `SUBMISSION.md`, `.env.example`)
- Team members: Duc (plus agents)

## Rules that shape the build
- Required loop: Scalekit pulls from **2 different apps** for **2 users** with different access, `cognee.remember` tagged by source and scoped per user, **1 agent task** that `recall`s and produces something useful, **Respan traces** scored on a scenario set, a change, a **re-run with before and after**.
- Every write goes through Scalekit with the acting user's identifier, never a shared bot token. Code changes go to a branch and PR.
- LLM calls through the Respan gateway. Never print or commit tokens.
- No destructive actions without a human confirmation step.

## Judging (100)
30 brain quality (cross-source answers with provenance, real workflow, an action) · 20 secure access story (isolation, grant, changed result, live) · 20 evaluation (scenario file, independent scorer, traced runs, before/after) · 15 memory design (node_set provenance, graph vs session, improve) · 10 reproducibility (README to eval score, `.env.example`, sample data) · 5 demo (3 minutes, all three layers).

## Submission
Fill `SUBMISSION.md`, then open a PR to the event repo adding `submissions/<team-name>/SUBMISSION.md`, or hand the link to an organizer. **Opening that PR is public: needs Duc's yes.**

## cognee feedback skill
Copied to `.claude/skills/cognee-hackathon-feedback/`. Its 10-minute checkpoint hook is **not installed** (it interrupts the agent to record mood); turn it on only if Duc says so.
