# Status (update after every merge)

Last update: 2026-10-07 15:30 PT. Deadline 6:00 PM PT; feature freeze 5:15 PM. No `.env` yet: 1, 2, 4, 5 blocked.

## Done on main (built; real cognee, LLM and Scalekit calls NOT yet run: no keys)
- Pull: `brain/pull.py`, `brain/act.py` (Scalekit Slack + GitHub per user, Slack post as the user, dry run and confirm).
- Memory + agent: `brain/records.py`, `brain/memory.py`, `brain/agent.py`, `brain/cli.py` (per-user datasets, node_set tags, share, forget, cited answers, "I can't see that." refusals).
- Eval: `eval/score.py`, `scenarios/scenarios.json` (12), `sample_data/` (fictional Northwind Labs, 4 cross-source decisions).
- Keyless dry run: alice 17 docs, bob 4; bob gets "I can't see that."; eval writes 12 rows and the scorer reads them.

## Package board (write your name in Owner before starting)
| # | Package | Files | Verify | Owner | State |
|---|---|---|---|---|---|
| 1 | First real run: ingest sample data for alice and bob, ask, share, ask | none (run only) | bob refuses, then answers after share | | open, needs `.env` |
| 2 | Baseline eval and score | `runs/` (ignored) | `eval.score` prints a mean | | open, after 1 |
| 3 | Respan tracing on `agent.answer` (replace the `respan_trace` TODO) | `brain/agent.py` | one traced run opens in Respan | Claude subagent (Opus) | building keyless; live check needs key |
| 4 | The improvement (better node_set tags or prompt) + improved eval | `brain/records.py` or `brain/agent.py` | after mean > before mean | | open, after 2 |
| 5 | Live pull: seed a small GitHub repo + Slack channels like the sample, pull as alice and bob | `sample_data/recorded/` | counts printed, one file inspected | | open, needs Scalekit connections |
| 6 | Slack user id to name mapping (live Slack returns ids) | `brain/pull.py` | names in saved file | Claude subagent (Sonnet) | building with faked responses; live check after 5 |
| 7 | Demo script rehearsal + `SUBMISSION.md` | `SUBMISSION.md` | 3-minute run end to end | | open, at 5:15 |

## Needs Duc
- [ ] Commit email: switch to the GitHub no-reply address before the first public push (rewrite the local, unpushed commits).
- [ ] Create the GitHub repo `brainy` (website; the CLI token cannot create repos), then `git remote add origin ... && git push -u origin main`.
- [ ] `.env`: Respan key and the three Scalekit values.
- [ ] Scalekit AgentKit connections `slack` and `github`.
- [ ] Yes before the submission PR to the event repo (public).

## Open questions
- Live Slack may need channel ids instead of `#name`.
- Model slug: `LLM_MODEL` defaults to `openai/gpt-5-mini`; if the gateway rejects it, use `gpt-5-mini`.
