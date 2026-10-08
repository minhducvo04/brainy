# Team Submission

Prepared October 7, 2026, from application commit `19bed11` and existing local verification records. **Not yet verified: a complete two-app, two-user live Scalekit pull, shareable Respan run links, and a successful measured improvement.** The reproducible demo uses synthetic company data.

Existing records show 19 tests passed, successful Respan chat and embedding probes, and eight passing checks in an isolated Cognee memory/access smoke test. The full demo and evaluation results below are historical team-reported results. No completed fresh evaluation export was available when this document was prepared. See the [team run log](docs/log/README.md) for the historical runs.

## Team

- Team name: **Brainy**.
- Participants: **Duc Vo and Miguel Coronel**.
- Company Brain / project name: **Brainy**.

## Company Brain Overview

Brainy helps engineering teams answer three questions: why did we choose this approach, who owns it, and what remains open? It combines decisions from GitHub and Slack in persistent Cognee memory and produces short answers with source citations. Gmail and Notion ingestion extend the workflow to email and decision documents. An engineering lead can see the full project context, while a new hire sees only their readable datasets. Sharing a dataset changes the new hire's answer without changing the question. Fictional Northwind Labs fixtures let judges reproduce the workflow with their own model credentials.

- Data sources connected through Scalekit: Slack and GitHub are the core implemented connectors; Gmail and Notion are also implemented. The reproducible demo uses synthetic fixtures. Separate workspace provisioning records describe a GitHub README read and six issue readbacks in a historical Scalekit environment. Authorization in the current team environment is pending. **A complete two-app, two-user live pull is not confirmed.**
- Primary use case / team workflow: Engineering decision lookup and onboarding. Combine a migration PR, an open rollback issue, and a Slack discussion to explain the PostgreSQL decision and its owner.
- Demo users: Alice, the engineering lead, owns GitHub, Slack `#eng`/`#general`, Gmail, and Notion records. Bob, a new hire, initially owns only Slack `#general` records.
- What makes it stand out: Cross-source explanations with citations, a before/after access grant, and evaluation that assigns zero when an answer includes a listed restricted fact.

## The Three Layers

### Pull - Scalekit

- Connections (`connection_name` to app): CLI defaults are `slack`, `github`, `gmail`, and `notion`. Workspace setup records instead name `slack`, `github-connect`, and `gmail-c2shktnB` in the configured team environment; CLI flags allow these overrides. Employee authorization is pending in those records. A live Notion connection remains unconfirmed.
- Tools called by the implementation:
  - Slack: `slack_fetch_conversation_history`, `slack_get_conversation_replies`, `slack_get_user_info`.
  - GitHub: `github_issues_list`, `github_pull_requests_list`.
  - Gmail: `gmail_fetch_mails`, `gmail_get_message_by_id`.
  - Notion: `notion_page_search`, `notion_page_content_get`.
- Live verification boundary: The separate historical provisioning check used `github_file_contents_get`. Those workspace records are not included in this repository and do not verify the application's full issue/PR pull path or the current team's authorization. Gmail, Notion, and Slack user-name lookup still need live tool verification.
- User identification: Every Scalekit call supplies the acting user's `identifier`. Cognee maps an email identifier directly to a user; demo names such as `alice` expand to `alice@acme.com`. Pull and ingest must use the same identity.
- Write-back action: `brain.cli post` can send a brief using `slack_send_message` as the acting user. It supports a dry run and requests confirmation before sending by default. The submission demonstrates a preview; a successful live Slack post is not claimed.
- Code entry points: [brain/pull.py](brain/pull.py), [brain/act.py](brain/act.py), [brain/cli.py](brain/cli.py).

### Remember - Cognee

- Permanent graph: Normalized issues/PRs, Slack messages/threads, emails, and Notion page text enter `cognee.remember(...)` with `dataset_name`, `user`, and `node_set`, without `session_id`.
- Session memory: Not used. The answer function does not store questions or generated answers as permanent company facts.
- Provenance tags: `source:github`, `source:slack`, `source:gmail`, `source:notion`, plus applicable `repo:*`, `channel:*`, `owner:*`, and `author:*` tags. Source labels also appear in stored text and answer context.
- Datasets and ownership: Alice owns `alice-brain`; Bob owns `bob-brain`. Each initially reads their own dataset. After the grant, Bob can also read `alice-brain`.
- Access control: `ENABLE_BACKEND_ACCESS_CONTROL=true`. Retrieval obtains the user's readable dataset IDs from Cognee and passes those IDs and the user into recall. Sharing checks the owner's share permission before granting Bob `read`. Dataset permissions enforce access; tags record provenance.
- Beyond defaults: Records are grouped by provenance before ingestion. Recall uses `SearchType.CHUNKS`. The answer prompt requests inline citations, limits responses to 120 words, and instructs refusal when the context lacks the answer. No custom ontology, custom graph model, or `improve()` call is used.
- Scope: This prototype trusts the CLI's selected user. Deployment needs authenticated identity binding and a share-revocation flow.
- Code entry points: [brain/records.py](brain/records.py), [brain/memory.py](brain/memory.py), [brain/agent.py](brain/agent.py).

### Act + Evaluate - Agent and Respan

- Agent task: Recall the caller's readable memory and generate a cited decision brief. A separate CLI action previews or posts the chosen brief to Slack.
- Respan gateway and models: Agent answers use the OpenAI-compatible Respan endpoint. The environment template also routes Cognee extraction and embeddings through it. Defaults are `openai/gpt-5-mini` and `openai/text-embedding-3-large` with 3,072 dimensions.
- Tracing: `respan-ai` initializes `Respan(app_name="brainy")` and wraps the answer with `workflow(name="answer")`. The prior submission records an HTTP 200 trace export and an `answer.workflow` span. **Shareable trace link: not available in the current evidence.** Tracing becomes a no-op if its key or SDK is unavailable or initialization fails.
- Testsets: [scenarios/scenarios.json](scenarios/scenarios.json) has 12 scenarios; [scenarios/scenarios_v2.json](scenarios/scenarios_v2.json) has 10 harder scenarios. These are local testsets; upload to a Respan testset is not confirmed.
- Evaluator: Independent Python checks, without an LLM judge. Normal answers score 70% for expected fact strings and 30% for expected source tags. Any listed restricted fact in the answer forces zero. Refusal scenarios check refusal wording. The source score checks returned tags, not whether each inline citation supports its sentence.
- Code entry points: [brain/agent.py](brain/agent.py), [brain/cli.py](brain/cli.py), [eval/score.py](eval/score.py).

## Evaluation Evidence

The original 12-scenario set reached a reported mean of **1.000**, so the team added a harder set. The before/after comparison below uses the same 10 harder scenarios. The [run log](docs/log/README.md) records these historical results; the historical raw answer files are absent from this checkout. These means have not been independently recalculated for this submission.

| Evidence | Available result | What it establishes |
|---|---|---|
| Application tests at `19bed11` | 19 passed, 0 failed | Recorded automated test result; not live connector validation |
| Respan gateway retry | Chat passed; embeddings passed with 3,072 dimensions | The direct model interfaces responded |
| Isolated Cognee smoke test | 8 passed, 0 failed, using one synthetic document | Remember, owner recall, reader isolation, read grant, shared recall, and removal checks |
| Original scenario set | Reported mean 1.000, 12 scenarios | Historical score on the easier set |
| Harder scenario set | Reported baseline 0.900; candidate 0.877, 10 scenarios each | Historical regression that led to a revert |

The table above summarizes existing local verification records; it is not a raw trace export. The isolated Cognee check does not establish full answer quality, cross-source retrieval, or live connector success.

### Baseline Run

- Respan trace / eval run link: **Not available.** The [historical run log](docs/log/README.md) records the mean; the baseline answer export and shareable Respan URL are still missing.
- Scenarios run: All 10 in `scenarios/scenarios_v2.json`, before sharing Alice's dataset with Bob.
- Mean score: **0.900**, reported on October 7, 2026.
- Worst scenario: `v10`, a mixed public/private question. Bob should answer the public on-call part and withhold the private API date. The prior submission records a refusal of the entire question.

```text
question: When does the weekly on-call rotation start, and on what date does the v1 API shut down?
expected: State that the weekly rotation starts November 2, cite Slack, and withhold the private API date.
got: Full refusal, according to the prior submission; exact raw response still needed.
score: 0.000 for that full-refusal behavior under the current scorer.
```

### Improved Run

This was an attempted improvement that regressed. A successful improvement is not claimed.

- Respan trace / eval run link: **Not available.** The [historical run log](docs/log/README.md) records the mean; the candidate answer export and shareable Respan URL are still missing.
- Change: Commit `7c4c746` added provenance labels to each context chunk and strengthened the citation prompt. The mixed-question failure remained, and `v05` lost an expected fact. The team reverted the change in `4f3700e`.
- Mean score: **0.877**, a reported decrease of **0.023**.

```text
Before:     mean = 0.900   (n = 10 scenarios)
Candidate:  mean = 0.877   (n = 10 scenarios)
Decision:   revert candidate; retain the baseline implementation
```

Next improvement: answer accessible parts of mixed questions and explicitly withhold inaccessible facts. This is not yet implemented or measured.

## Access Story

The [team run log](docs/log/README.md) records this demonstration with real Cognee and LLM calls over synthetic GitHub and Slack records. The outcomes below are reported from that run; a raw three-answer transcript is not available. The separate isolated smoke test also passed reader isolation and before/after grant checks, but used a different one-document fixture.

- User A: `alice` / `alice@acme.com`; reads `alice-brain`, containing GitHub and Slack `#eng`/`#general`. The reset script also loads Alice's Gmail and Notion fixtures when present.
- User B: `bob` / `bob@acme.com`; initially reads only `bob-brain`, containing Slack `#general`. These are demo identities, not evidence of OAuth completion for two live accounts.
- Question asked by both: **"Why did we switch to Postgres and who owns the migration?"**
- Result for A: A cited answer naming Carol and describing JSONB, row locks, and replication lag.
- Result for B before sharing: **"I can't see that."**
- Grant: Alice grants Bob `read` on `alice-brain` using `python -m brain.cli share --owner alice --to bob`.
- Result for B after sharing: A cited answer using the newly readable Alice dataset alongside Bob's own dataset.
- Grant scope: Alice's entire dataset becomes readable, including Gmail/Notion fixtures if loaded. The grant is not limited to one document.

## Architecture

```text
[Scalekit per-user connections]       [Synthetic Northwind fixtures]
             |                                     |
             | execute_tool(identifier=user)       |
             +----------------+--------------------+
                              v
                 [Normalize text + provenance]
                              |
                              | remember(dataset_name, user, node_set)
                              v
                  [Cognee persistent datasets]
                    alice-brain / bob-brain
                              |
                              | authorized IDs + recall(CHUNKS, user)
                              v
                   [Answer agent via Respan]
                     cited brief or refusal
                       /              \
                      v                v
          [Scalekit Slack action]  [Scenario answers + Python scorer]
          preview / confirmed post    before/after scores
```

Scalekit scopes live source access to the supplied identifier. Cognee enforces dataset permissions during retrieval. Respan traces the answer workflow; the local evaluator scores its outputs.

## Reproduction

Judges can use the committed synthetic fixtures without our SaaS accounts. They still need valid model and embedding credentials. Use Python 3.12 and `uv`:

```bash
git clone https://github.com/minhducvo04/brainy.git
cd brainy
uv venv --python 3.12
uv pip install -r requirements.txt
cp .env.example .env
# Fill in the Respan model and embedding credentials before continuing.
```

On Apple Silicon, apply the [README's Ladybug installation fix](README.md#macos-apple-silicon-ladybug-fix) before ingestion. Current application code defaults to `.cognee_system` and `.cognee_data` in the repository working directory. Use these locations with the reset script.

The existing automated-test record used `PYTHONPATH=. .venv/bin/python -m pytest -q` and reported 19 passing tests. This submission does not claim that test result verifies live integrations. Run only one reset, ingestion, or evaluation process at a time against the same local Cognee storage.

The latest reset script restores a local verified snapshot when `runs/demo-golden/.cognee_system` exists. The snapshot is not distributed in Git, so a fresh checkout rebuilds the datasets and saves one after verification. Both modes need working model credentials. Prepare this step before the timed demo: ingestion timeouts are 15 minutes for Alice and 10 minutes for Bob, followed by two answer checks of up to 3 minutes each. The reset checks source presence, readable datasets, and refusal behavior; it does not verify every fact or inline citation.

```bash
# Reset to unshared demo datasets. Use --rebuild to force fresh ingestion.
bash scripts/reset_demo.sh

# Evaluate before granting access, while Bob remains restricted.
.venv/bin/python -m brain.cli eval --scenarios scenarios/scenarios_v2.json --out runs/v2-baseline-reproduced.json
.venv/bin/python -m eval.score --answers runs/v2-baseline-reproduced.json --scenarios scenarios/scenarios_v2.json

# Demonstrate the same question before and after the grant.
.venv/bin/python -m brain.cli ask --user alice "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"
.venv/bin/python -m brain.cli share --owner alice --to bob
.venv/bin/python -m brain.cli ask --user bob "Why did we switch to Postgres and who owns the migration?"

# Preview the write-back action without sending a message.
.venv/bin/python -m brain.cli post --user alice --to "#eng" --text "Paste the cited answer here" --dry-run
```

Model outputs can vary, so a rerun may differ from historical scores. To reproduce the candidate, use a separate checkout of `7c4c746`, ingest the same fixtures with Bob's restricted access intact, and run the same scenarios with identical model settings. Once both answer files exist, compare them using the harder scenario set:

```bash
.venv/bin/python -m eval.score --compare runs/v2-before.json runs/v2-after.json --scenarios scenarios/scenarios_v2.json
```

For live data, authorize the real user in Scalekit first. Replace the identifier, channel ID, and repository below with your own. The command saves JSON; ingest the resulting files separately using the same user identifier.

```bash
.venv/bin/python -m brain.cli pull \
  --user alice@example.com \
  --slack-channels CHANNEL_ID \
  --github-repo owner/repository \
  --slack-connection slack \
  --github-connection github-connect \
  --save
```

Environment variables, documented in [.env.example](.env.example):

```text
RESPAN_API_KEY
LLM_PROVIDER=custom
LLM_ENDPOINT=https://api.respan.ai/api
LLM_API_KEY=<Respan key>
LLM_MODEL=openai/gpt-5-mini
EMBEDDING_PROVIDER=custom
EMBEDDING_ENDPOINT=https://api.respan.ai/api
EMBEDDING_API_KEY=<Respan key>
EMBEDDING_MODEL=openai/text-embedding-3-large
EMBEDDING_DIMENSIONS=3072
ENABLE_BACKEND_ACCESS_CONTROL=true

# Required for live Scalekit pulls and real write-back actions:
SCALEKIT_ENVIRONMENT_URL
SCALEKIT_CLIENT_ID
SCALEKIT_CLIENT_SECRET
```

## Demo

- Demo link or local instructions: Use the [reproduction commands above](#reproduction). No recording, hosted demo URL, or slide deck is included in the current materials.
- Three-minute pitch outline:
  1. **0:00-0:20:** Explain the problem: decisions are spread across issues, threads, and documents.
  2. **0:20-0:45:** Show GitHub and Slack fixtures and the per-user pull path. Distinguish the fixture demo from the separately verified GitHub read.
  3. **0:45-1:15:** Ask Alice the PostgreSQL question. Show the reason, owner, and citations.
  4. **1:15-1:55:** Ask Bob, show the refusal, grant access, and ask again.
  5. **1:55-2:15:** Preview the Slack brief. Show an answer trace if accessible in the team's Respan dashboard; otherwise state that the shareable trace evidence is missing.
  6. **2:15-2:45:** Show the historical ten-scenario before/after scores and identify them as reported results. Explain the regression and revert.
  7. **2:45-3:00:** Describe next steps: partial answers, live multi-app authorization, and authenticated application access.

Prepare ingestion and evaluation before the timed demo. The trace segment requires an accessible Respan link. Reset before each access demonstration because the CLI does not implement share revocation.

## Links

- Repo: [minhducvo04/brainy](https://github.com/minhducvo04/brainy).
- Respan traces / eval runs: **Not available in the current materials.** Baseline, candidate, and access-demo trace links remain to be supplied.
- Slides / writeup: This submission and the [README](README.md); no slides.
- Scenario files: [Original 12](scenarios/scenarios.json), [harder 10](scenarios/scenarios_v2.json).
- Prior verification record: [Team run log](docs/log/README.md).
- Synthetic fixture description: [Northwind Labs sample data](sample_data/README.md).

## Remaining Evidence Gaps

- Complete a live pull from two different apps for two users with different access in the current Scalekit environment.
- Supply baseline and candidate raw answer exports, plus shareable Respan trace/evaluation links. The local Python scores are not evidence of scores attached to Respan runs.
- Supply the full access-demo transcript or show it live, including the grant and the changed answer.
- Measure a successful improvement on the same scenario set. The existing experiment records a regression, followed by a revert.

The source code, fixture workflow, commands, and historical results are documented above. These outstanding items are not presented as completed work.
