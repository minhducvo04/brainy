"""Turn pulled source items into remember() text plus node_set tags.

Pure functions, no cognee import. Every document starts with a provenance header
line (``[tags: ...]``) and every Slack line carries its own channel, user and ts,
so a recalled chunk can be traced back to its source even when it is cut from the
middle of a document.

Input shapes:
  GitHub: {id, number, title, body, author, url, created_at, repo}
          (``kind``: "pull_request"/"pr" or "issue"; without it a ``/pull/`` url means pr)
  Slack:  {channel, user, ts, text, thread_ts}
"""

from __future__ import annotations

import re
from collections import defaultdict

TAGS_RE = re.compile(r"\[tags: ([^\]]+)\]")
SLACK_LINE_RE = re.compile(r"\[slack #([^\s\]]+) \| ([^|\]]+?) \| ([^\]]+?)\]")


def _clean(value) -> str:
    return str(value or "").strip()


def _tag_header(tags: list[str]) -> str:
    return f"[tags: {', '.join(tags)}]"


def github_kind(item: dict) -> str:
    kind = _clean(item.get("kind")).lower()
    if kind in ("pr", "pull_request"):
        return "pr"
    if kind == "issue":
        return kind
    return "pr" if "/pull/" in _clean(item.get("url")) else "issue"


def github_record(item: dict, owner: str) -> dict:
    """One document per PR or issue."""
    repo = _clean(item.get("repo")) or "unknown"
    author = _clean(item.get("author")) or "unknown"
    kind = github_kind(item)
    tags = ["source:github", f"repo:{repo}", f"owner:{owner}", f"author:{author}"]
    lines = [
        _tag_header(tags),
        f"[github {repo} {kind} #{item.get('number')} | {author} | {_clean(item.get('created_at'))}]"
        f" {_clean(item.get('title'))}",
        f"URL: {_clean(item.get('url'))}",
        "",
        _clean(item.get("body")),
    ]
    return {
        "text": "\n".join(lines).strip() + "\n",
        "node_set": tags,
        "ref": f"github:{repo}#{item.get('number')}",
    }


def slack_line(msg: dict) -> str:
    channel = _clean(msg.get("channel")).lstrip("#") or "unknown"
    return f"[slack #{channel} | {_clean(msg.get('user')) or '?'} | {_clean(msg.get('ts'))}] {_clean(msg.get('text'))}"


def slack_records(messages: list[dict], owner: str, channels: list[str] | None = None) -> list[dict]:
    """One document per thread (a message with no thread_ts is its own thread),
    one line per message, oldest first. ``channels`` filters by channel name."""
    wanted = {c.lstrip("#") for c in channels} if channels else None
    threads: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for msg in messages:
        channel = _clean(msg.get("channel")).lstrip("#")
        if wanted is not None and channel not in wanted:
            continue
        if not _clean(msg.get("text")):
            continue
        root = _clean(msg.get("thread_ts")) or _clean(msg.get("ts"))
        threads[(channel, root)].append(msg)

    records = []
    for (channel, root), msgs in sorted(threads.items()):
        msgs.sort(key=lambda m: float(_clean(m.get("ts")) or 0))
        users = sorted({_clean(m.get("user")) for m in msgs if _clean(m.get("user"))})
        tags = ["source:slack", f"channel:{channel}", f"owner:{owner}"]
        text = "\n".join(
            [_tag_header(tags), f"# Slack #{channel} thread {root} (participants: {', '.join(users)})"]
            + [slack_line(m) for m in msgs]
        )
        records.append({"text": text + "\n", "node_set": tags, "ref": f"slack:#{channel}/{root}"})
    return records


def gmail_record(item: dict, owner: str) -> dict:
    tags = ["source:gmail", f"owner:{owner}"]
    label = f"[gmail | {_clean(item.get('subject')) or '(no subject)'} | {_clean(item.get('from')) or 'unknown'}]"
    return {"text": "\n".join([_tag_header(tags), label, _clean(item.get("body"))]) + "\n",
            "node_set": tags, "ref": f"gmail:{_clean(item.get('id'))}"}


def notion_record(item: dict, owner: str) -> dict:
    tags = ["source:notion", f"owner:{owner}"]
    label = f"[notion | {_clean(item.get('title')) or 'Untitled'}]"
    return {"text": "\n".join([_tag_header(tags), label, f"URL: {_clean(item.get('url'))}",
                               _clean(item.get("body"))]) + "\n",
            "node_set": tags, "ref": f"notion:{_clean(item.get('id'))}"}


def build_records(github_items, slack_messages, owner: str, channels=None,
                  gmail_items=None, notion_items=None) -> list[dict]:
    return ([github_record(i, owner) for i in github_items or []]
            + slack_records(slack_messages or [], owner, channels)
            + [gmail_record(i, owner) for i in gmail_items or []]
            + [notion_record(i, owner) for i in notion_items or []])


def tags_in_text(text: str) -> list[str]:
    """Recover provenance tags from a recalled chunk: tag headers plus Slack line prefixes."""
    found: set[str] = set()
    for match in TAGS_RE.finditer(text or ""):
        found.update(t.strip() for t in match.group(1).split(",") if t.strip())
    for match in SLACK_LINE_RE.finditer(text or ""):
        found.update({"source:slack", f"channel:{match.group(1)}"})
    if "[github " in (text or ""):
        found.add("source:github")
    for source in ("gmail", "notion"):
        if f"[{source} | " in (text or ""):
            found.add(f"source:{source}")
    return sorted(found)
