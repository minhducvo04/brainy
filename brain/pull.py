"""Per-user pulls from Slack and GitHub through Scalekit AgentKit.

Follows examples/scalekit_to_cognee.py: authorize once per user per connection
(the link is printed when the account is not ACTIVE), then ``execute_tool`` with
``identifier=<user>`` so Scalekit adds that user's own token. No bot tokens.

Output is normalized to the recorded shapes in sample_data/:
  GitHub: {id, number, kind, title, body, author, url, created_at, repo}
  Slack:  {channel, user, ts, text, thread_ts}  (thread_ts is None for a thread root)

Tool names come from the Scalekit connector docs (docs.scalekit.com/agentkit/connectors/
slack and /github). The raw output shape of each tool was not seen live, so the
normalizers accept a bare list or a dict wrapping one under a common key.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

SLACK_HISTORY_TOOL = "slack_fetch_conversation_history"  # inputs: channel, limit, cursor
SLACK_REPLIES_TOOL = "slack_get_conversation_replies"  # inputs: channel, ts, limit, cursor
SLACK_USER_TOOL = "slack_get_user_info"  # inputs: user (Slack users.info); name not seen live
GITHUB_ISSUES_TOOL = "github_issues_list"  # inputs: owner, repo, state, per_page, page
GITHUB_PULLS_TOOL = "github_pull_requests_list"  # inputs: owner, repo, state, per_page, page


def scalekit_actions():
    from dotenv import load_dotenv
    from scalekit import ScalekitClient

    load_dotenv()
    client = ScalekitClient(
        env_url=os.environ["SCALEKIT_ENVIRONMENT_URL"],
        client_id=os.environ["SCALEKIT_CLIENT_ID"],
        client_secret=os.environ["SCALEKIT_CLIENT_SECRET"],
    )
    return client.actions


def ensure_authorized(actions, connection_name: str, identifier: str) -> None:
    """Print the consent link once per user per connection; no-op when already ACTIVE."""
    account = actions.get_or_create_connected_account(connection_name=connection_name, identifier=identifier)
    if account.connected_account.status == "ACTIVE":
        return
    link = actions.get_authorization_link(connection_name=connection_name, identifier=identifier)
    print(f"Authorize {connection_name} for {identifier}: {link.link}")
    input("Press Enter after authorizing...")


def _items(data, *keys) -> list:
    """Find the list in a tool result: a bare list, or a dict holding one under a known key."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in (*keys, "items", "data", "results", "result", "body", "response"):
            value = data.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                found = _items(value, *keys)
                if found:
                    return found
    return []


def _next_cursor(data) -> str:
    if isinstance(data, dict):
        meta = data.get("response_metadata") or {}
        return str(meta.get("next_cursor") or "").strip()
    return ""


# --- Slack -----------------------------------------------------------------


def normalize_slack_message(raw: dict, channel: str) -> dict:
    ts = str(raw.get("ts") or "")
    thread_ts = raw.get("thread_ts")
    thread_ts = str(thread_ts) if thread_ts and str(thread_ts) != ts else None
    return {
        "channel": channel.lstrip("#"),
        "user": str(raw.get("user") or raw.get("username") or raw.get("bot_id") or "?"),
        "ts": ts,
        "text": str(raw.get("text") or "").strip(),
        "thread_ts": thread_ts,
    }


def normalize_slack(raw_messages: list[dict], channel: str) -> list[dict]:
    """Dedupe by ts, drop empty texts, oldest first."""
    seen: dict[str, dict] = {}
    for raw in raw_messages:
        msg = normalize_slack_message(raw, channel)
        if msg["ts"] and msg["text"]:
            seen.setdefault(msg["ts"], msg)
    return sorted(seen.values(), key=lambda m: float(m["ts"] or 0))


_MENTION = re.compile(r"<@([UW][A-Z0-9]+)(?:\|[^>]*)?>")
_USER_ID = re.compile(r"^[UW][A-Z0-9]{2,}$")


def _display_name(data) -> str:
    """Pull a name out of a users.info result (profile display name, then real name, then name)."""
    if isinstance(data, dict):
        user = data.get("user") if isinstance(data.get("user"), dict) else data
        for source in (user.get("profile") or {}, user):
            if not isinstance(source, dict):
                continue
            for key in ("display_name", "real_name", "name"):
                if str(source.get(key) or "").strip():
                    return str(source[key]).strip()
        for key in ("data", "result", "response", "body"):
            if isinstance(data.get(key), dict):
                found = _display_name(data[key])
                if found:
                    return found
    return ""


def resolve_slack_names(actions, connection: str, user: str, msgs: list[dict], cache: dict[str, str]) -> None:
    """Replace Slack user ids (author field and <@U...> mentions) with names, in place.
    ``cache`` maps id -> name for one pull; a failed lookup keeps the raw id."""

    def name_for(uid: str) -> str:
        if uid not in cache:
            try:
                result = actions.execute_tool(
                    tool_name=SLACK_USER_TOOL, tool_input={"user": uid}, connection_name=connection, identifier=user
                )
                cache[uid] = _display_name(result.data) or uid
            except Exception:
                cache[uid] = uid
        return cache[uid]

    for msg in msgs:
        if _USER_ID.match(msg["user"]):
            msg["user"] = name_for(msg["user"])
        msg["text"] = _MENTION.sub(lambda m: "@" + name_for(m.group(1)), msg["text"])


def _has_replies(raw: dict) -> bool:
    return int(raw.get("reply_count") or 0) > 0 or (raw.get("thread_ts") and raw.get("thread_ts") == raw.get("ts"))


def pull_slack(actions, connection: str, user: str, channels: list[str], limit: int = 200, threads: bool = True):
    out: list[dict] = []
    names: dict[str, str] = {}
    for channel in channels:
        raw: list[dict] = []
        cursor = ""
        while len(raw) < limit:
            tool_input = {"channel": channel, "limit": min(200, limit - len(raw))}
            if cursor:
                tool_input["cursor"] = cursor
            result = actions.execute_tool(
                tool_name=SLACK_HISTORY_TOOL, tool_input=tool_input, connection_name=connection, identifier=user
            )
            raw += _items(result.data, "messages")
            cursor = _next_cursor(result.data)
            if not cursor:
                break
        if threads:
            for root in [m for m in raw if _has_replies(m)]:
                result = actions.execute_tool(
                    tool_name=SLACK_REPLIES_TOOL,
                    tool_input={"channel": channel, "ts": root["ts"], "limit": 200},
                    connection_name=connection,
                    identifier=user,
                )
                raw += _items(result.data, "messages")
        msgs = normalize_slack(raw, channel)
        resolve_slack_names(actions, connection, user, msgs, names)
        print(f"slack {channel}: {len(msgs)} messages")
        out += msgs
    return out


# --- GitHub ----------------------------------------------------------------


def normalize_github_item(raw: dict, repo: str, kind: str) -> dict:
    user = raw.get("user") or {}
    author = user.get("login") if isinstance(user, dict) else user
    number = raw.get("number")
    return {
        "id": f"{repo}#{number}",
        "number": number,
        "kind": kind,
        "title": str(raw.get("title") or "").strip(),
        "body": str(raw.get("body") or "").strip(),
        "author": str(author or raw.get("author") or "unknown"),
        "url": str(raw.get("html_url") or raw.get("url") or ""),
        "created_at": str(raw.get("created_at") or ""),
        "repo": repo,
    }


def normalize_github(raw_issues: list[dict], raw_pulls: list[dict], repo: str) -> list[dict]:
    """GitHub's issues list also returns PRs (they carry a ``pull_request`` key);
    those are skipped there and taken from the PR list. Sorted by number."""
    items = {}
    for raw in raw_pulls:
        item = normalize_github_item(raw, repo, "pull_request")
        items[item["number"]] = item
    for raw in raw_issues:
        if raw.get("pull_request"):
            continue
        item = normalize_github_item(raw, repo, "issue")
        items.setdefault(item["number"], item)
    return sorted(items.values(), key=lambda i: i["number"] or 0)


def _github_list(actions, tool: str, connection: str, user: str, owner: str, name: str, limit: int, key: str):
    out: list[dict] = []
    page = 1
    while len(out) < limit:
        result = actions.execute_tool(
            tool_name=tool,
            tool_input={"owner": owner, "repo": name, "state": "all", "per_page": 100, "page": page},
            connection_name=connection,
            identifier=user,
        )
        batch = _items(result.data, key)
        out += batch
        if len(batch) < 100:
            break
        page += 1
    return out[:limit]


def pull_github(actions, connection: str, user: str, repo: str, limit: int = 200) -> list[dict]:
    owner, name = repo.split("/", 1)
    issues = _github_list(actions, GITHUB_ISSUES_TOOL, connection, user, owner, name, limit, "issues")
    pulls = _github_list(actions, GITHUB_PULLS_TOOL, connection, user, owner, name, limit, "pull_requests")
    items = normalize_github(issues, pulls, repo)
    print(f"github {repo}: {len(items)} issues and PRs")
    return items


# --- Entry point -------------------------------------------------------------


def save(items: list[dict], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2) + "\n")
    print(f"saved {len(items)} to {path}")
    return path


def pull(
    user: str,
    slack_channels: list[str] | None = None,
    github_repo: str | None = None,
    slack_connection: str = "slack",
    github_connection: str = "github",
    limit: int = 200,
    save_dir: str | None = None,
) -> dict:
    """Pull as ``user``; returns {"slack": [...], "github": [...]}, saving
    ``<save_dir>/<user>-<source>.json`` when ``save_dir`` is given."""
    actions = scalekit_actions()
    result: dict[str, list] = {}
    if slack_channels:
        ensure_authorized(actions, slack_connection, user)
        result["slack"] = pull_slack(actions, slack_connection, user, slack_channels, limit)
    if github_repo:
        ensure_authorized(actions, github_connection, user)
        result["github"] = pull_github(actions, github_connection, user, github_repo, limit)
    if save_dir:
        for source, items in result.items():
            save(items, Path(save_dir) / f"{user}-{source}.json")
    return result
