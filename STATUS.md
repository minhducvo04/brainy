# Status (update after every merge)

Last update: 2026-10-07 16:05 PT. Deadline 6:00 PM PT; feature freeze 5:15 PM. No `.env` yet: 1, 2, 4, 5 blocked.

## Done on main (built; real cognee, LLM and Scalekit calls NOT yet run: no keys)
- Pull: `brain/pull.py`, `brain/act.py` (Scalekit Slack + GitHub per user, Slack post as the user, dry run and confirm).
- Memory + agent: `brain/records.py`, `brain/memory.py`, `brain/agent.py`, `brain/cli.py` (per-user datasets, node_set tags, share, forget, cited answers, "I can't see that." refusals).
- Eval: `eval/score.py`, `scenarios/scenarios.json` (12), `sample_data/` (fictional Northwind Labs, 4 cross-source decisions).
- Keyless dry run: alice 17 docs, bob 4; bob gets "I can't see that."; eval writes 12 rows and the scorer reads them.

## Package board (write your name in Owner before starting)
| # | Package | Files | Verify | Owner | State |
|---|---|---|---|---|---|
| 1 | First real run: ingest sample data for alice and bob, ask, share, ask | none (run only) | bob refuses, then answers after share | Planner | waiting on Duc saving `.env` |
| 2 | Baseline eval and score | `runs/` (ignored) | `eval.score` prints a mean | Claude subagent (Sonnet, medium) | queued, after 1 |
| 3 | Respan tracing on `agent.answer` (replace the `respan_trace` TODO) | `brain/agent.py` | one traced run opens in Respan | Claude subagent (Opus) | merged b595e8d; keyless + fake-key checked; live trace needs key |
| 4 | The improvement (better node_set tags or prompt) + improved eval | `brain/records.py` or `brain/agent.py` | after mean > before mean | Claude subagent (Opus, medium) | queued, after 2 and 8 |
| 5 | Live pull: seed a small GitHub repo + Slack channels like the sample, pull as alice and bob | `sample_data/recorded/` | counts printed, one file inspected | Codex Sol 0 (default, medium) | brief sent to Duc to paste; live needs Scalekit connections |
| 6 | Slack user id to name mapping (live Slack returns ids) | `brain/pull.py` | names in saved file | Claude subagent (Sonnet) | merged da384dd; fake Slack test passes; tool name `slack_get_user_info` unverified live |
| 8 | Gmail + Notion pull (one fictional email, one Notion page) | `brain/pull.py`, `brain/records.py`, `brain/cli.py`, `tests/test_gmail_notion.py` | fake-response test passes; live pull cites `[gmail ...]` and `[notion ...]` | Codex Sol 1 (default, medium) | brief sent to Duc to paste; live needs Scalekit `gmail` + `notion` |
| 7 | Demo script rehearsal + `SUBMISSION.md` | `SUBMISSION.md` | 3-minute run end to end | Cursor (composer-2.5, headless) | drafting `SUBMISSION.md` now; rehearsal at 5:15 |

## Needs Duc
- [ ] Paste the three Codex briefs from `docs/plans/2026-10-07-round2-briefs.md` (Sol 0, Sol 1, Astra); no Codex CLI on this Mac.
- [ ] Yes on the example email + Notion page text (planner shows it first).
- [ ] Scalekit connections `gmail` and `notion` too.
- Reviewer for every package: Codex Astra (default, high).
- [x] Commit email: rewritten to the GitHub no-reply address (backup branch `backup/main-before-email`).
- [x] Repo https://github.com/minhducvo04/brainy (public); main pushed at e62941e.
- [ ] `.env`: Respan key and the three Scalekit values.
- [ ] Scalekit AgentKit connections `slack` and `github`.
- [ ] Yes before the submission PR to the event repo (public).

## Open questions
- Live Slack may need channel ids instead of `#name`.
- Model slug: `LLM_MODEL` defaults to `openai/gpt-5-mini`; if the gateway rejects it, use `gpt-5-mini`.
- Tests need `PYTHONPATH=.` (plain `pytest -q` fails at collection on `brain`/`eval` imports).
- `respan-ai` and its OpenTelemetry deps are now installed in the shared `.venv`.
