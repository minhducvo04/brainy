"""Pull from Slack + Google Drive through Scalekit and remember it in Cognee.

Steps 1-2 of the hackathon loop, for one user:

    authorize (once)  ->  execute_tool (Scalekit)  ->  cognee.remember(node_set=[...])
                                                   ->  cognee.recall(cross-source question)

Usage:
    python scalekit_to_cognee.py --user alice@acme.com --channel "#general" --file-id <doc_id>

Requires SCALEKIT_ENVIRONMENT_URL / SCALEKIT_CLIENT_ID / SCALEKIT_CLIENT_SECRET and
LLM_API_KEY in the environment or a .env next to this file. Connections named
``slack`` and ``googledrive`` must exist under AgentKit -> Connections (override the
names with --slack-connection / --drive-connection).
"""

from __future__ import annotations

import argparse
import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

# Per-user datasets, isolated graph + vector stores. Must be set before cognee is imported.
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "true")

import cognee  # noqa: E402
from scalekit import ScalekitClient  # noqa: E402


def scalekit_actions():
    client = ScalekitClient(
        env_url=os.environ["SCALEKIT_ENVIRONMENT_URL"],
        client_id=os.environ["SCALEKIT_CLIENT_ID"],
        client_secret=os.environ["SCALEKIT_CLIENT_SECRET"],
    )
    return client.actions


def ensure_authorized(actions, connection_name: str, identifier: str) -> None:
    """Open the consent flow once per user per connection; no-op when already ACTIVE."""
    account = actions.get_or_create_connected_account(
        connection_name=connection_name, identifier=identifier
    )
    if account.connected_account.status == "ACTIVE":
        return
    link = actions.get_authorization_link(connection_name=connection_name, identifier=identifier)
    print(f"Authorize {connection_name} for {identifier}: {link.link}")
    input("Press Enter after authorizing...")


def pull_slack_channel(actions, connection_name: str, identifier: str, channel: str, limit: int):
    """Yield one transcript line per message, newest first as Slack returns them."""
    result = actions.execute_tool(
        tool_name="slack_fetch_conversation_history",
        tool_input={"channel": channel, "limit": limit},
        connection_name=connection_name,
        identifier=identifier,
    )
    for message in result.data.get("messages", []):
        text = message.get("text", "").strip()
        if text:
            yield f"[slack {channel} · {message.get('user', '?')} · {message.get('ts', '')}] {text}"


def pull_drive_doc(actions, connection_name: str, identifier: str, file_id: str) -> str:
    """Export a Google Doc as plain text. Inspect ``result.data`` once: the exported body
    may come back as a string or wrapped in a small JSON object depending on the file."""
    result = actions.execute_tool(
        tool_name="googledrive_export_file",
        tool_input={"file_id": file_id, "mime_type": "text/plain"},
        connection_name=connection_name,
        identifier=identifier,
    )
    data = result.data
    if isinstance(data, dict):
        data = data.get("content") or data.get("data") or data
    return str(data)


async def get_or_create_user(email: str):
    from cognee.modules.users.methods import create_user, get_user_by_email

    return await get_user_by_email(email) or await create_user(email, "hackathon-pw")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--user", required=True, help="stable user id; doubles as the cognee user email")
    parser.add_argument("--channel", default="#general", help="Slack channel id or #name")
    parser.add_argument("--file-id", help="Google Doc file id to export (optional)")
    parser.add_argument("--limit", type=int, default=200, help="max Slack messages to pull")
    parser.add_argument("--slack-connection", default="slack")
    parser.add_argument("--drive-connection", default="googledrive")
    parser.add_argument("--dataset", default=None, help="cognee dataset (default: <user>-brain)")
    parser.add_argument(
        "--question",
        default="What was decided most recently, and who owns the follow-up?",
        help="cross-source question to recall at the end",
    )
    args = parser.parse_args()

    dataset = args.dataset or f"{args.user.split('@')[0]}-brain"
    actions = scalekit_actions()
    user = await get_or_create_user(args.user)

    # --- Slack ---------------------------------------------------------------
    ensure_authorized(actions, args.slack_connection, args.user)
    lines = list(pull_slack_channel(actions, args.slack_connection, args.user, args.channel, args.limit))
    print(f"pulled {len(lines)} Slack messages from {args.channel}")
    if lines:
        # One document per channel keeps the conversation context together for extraction.
        transcript = f"# Slack {args.channel}\n" + "\n".join(reversed(lines))
        await cognee.remember(
            transcript,
            dataset_name=dataset,
            user=user,
            node_set=["source:slack", f"channel:{args.channel.lstrip('#')}", f"owner:{args.user}"],
        )

    # --- Google Drive --------------------------------------------------------
    if args.file_id:
        ensure_authorized(actions, args.drive_connection, args.user)
        doc_text = pull_drive_doc(actions, args.drive_connection, args.user, args.file_id)
        print(f"pulled {len(doc_text)} chars from Drive file {args.file_id}")
        await cognee.remember(
            doc_text,
            dataset_name=dataset,
            user=user,
            node_set=["source:googledrive", f"doc:{args.file_id}", f"owner:{args.user}"],
        )

    # --- Recall across both ----------------------------------------------------
    print(f"\nQ: {args.question}")
    for item in await cognee.recall(args.question, datasets=[dataset], user=user, top_k=5):
        text = getattr(item, "text", None)
        if text:
            print(f" -> [{item.source}] {text[:500]}")

    print(f"\nDone. Explore the graph: cognee-cli -ui  (dataset: {dataset})")


if __name__ == "__main__":
    asyncio.run(main())
