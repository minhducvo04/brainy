# Plan: Company Brain (draft, 15:20 PT; deadline 18:00)

## Assumptions (Duc can change any)
- Use case: **Decision archaeology for an engineering team**: "why did we pick X, who owns it, what is still open?" answered from **GitHub** (issues, PRs) + **Slack** (threads), with citations. Action: post the answer to the asker's Slack DM, or open a GitHub issue for an open question, through Scalekit as that user.
- Users: alice (eng lead: GitHub + Slack #eng) and bob (new hire: Slack #general only). Bob cannot see the eng decisions until Alice shares her dataset.
- Sample data: a small seeded GitHub repo and Slack channels we control, plus a recorded pull (`sample_data/`) so judges can run without our accounts.
- Stack: Python 3.12, `uv`, cognee >= 1.6.3, scalekit-sdk-python, OpenAI SDK pointed at the Respan gateway, Respan tracing.

## Demo script (3 minutes)
1. Problem: decisions scatter across PRs and Slack.
2. Pull as alice (GitHub + Slack) and as bob (Slack only); show the graph.
3. alice asks "Why did we switch to Postgres and who owns the migration?": answer cites a PR and a thread.
4. bob asks the same: "I can't see that"; alice shares; bob asks again and gets it.
5. Agent posts the brief to alice's Slack DM through Scalekit.
6. Respan: baseline eval score, the change (better node_set tags + prompt), improved score.

## Packages (one owner each, no shared files)
| # | Package | Files | Verify | Owner |
|---|---|---|---|---|
| A | Access: Scalekit pulls for GitHub + Slack per user, write-back post | `brain/pull.py`, `brain/act.py` | real pull for one user prints N items with source tags | Codex lane 0 |
| B | Memory: remember with node_set `source:*`, `channel:*`, `owner:*`; per-user datasets; share | `brain/memory.py` | alice recall finds a PR fact; bob gets nothing; after share bob gets it | Codex lane 1 |
| C | Agent + Respan: recall, answer with citations, traced through the Respan gateway | `brain/agent.py` | one traced run visible in Respan | Claude subagent |
| D | Eval: 10 scenarios (incl. as_user access cases), independent scorer (must_mention + sources), before/after runner | `scenarios/scenarios.json`, `eval/score.py` | runs on a fake answer set and prints a mean | Cursor |
| E | Sample data + recorded pull + README to eval score | `sample_data/`, `README.md` | fresh clone runs the eval with recorded data | Cursor |
| F | Review and demo checks | none | demo script end to end after each merge | Astra + planner |

Order: agree the remember() text format first (one line per Slack message with channel/user/ts; one doc per PR/issue), then A to E in parallel. Freeze features at 17:15; demo polish and SUBMISSION.md until 17:50.

## Needs Duc now
1. Respan key from kickoff, Scalekit account (env URL, client id, secret) into `.env` (never paste them in chat).
2. In Scalekit AgentKit -> Connections: create `slack` and `github`.
3. Confirm or change the use case and users above.
