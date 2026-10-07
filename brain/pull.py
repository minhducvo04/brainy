"""Per-user pulls from Slack, GitHub, Gmail and Notion through Scalekit AgentKit.

Follows examples/scalekit_to_cognee.py: authorize once per user per connection
(the link is printed when the account is not ACTIVE), then ``execute_tool`` with
``identifier=<user>`` so Scalekit adds that user's own token. No bot tokens.

Output is normalized to the recorded shapes in sample_data/:
  GitHub: {id, number, kind, title, body, author, url, created_at, repo}
  Slack:  {channel, user, ts, text, thread_ts}  (thread_ts is None for a thread root)
  Gmail:  {id, subject, from, body, date}
  Notion: {id, title, url, body}

Tool names come from the Scalekit connector docs (docs.scalekit.com/agentkit/connectors/
slack and /github). The raw output shape of each tool was not seen live, so the
normalizers accept a bare list or a dict wrapping one under a common key.
"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

SLACK_HISTORY_TOOL = "slack_fetch_conversation_history"  # inputs: channel, limit, cursor
SLACK_REPLIES_TOOL = "slack_get_conversation_replies"  # inputs: channel, ts, limit, cursor
SLACK_USER_TOOL = "slack_get_user_info"  # inputs: user (Slack users.info); name not seen live
GITHUB_ISSUES_TOOL = "github_issues_list"  # inputs: owner, repo, state, per_page, page
GITHUB_PULLS_TOOL = "github_pull_requests_list"  # inputs: owner, repo, state, per_page, page


# Names and inputs confirmed in docs; response shapes have not been seen live.
# https://docs.scalekit.com/agentkit/connectors/gmail/
GMAIL_FETCH_TOOL = "gmail_fetch_mails"  # not seen live
GMAIL_MESSAGE_TOOL = "gmail_get_message_by_id"  # not seen live
# https://docs.scalekit.com/agentkit/connectors/notion/
NOTION_SEARCH_TOOL = "notion_page_search"  # not seen live
NOTION_CONTENT_TOOL = "notion_page_content_get"  # not seen live


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


# --- Gmail / Notion ----------------------------------------------------------


def _object(data, *keys) -> dict:
    """Unwrap common object envelopes while preserving provider pagination fields."""
    while isinstance(data, dict):
        wrapped = next((data[k] for k in (*keys, "data", "result", "response")
                        if isinstance(data.get(k), dict)), None)
        if wrapped is None:
            return data
        data = wrapped
    return {}


def _gmail_body(payload: dict) -> str:
    parts = payload.get("parts") or []
    if parts:
        plain = [p for p in parts if p.get("mimeType") == "text/plain"]
        return "\n".join(filter(None, (_gmail_body(p) for p in plain or parts)))
    encoded = (payload.get("body") or {}).get("data")
    if not encoded or payload.get("mimeType", "text/plain") not in ("text/plain", "text/html"):
        return ""
    return base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("utf-8", errors="replace")


def normalize_gmail(raw: dict) -> dict:
    raw = _object(raw, "message")
    payload = raw.get("payload") or {}
    headers = {h["name"].lower(): h.get("value", "") for h in payload.get("headers", [])}
    body = raw.get("body") if isinstance(raw.get("body"), str) else ""
    return {
        "id": str(raw.get("id") or raw.get("messageId") or ""),
        "subject": str(raw.get("subject") or headers.get("subject") or "(no subject)"),
        "from": str(raw.get("from") or headers.get("from") or "unknown"),
        "body": _gmail_body(payload) or body or str(raw.get("snippet") or ""),
        "date": str(headers.get("date") or raw.get("internalDate") or ""),
    }


def pull_gmail(actions, connection: str, user: str, query: str, limit: int = 200) -> list[dict]:
    out, seen, cursors = [], set(), set()
    cursor = ""
    while len(out) < limit:
        inputs = {"query": query, "format": "full", "max_results": min(100, limit - len(out))}
        if cursor:
            inputs["page_token"] = cursor
        result = actions.execute_tool(tool_name=GMAIL_FETCH_TOOL, tool_input=inputs,
                                      connection_name=connection, identifier=user)
        data = _object(result.data) if isinstance(result.data, dict) else result.data
        for raw in _items(data, "messages", "emails"):
            mid = raw.get("id") or raw.get("messageId")
            if not mid or mid in seen:
                continue
            if not raw.get("payload") and not raw.get("body"):
                detail = actions.execute_tool(tool_name=GMAIL_MESSAGE_TOOL,
                    tool_input={"message_id": mid, "format": "full"},
                    connection_name=connection, identifier=user)
                raw = _object(detail.data, "message")
            item = normalize_gmail(raw)
            item["id"] = str(mid)
            out.append(item)
            seen.add(mid)
            if len(out) >= limit:
                break
        cursor = data.get("nextPageToken", "") if isinstance(data, dict) else ""
        if not cursor or cursor in cursors:
            break
        cursors.add(cursor)
    print(f"gmail: {len(out)} emails")
    return out


def _rich_text(parts) -> str:
    if isinstance(parts, str):
        return parts
    return "".join(p.get("plain_text") or (p.get("text") or {}).get("content", "") for p in parts or [])


def _notion_content(actions, connection: str, user: str, block_id: str, visited: set) -> str:
    if block_id in visited:
        return ""
    visited.add(block_id)
    lines, cursors = [], set()
    cursor = ""
    while True:
        inputs = {"block_id": block_id, "page_size": 100}
        if cursor:
            inputs["start_cursor"] = cursor
        result = actions.execute_tool(tool_name=NOTION_CONTENT_TOOL, tool_input=inputs,
                                      connection_name=connection, identifier=user)
        data = _object(result.data) if isinstance(result.data, dict) else result.data
        for block in _items(data, "blocks"):
            content = block.get(block.get("type"), {})
            text = _rich_text(content.get("rich_text"))
            if content.get("cells"):
                text = " | ".join(_rich_text(cell) for cell in content["cells"])
            if text:
                lines.append(text)
            if block.get("has_children") and block.get("id"):
                lines.append(_notion_content(actions, connection, user, block["id"], visited))
        cursor = data.get("next_cursor", "") if isinstance(data, dict) else ""
        if not cursor or cursor in cursors:
            break
        cursors.add(cursor)
    return "\n".join(filter(None, lines))


def pull_notion(actions, connection: str, user: str, query: str, limit: int = 200) -> list[dict]:
    out, seen, cursors = [], set(), set()
    cursor = ""
    while len(out) < limit:
        inputs = {"query": query, "page_size": min(100, limit - len(out))}
        if cursor:
            inputs["start_cursor"] = cursor
        result = actions.execute_tool(tool_name=NOTION_SEARCH_TOOL, tool_input=inputs,
                                      connection_name=connection, identifier=user)
        data = _object(result.data) if isinstance(result.data, dict) else result.data
        for page in _items(data, "pages"):
            pid = page.get("id")
            if not pid or pid in seen or page.get("object", "page") != "page":
                continue
            title = _rich_text(page.get("title"))
            for prop in (page.get("properties") or {}).values():
                if prop.get("type") == "title" or "title" in prop:
                    title = _rich_text(prop.get("title")) or title
            out.append({"id": pid, "title": title or "Untitled", "url": page.get("url", ""),
                        "body": _notion_content(actions, connection, user, pid, set())})
            seen.add(pid)
            if len(out) >= limit:
                break
        cursor = data.get("next_cursor", "") if isinstance(data, dict) else ""
        if not cursor or cursor in cursors:
            break
        cursors.add(cursor)
    print(f"notion: {len(out)} pages")
    return out


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
    gmail_query: str | None = None,
    notion_query: str | None = None,
) -> dict:
    """Pull selected sources as ``user``; returns lists keyed by source, saving
    ``<save_dir>/<user>-<source>.json`` when ``save_dir`` is given."""
    actions = scalekit_actions()
    result: dict[str, list] = {}
    if slack_channels:
        ensure_authorized(actions, slack_connection, user)
        result["slack"] = pull_slack(actions, slack_connection, user, slack_channels, limit)
    if github_repo:
        ensure_authorized(actions, github_connection, user)
        result["github"] = pull_github(actions, github_connection, user, github_repo, limit)
    if gmail_query is not None:
        ensure_authorized(actions, "gmail", user)
        result["gmail"] = pull_gmail(actions, "gmail", user, gmail_query, limit)
    if notion_query is not None:
        ensure_authorized(actions, "notion", user)
        result["notion"] = pull_notion(actions, "notion", user, notion_query, limit)
    if save_dir:
        for source, items in result.items():
            save(items, Path(save_dir) / f"{user}-{source}.json")
    return result
