# Status (update after every merge)

Last update: 2026-10-07 16:29 PT. Deadline 6:00 PM PT; feature freeze 5:15 PM. No `.env` yet: 1, 2, 4, 5 blocked.

## Done on main (built; real cognee, LLM and Scalekit calls NOT yet run: no keys)
- Pull: `brain/pull.py`, `brain/act.py` (Scalekit Slack + GitHub per user, Slack post as the user, dry run and confirm).
- Memory + agent: `brain/records.py`, `brain/memory.py`, `brain/agent.py`, `brain/cli.py` (per-user datasets, node_set tags, share, forget, cited answers, "I can't see that." refusals).
- Eval: `eval/score.py`, `scenarios/scenarios.json` (12), `sample_data/` (fictional Northwind Labs, 4 cross-source decisions).
- Keyless dry run: alice 17 docs, bob 4; bob gets "I can't see that."; eval writes 12 rows and the scorer reads them.

## Package board (write your name in Owner before starting)
| # | Package | Files | Verify | Owner | State |
|---|---|---|---|---|---|
| 1 | First real run: ingest sample data for alice and bob, ask, share, ask | none (run only) | bob refuses, then answers after share | Planner | VERIFIED 16:13: alice 17 docs, bob 4; alice cited answer (Carol owns, 8 sources); bob "I can't see that."; after share bob cited answer from both brains |
| 2 | Baseline eval and score | `runs/` (ignored) | `eval.score` prints a mean | Planner (subagent hit env issue) | VERIFIED 16:25: 12/12, mean 1.000 (ceiling; see package 10) |
| 3 | Respan tracing on `agent.answer` (replace the `respan_trace` TODO) | `brain/agent.py` | one traced run opens in Respan | Claude subagent (Opus) | merged b595e8d; keyless + fake-key checked; live trace needs key |
| 4 | The improvement (prompt + labeled context) + improved eval | `brain/agent.py` | v2 after mean > v2 before mean | Codex Sol 2 built 2591c00; review Astra | in review; measure on package 10 set |
| 5 | Live pull: seed script, then pull as alice and bob | `scripts/seed_demo.py`, `sample_data/recorded/` | dry run counts; live pull counts | Claude Sonnet; review Astra (fixed GitHub to Scalekit) | MERGED 94e20b4 (dry run 19 posts, 7 issues); live seed waits on Slack workspace + connections |
| 6 | Slack user id to name mapping (live Slack returns ids) | `brain/pull.py` | names in saved file | Claude subagent (Sonnet) | merged da384dd; fake Slack test passes; tool name `slack_get_user_info` unverified live |
| 8 | Gmail + Notion pull | `brain/pull.py`, `brain/records.py`, `brain/cli.py`, `tests/test_gmail_notion.py` | fake tests pass; live cites gmail/notion | Codex Astra; review Claude Opus lane | fix done ee44bd9 (19 tests); re-check pending |
| 9 | Fictional Gmail + Notion sample data (Typesense) | `sample_data/gmail.json`, `sample_data/notion.json`, `sample_data/README.md` | records builder tags both | Codex Sol 1 built b63c2f8; review Claude Opus lane | in review |
| 10 | Harder held-out eval set (builders must not see it) | `scenarios/scenarios_v2.json` | valid JSON, 10 scenarios, scorer reads it | Cursor (composer-2.5) | building; then baseline v2 before package 4 merges |
| 11 | Demo reset script | `scripts/reset_demo.sh` | bash -n passes; planner runs it | Codex Sol 1 | building |
| 12 | README demo section | `README.md` | listed commands parse | Codex Sol 2 | building |
| 7 | Demo script rehearsal + `SUBMISSION.md` | `SUBMISSION.md` | 3-minute run end to end | Cursor; review Astra | draft MERGED 94e20b4 (426 words, scores TBD); rehearsal at 5:15 |

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
- Embedding model changed between 16:17 and 16:19 (bge-small 384 to text-embedding-3-large 3072); re-ingested at 16:20. Do not change EMBEDDING_* in `.env` again without a re-ingest.
- Shares cannot be revoked; demo reset = move `.cognee_system` and `.cognee_data` to `runs/` and re-ingest alice + bob (~1.5 min).
- Live Slack may need channel ids instead of `#name`.
- Model slug: `LLM_MODEL` defaults to `openai/gpt-5-mini`; if the gateway rejects it, use `gpt-5-mini`.
- Tests need `PYTHONPATH=.` (plain `pytest -q` fails at collection on `brain`/`eval` imports).
- `respan-ai` and its OpenTelemetry deps are now installed in the shared `.venv`.
