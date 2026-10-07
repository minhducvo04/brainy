# Team Submission

## Team

- Team name:
- Participants:
- Company Brain / project name:

## Company Brain Overview

One-paragraph description of what your Company Brain does, which team
workflow it solves, and who the users are.

- Data sources connected through Scalekit (≥ 2 apps):
- Primary use case / team workflow:
- Users in the demo and how their access differs:
- What makes it stand out:

## The Three Layers

### Pull — Scalekit

- Connections created (`connection_name` → app):
- Tools called (`gmail_fetch_mails`, `slack_fetch_conversation_history`,
  `googledrive_export_file`, `github_file_contents_get`, ...):
- How users are identified (`identifier` ↔ Cognee user):
- Any write-back actions the agent takes (post, draft, open issue, push
  branch/commit, open PR):
- Code entry point:

### Remember — Cognee

- What goes into the permanent graph (`cognee.remember(...)` without
  `session_id`):
- What stays in session memory (`session_id=...`), if anything:
- `node_set` tags used for provenance (`source:*`, `channel:*`, `owner:*`):
- Datasets and who owns / can read each:
- Access control (`ENABLE_BACKEND_ACCESS_CONTROL`, shares granted):
- Anything beyond defaults (custom graph model, ontology, `improve()`,
  custom prompt, `query_type` choice):
- Code entry point:

### Act + Evaluate — your agent(s) + Respan

- Agent(s) and the task each performs:
- LLM calls routed through the Respan gateway? (models used):
- How the runs are traced (Respan SDK decorator / instrumentor):
- Scenario file / Respan testset (path, number of scenarios):
- Evaluator (LLM judge + model, Python check, human review):
- Code entry point:

## Evaluation Evidence

Show that the brain does the job — and that it got better. Concrete numbers
beat prose.

### Baseline Run

- Respan trace / eval run link:
- Scenarios run:
- Mean score:
- Worst scenario and why it failed:

```text
question:
expected:
got:
score:
```

### Improved Run

- Respan trace / eval run link:
- What changed in the brain or agent between runs (one or two sentences):
- Mean score:

```text
Before:  mean = ___   (n = ___ scenarios)
After:   mean = ___   (n = ___ scenarios)
```

## Access Story

Two users, the same question, different results — then a grant.

- User A (identifier, connections, datasets readable):
- User B (identifier, connections, datasets readable):
- Question asked by both:
- Result for A:
- Result for B before the share:
- The grant (who shared what with whom, which permission):
- Result for B after the share:

## Architecture

Short diagram or bullet list. The hackathon's core pattern is
**Pull → Remember → Act → Evaluate** across the three layers; show how yours
maps onto it and where user access is enforced.

```text
[ Scalekit connections, per user ]
        |
        | execute_tool(identifier=...)  -> documents / threads / issues
        v
[ Cognee — remember(node_set=[...], dataset_name=..., user=...) ]
        |
        | recall(question, user=...)   -> grounded context
        v
[ your agent — traced by Respan ]    -> answer / brief / action (via Scalekit)
        |
        v
[ Respan evaluator over testset ]    -> scenarios -> scores -> before/after
```

## Reproduction

Commands to reproduce your demo and your eval:

```bash
# paste commands here
```

Environment variables required:

```text
RESPAN_API_KEY                # Respan gateway credits, provided at kickoff
LLM_PROVIDER / LLM_ENDPOINT / LLM_API_KEY / LLM_MODEL      # cognee -> Respan gateway
EMBEDDING_PROVIDER / EMBEDDING_ENDPOINT / EMBEDDING_API_KEY / EMBEDDING_MODEL / EMBEDDING_DIMENSIONS
SCALEKIT_ENVIRONMENT_URL
SCALEKIT_CLIENT_ID
SCALEKIT_CLIENT_SECRET
# add anything else your brain needs
```

Judges without your SaaS accounts: how do they run it? (sample data folder,
recorded pull, seeded dataset, ...)

## Demo

- Live demo link (Loom, YouTube, etc.) or local instructions:
- 3-minute pitch outline:

```text
1. Problem / team workflow
2. Pull demo (Scalekit, two sources, as user A)
3. Brain demo (Cognee graph + a cross-source answer)
4. Access demo (user B asks, gets less; grant; asks again)
5. Agent task demo (traced run, action taken)
6. Eval demo (before/after scores in Respan)
7. What is next
```

## Links

- Repo:
- Respan traces / eval runs:
- Slides / writeup:
- Anything else:
