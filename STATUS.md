# Status (update after every merge)

Last update: 2026-10-07 16:15 PT. Deadline 6:00 PM PT; feature freeze 5:15 PM. No `.env` yet: 1, 2, 4, 5 blocked.

## Done on main (built; real cognee, LLM and Scalekit calls NOT yet run: no keys)
- Pull: `brain/pull.py`, `brain/act.py` (Scalekit Slack + GitHub per user, Slack post as the user, dry run and confirm).
- Memory + agent: `brain/records.py`, `brain/memory.py`, `brain/agent.py`, `brain/cli.py` (per-user datasets, node_set tags, share, forget, cited answers, "I can't see that." refusals).
- Eval: `eval/score.py`, `scenarios/scenarios.json` (12), `sample_data/` (fictional Northwind Labs, 4 cross-source decisions).
- Keyless dry run: alice 17 docs, bob 4; bob gets "I can't see that."; eval writes 12 rows and the scorer reads them.

## Package board (write your name in Owner before starting)
| # | Package | Files | Verify | Owner | State |
|---|---|---|---|---|---|
| 1 | First real run: ingest sample data for alice and bob, ask, share, ask | none (run only) | bob refuses, then answers after share | Planner | VERIFIED 16:13: alice 17 docs, bob 4; alice cited answer (Carol owns, 8 sources); bob "I can't see that."; after share bob cited answer from both brains |
| 2 | Baseline eval and score | `runs/` (ignored) | `eval.score` prints a mean | Claude subagent (Sonnet, medium) | running (Sonnet subagent), share revoked for baseline |
| 3 | Respan tracing on `agent.answer` (replace the `respan_trace` TODO) | `brain/agent.py` | one traced run opens in Respan | Claude subagent (Opus) | merged b595e8d; keyless + fake-key checked; live trace needs key |
| 4 | The improvement (prompt + labeled context) + improved eval | `brain/agent.py` | after mean > before mean | Codex Sol 2 (medium); review Astra | building; measure after 1 and 2 |
| 5 | Live pull: seed script, then pull as alice and bob | `scripts/seed_demo.py`, `sample_data/recorded/` | dry run counts; live pull counts | Claude Sonnet built 06626be; review Astra | in review; live needs `.env`, connections, Duc yes |
| 6 | Slack user id to name mapping (live Slack returns ids) | `brain/pull.py` | names in saved file | Claude subagent (Sonnet) | merged da384dd; fake Slack test passes; tool name `slack_get_user_info` unverified live |
| 8 | Gmail + Notion pull | `brain/pull.py`, `brain/records.py`, `brain/cli.py`, `tests/test_gmail_notion.py` | fake-response tests pass; live cites `[gmail ...]`, `[notion ...]` | Codex Astra built ce166b3; review Claude Opus lane | fix-first (pull failure loses other sources); back with author |
| 9 | Fictional Gmail + Notion sample data (Typesense decision) | `sample_data/gmail.json`, `sample_data/notion.json`, `sample_data/README.md` | records builder tags both | Codex Sol 1 (light); review Claude Opus lane | building |
| 7 | Demo script rehearsal + `SUBMISSION.md` | `SUBMISSION.md` | 3-minute run end to end | Cursor (composer-2.5) drafted 5b896ab; review Astra | in review; rehearsal at 5:15 |

## Needs Duc
- [x] Example email sent (to the +alice alias) and private Notion page created 16:11.
- [ ] Look in the Respan dashboard for traces named `answer` (package 3 live check).
- [ ] Name the Slack workspace for the live seed (yes given).
- [ ] Scalekit connections `gmail` and `notion` too.
- Lanes: Codex hackathon lane 0 Astra (gpt-6-astra, high) = reviewer/mentor; lane 1 Sol light, lane 2 Sol medium = builders; Claude Opus lane (Hackathon lane 0) = reviewer of Astra's own work; Cursor headless = docs/tests. Codex via `codex queue`.
- [x] Commit email: rewritten to the GitHub no-reply address (backup branch `backup/main-before-email`).
- [x] Repo https://github.com/minhducvo04/brainy (public); main pushed at e62941e.
- [x] `.env` saved (real cognee + LLM + Respan calls work).
- [ ] Scalekit AgentKit connections `slack` and `github`.
- [ ] Yes before the submission PR to the event repo (public).

## Open questions
- Live Slack may need channel ids instead of `#name`.
- Model slug: `LLM_MODEL` defaults to `openai/gpt-5-mini`; if the gateway rejects it, use `gpt-5-mini`.
- Tests need `PYTHONPATH=.` (plain `pytest -q` fails at collection on `brain`/`eval` imports).
- `respan-ai` and its OpenTelemetry deps are now installed in the shared `.venv`.
