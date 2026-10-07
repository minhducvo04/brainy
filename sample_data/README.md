# Sample data: Northwind Labs (fictional)

Everything here is invented. Northwind Labs, its people, repo and messages do not exist.
The files are recorded pulls in the shape the pull step produces, so the eval runs without any accounts.

| File | Shape |
|---|---|
| `github.json` | list of `{id, number, kind, title, body, author, url, created_at, repo}` (issues and PRs) |
| `slack.json` | list of `{channel, user, ts, text, thread_ts}` |

## People and access

| User | Role | Sees |
|---|---|---|
| alice | engineering lead | GitHub, Slack `#eng`, Slack `#general` |
| bob | new hire | Slack `#general` only |
| carol, dave, erin | teammates | authors only, not demo users |

Each Slack message carries its channel, so access is a filter on `channel`. Bob has no GitHub connection.

## Planted decisions

Each needs both sources for the full answer. Bob can only see the vague hint posted in `#general`.

| Decision | GitHub has | Slack `#eng` has |
|---|---|---|
| PostgreSQL migration | PR 42: cutover October 14; issue 44: rollback plan open | Carol owns it; why: JSONB, row locks, replication lag |
| Rate limiter | PR 51: token bucket in Redis, 100 requests per minute | Dave owns it; why: mobile bursts |
| On-call rotation | Issue 58: weekly from November 2 | Erin owns it; why: pager fatigue (the date is also public in `#general`) |
| v1 API deprecation | PR 63: sunset December 1 | Alice accountable; why: no pagination limits |
