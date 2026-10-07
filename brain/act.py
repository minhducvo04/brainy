"""Post a brief to Slack as the acting user, through Scalekit (never a bot token).

The message goes out with ``identifier=<user>``, so Slack shows it from that
user's own authorized account. A human confirms before anything is sent unless
``yes=True``; ``dry_run=True`` only prints what would be sent.
"""

from __future__ import annotations

from brain.pull import ensure_authorized, scalekit_actions

SLACK_SEND_TOOL = "slack_send_message"  # inputs: channel, text (required); thread_ts optional


def post_brief(
    user: str,
    channel: str,
    text: str,
    connection: str = "slack",
    yes: bool = False,
    dry_run: bool = False,
    ask=input,
) -> dict:
    """``channel`` is a channel (#name or id) or a user id for a DM."""
    preview = f"as {user} via Scalekit {connection} -> {channel}:\n{text}"
    if dry_run:
        print(f"[dry run] would send {preview}")
        return {"sent": False, "dry_run": True}
    if not yes and ask(f"Send {preview}\nType yes to send: ").strip().lower() != "yes":
        print("cancelled")
        return {"sent": False, "cancelled": True}
    actions = scalekit_actions()
    ensure_authorized(actions, connection, user)
    result = actions.execute_tool(
        tool_name=SLACK_SEND_TOOL,
        tool_input={"channel": channel, "text": text},
        connection_name=connection,
        identifier=user,
    )
    data = result.data or {}
    # Count it as sent only when Slack says so (ok=true or a message ts); the raw
    # output shape was not seen live, so anything else is reported, not assumed.
    ok = isinstance(data, dict) and (data.get("ok") is True or bool(data.get("ts")))
    print(f"sent={ok} execution_id={result.execution_id} keys={sorted(data) if isinstance(data, dict) else type(data)}")
    return {"sent": ok, "execution_id": result.execution_id, "data": data}
