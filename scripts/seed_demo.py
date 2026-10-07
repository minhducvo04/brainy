"""Seed the made-up Northwind data into a live Slack workspace and a public GitHub repo.

Default is a dry run (no network). ``--live`` asks y/N before each target group.
Slack posts go through ``brain.act.post_brief`` (Scalekit, as ``--user``), top level,
with the original author as a prefix ("carol: ..."). GitHub gets issues only, via
``gh issue create``; PRs become issues titled "[PR #n] ...".
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import OrderedDict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "sample_data"
REPO = "minhducvo04/brainy-demo-data"


def slack_groups() -> "OrderedDict[str, list[dict]]":
    msgs = sorted(json.loads((DATA / "slack.json").read_text()), key=lambda m: float(m["ts"]))
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for m in msgs:
        groups.setdefault(m["channel"], []).append(m)
    return groups


def github_issues() -> list[dict]:
    out = []
    for it in json.loads((DATA / "github.json").read_text()):
        pr = it["kind"] == "pull_request"
        title = f"[PR #{it['number']}] {it['title']}" if pr else it["title"]
        body = (
            f"{it['body']}\n\n---\nOriginal {'pull request' if pr else 'issue'} "
            f"#{it['number']} by {it['author']} in {it['repo']}, opened {it['created_at']}.\n"
            f"(Made-up Northwind Labs demo data.)"
        )
        out.append({"title": title, "body": body})
    return out


def confirm(question: str) -> bool:
    return input(f"{question} [y/N] ").strip().lower() == "y"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="really post (default is a dry run)")
    ap.add_argument("--dry-run", action="store_true", help="print only (the default)")
    ap.add_argument("--user", default="alice", help="Scalekit identifier that posts to Slack")
    ap.add_argument("--connection", default="slack")
    ap.add_argument("--repo", default=REPO)
    args = ap.parse_args()
    live = args.live and not args.dry_run

    groups, issues = slack_groups(), github_issues()
    print(f"[{'LIVE' if live else 'DRY RUN'}] Slack as {args.user}, GitHub repo {args.repo}")

    for ch, msgs in groups.items():
        print(f"\n== Slack #{ch}: {len(msgs)} posts ==")
        for m in msgs:
            print(f"  #{ch} | as {m['user']} | {m['user']}: {m['text']}")
        if live and confirm(f"Post these {len(msgs)} messages to #{ch} as {args.user}?"):
            from brain.act import post_brief

            for m in msgs:
                post_brief(args.user, f"#{ch}", f"{m['user']}: {m['text']}",
                           connection=args.connection, yes=True)

    print(f"\n== GitHub {args.repo}: {len(issues)} issues ==")
    for i in issues:
        print(f"  TITLE: {i['title']}\n  BODY: {i['body']}\n")
    if live and confirm(f"Create these {len(issues)} issues in {args.repo}?"):
        for i in issues:
            subprocess.run(["gh", "issue", "create", "--repo", args.repo,
                            "--title", i["title"], "--body", i["body"]], check=True)

    counts = ", ".join(f"#{c}={len(m)}" for c, m in groups.items())
    print(f"COUNTS: slack {counts}; total slack={sum(map(len, groups.values()))}; github issues={len(issues)}"
          f"{'' if live else ' (nothing sent)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
