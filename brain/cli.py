"""Company Brain CLI.

  python -m brain.cli ingest --user alice --github sample_data/github.json --slack sample_data/slack.json --channels eng,general
  python -m brain.cli ask --user bob "Why did we switch to Postgres?"
  python -m brain.cli share --owner alice --to bob
  python -m brain.cli forget --user alice
  python -m brain.cli eval --scenarios scenarios/scenarios.json --out runs/baseline.json
  python -m brain.cli pull --user alice@acme.com --slack-channels eng,general --github-repo owner/name --save
  python -m brain.cli post --user alice@acme.com --to "#eng" --text "brief" --dry-run

Scenario file: a list (or {"scenarios": [...]}) of {id, question, as_user|user}.
eval writes [{id, answer, sources}] for the scorer.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path


def _load_json(path: str | None):
    if not path:
        return []
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):  # tolerate {"items": [...]} / {"messages": [...]}
        for key in ("items", "messages", "data"):
            if isinstance(data.get(key), list):
                return data[key]
    return data


async def cmd_ingest(args) -> None:
    from brain import memory
    from brain.records import build_records

    channels = [c.strip() for c in args.channels.split(",")] if args.channels else None
    records = build_records(_load_json(args.github), _load_json(args.slack), memory.email_for(args.user), channels)
    print(f"{len(records)} documents for {args.user}")
    print(json.dumps(await memory.remember(records, args.user)))


async def cmd_ask(args) -> None:
    from brain.agent import answer

    print(json.dumps(await answer(args.question, args.user), indent=2))


async def cmd_share(args) -> None:
    from brain import memory

    print(json.dumps(await memory.share(args.owner, args.to, args.permission)))


async def cmd_forget(args) -> None:
    from brain import memory

    if not args.yes and input(f"Forget {memory.dataset_for(args.user)}? type yes: ").strip() != "yes":
        print("cancelled")
        return
    print(await memory.forget(args.user))


async def cmd_eval(args) -> None:
    from brain.agent import answer

    data = json.loads(Path(args.scenarios).read_text())
    scenarios = data["scenarios"] if isinstance(data, dict) else data
    rows = []
    for sc in scenarios:
        user = sc.get("as_user") or sc.get("user")
        result = await answer(sc["question"], user)
        rows.append({"id": sc["id"], "answer": result["answer"], "sources": result["sources"]})
        print(f"{sc['id']} ({user}): {len(result['sources'])} sources")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))
    print(f"wrote {len(rows)} rows to {out}")


async def cmd_pull(args) -> None:
    from brain.pull import pull

    channels = [c.strip() for c in args.slack_channels.split(",") if c.strip()] if args.slack_channels else None
    result = pull(
        args.user,
        slack_channels=channels,
        github_repo=args.github_repo,
        slack_connection=args.slack_connection,
        github_connection=args.github_connection,
        limit=args.limit,
        save_dir=args.save,
    )
    print(json.dumps({source: len(items) for source, items in result.items()}))


async def cmd_post(args) -> None:
    from brain.act import post_brief

    post_brief(args.user, args.to, args.text, connection=args.slack_connection, yes=args.yes, dry_run=args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="brain", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ingest", help="remember pulled GitHub + Slack items for a user")
    s.add_argument("--user", required=True)
    s.add_argument("--github", help="JSON list of GitHub PRs/issues")
    s.add_argument("--slack", help="JSON list of Slack messages")
    s.add_argument("--channels", help="comma-separated Slack channels to keep (default: all)")
    s.set_defaults(fn=cmd_ingest)

    s = sub.add_parser("ask", help="answer a question from the user's readable memory")
    s.add_argument("--user", required=True)
    s.add_argument("question")
    s.set_defaults(fn=cmd_ask)

    s = sub.add_parser("share", help="owner grants read on their brain to another user")
    s.add_argument("--owner", required=True)
    s.add_argument("--to", required=True)
    s.add_argument("--permission", default="read")
    s.set_defaults(fn=cmd_share)

    s = sub.add_parser("forget", help="delete a user's brain dataset (asks for confirmation)")
    s.add_argument("--user", required=True)
    s.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    s.set_defaults(fn=cmd_forget)

    s = sub.add_parser("eval", help="run scenarios and write [{id, answer, sources}]")
    s.add_argument("--scenarios", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_eval)

    s = sub.add_parser("pull", help="pull Slack + GitHub as one user through Scalekit")
    s.add_argument("--user", required=True, help="Scalekit identifier, e.g. alice@acme.com")
    s.add_argument("--slack-channels", help="comma-separated channels (#name or id)")
    s.add_argument("--github-repo", help="owner/name")
    s.add_argument("--slack-connection", default="slack")
    s.add_argument("--github-connection", default="github")
    s.add_argument("--limit", type=int, default=200, help="max items per channel or list")
    s.add_argument(
        "--save", nargs="?", const="sample_data/recorded", default=None,
        help="write <dir>/<user>-<source>.json for ingest (default dir: sample_data/recorded)",
    )
    s.set_defaults(fn=cmd_pull)

    s = sub.add_parser("post", help="post a brief to Slack as the user through Scalekit")
    s.add_argument("--user", required=True)
    s.add_argument("--to", required=True, help="channel (#name or id) or user id for a DM")
    s.add_argument("--text", required=True)
    s.add_argument("--slack-connection", default="slack")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="print what would be sent, send nothing")
    g.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    s.set_defaults(fn=cmd_post)
    return p


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    asyncio.run(args.fn(args))


if __name__ == "__main__":
    main()
