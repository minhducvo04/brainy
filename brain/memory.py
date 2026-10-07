"""Per-user cognee memory: remember with node_set provenance, recall, share, forget.

Follows docs/event/README.md sections 4 and 5. Access control is switched on and
cognee state is kept in ./.cognee_system and ./.cognee_data, both set before
cognee is imported.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "true"
os.environ.setdefault("SYSTEM_ROOT_DIRECTORY", str(Path(".cognee_system").resolve()))
os.environ.setdefault("DATA_ROOT_DIRECTORY", str(Path(".cognee_data").resolve()))

import cognee  # noqa: E402
from cognee import SearchType  # noqa: E402
from cognee.modules.data.methods import get_authorized_existing_datasets  # noqa: E402
from cognee.modules.engine.operations.setup import setup  # noqa: E402
from cognee.modules.users.methods import create_user, get_user_by_email  # noqa: E402
from cognee.modules.users.permissions.methods import (  # noqa: E402
    authorized_give_permission_on_datasets,
)

from brain.records import tags_in_text  # noqa: E402

DEMO_DOMAIN = "acme.com"
DEMO_PASSWORD = "hackathon-pw"  # local demo users only, as in the event README


def email_for(user: str) -> str:
    """The Scalekit identifier doubles as the cognee user email."""
    return user if "@" in user else f"{user}@{DEMO_DOMAIN}"


def dataset_for(user: str) -> str:
    return f"{email_for(user).split('@')[0]}-brain"


_ready = False


async def _ensure_setup() -> None:
    """Create cognee's relational tables once per process; a fresh store has none."""
    global _ready
    if not _ready:
        await setup()
        _ready = True


async def get_or_create_user(user: str):
    await _ensure_setup()
    email = email_for(user)
    return await get_user_by_email(email) or await create_user(email, DEMO_PASSWORD)


async def readable_datasets(user: str) -> list:
    """Datasets the user owns or was granted read on. Empty when there are none."""
    u = await get_or_create_user(user)
    try:
        return await get_authorized_existing_datasets(None, "read", u)
    except Exception as exc:  # cognee raises when a user has no datasets at all
        if "NotFound" in type(exc).__name__:
            return []
        raise


async def remember(records: list[dict], user: str) -> dict:
    """Remember records in the user's own dataset. Records sharing a node_set go in
    one call so cognify runs once per tag group, not once per item."""
    u = await get_or_create_user(user)
    dataset = dataset_for(user)
    groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for rec in records:
        groups[tuple(rec["node_set"])].append(rec["text"])
    for node_set, texts in groups.items():
        await cognee.remember(texts, dataset_name=dataset, user=u, node_set=list(node_set))
    return {"dataset": dataset, "documents": len(records), "calls": len(groups)}


async def recall(question: str, user: str, top_k: int = 8) -> dict:
    """Return {context: [{text, dataset, tags}], sources: [tag...], datasets: [name...]}.

    Uses SearchType.CHUNKS (raw passages, no LLM) so each hit is our own text and
    its provenance tags can be read back from it. Only datasets the user may read
    are searched; a user with none gets an empty context."""
    u = await get_or_create_user(user)
    readable = await readable_datasets(user)
    if not readable:
        return {"context": [], "sources": [], "datasets": []}
    results = await cognee.recall(
        question,
        query_type=SearchType.CHUNKS,
        dataset_ids=[d.id for d in readable],
        user=u,
        top_k=top_k,
    )
    context, sources = [], set()
    for item in results:
        text = getattr(item, "text", None)
        if not text:
            continue
        tags = tags_in_text(text)
        sources.update(tags)
        context.append({"text": text, "dataset": getattr(item, "dataset_name", None), "tags": tags})
    return {"context": context, "sources": sorted(sources), "datasets": [d.name for d in readable]}


async def share(owner: str, grantee: str, permission: str = "read") -> dict:
    """Owner grants ``permission`` on their brain dataset to grantee (README section 5)."""
    o = await get_or_create_user(owner)
    g = await get_or_create_user(grantee)
    (ds,) = await get_authorized_existing_datasets([dataset_for(owner)], "share", o)
    await authorized_give_permission_on_datasets(g.id, [ds.id], permission, o.id)
    return {"dataset": ds.name, "grantee": email_for(grantee), "permission": permission}


async def forget(user: str) -> dict:
    """Remove the user's own brain dataset."""
    u = await get_or_create_user(user)
    return await cognee.forget(dataset=dataset_for(user), user=u)
