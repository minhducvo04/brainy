# Company Brain Challenge

## Challenge

Build a **Company Brain**: an AI system that understands a company's
knowledge across its workplace tools, remembers context over time, and
securely helps *different people* get work done — each seeing only what they
are authorized to see.

Three layers, three partners:

- **Scalekit** is the access layer — per-user OAuth connections to the
  company's apps, and the tools your agent calls on each user's behalf. That
  includes code: the GitHub connector pulls repositories, files, issues and
  PRs into the brain and pushes branches, commits and pull requests back out.
- **Cognee** is the memory layer — one knowledge graph built from everything
  pulled, scoped per user / team, queried by the agents.
- **Respan** is the LLM gateway and evaluation layer — it provides the
  event's LLM credits on its gateway (one key, 1,000+ models), logs every
  call, traces the agents' runs, and scores them with evaluators over a
  scenario set.

## Required Loop

Every team must demonstrate this sequence end to end:

```text
1. Connect ≥ 2 sources through Scalekit (two different apps, not two channels).
2. Pull from them on behalf of ≥ 2 users with different access.
3. remember() the pulled content into Cognee, tagged by source, scoped per user.
4. Wire ≥ 1 agent task that recall()s from the brain and produces a useful
   output (an answer, a brief, a routed ticket, a posted message).
5. Trace the runs in Respan and score them against a scenario set.
6. Change something (more sources, better tagging, a share, a prompt).
7. Re-run the eval. Show before and after.
```

Steps 5–7 are what separate a Company Brain from a demo. A scenario set of
8–15 questions is plenty.

## What Counts

**A real cross-source answer** means the agent's output needs facts from at
least two connected apps to be correct — the date from the doc *and* the
owner from the thread. Single-source answers score as retrieval, not as a
brain.

**A real access story** means two users, the same question, different (and
correct) results — because their Scalekit connections differ, or because
their Cognee dataset permissions differ, or both. Then a grant, and the
difference closes. Show it live.

**A real evaluation** means:

- a scenario file checked into your repo (question, expected facts or
  expected action, optional expected sources);
- a scorer that is not the agent itself (keyword/fact match, an LLM judge
  with a pinned model, or a human rating entered into the run);
- traced runs you can open in Respan and inspect step by step;
- a before score and an after score, and one sentence on what changed.

**Taking action** (posting the brief to Slack, drafting the email, opening the
issue, pushing a commit and opening a PR) is encouraged and scored under brain
quality — but every write must go through Scalekit with the acting user's
identifier, never with a shared bot token. A PR the agent pushes lands under
the authorizing user's GitHub account, which is the point.

## Scenario Format

Keep scenarios machine-readable so your eval can loop over them and Respan
can take them as a testset. A shape that works:

```json
{
  "question": "When is the launch and who owns the announcement?",
  "must_mention": ["October 21", "Priya"],
  "expected_sources": ["source:googledrive", "source:slack"],
  "as_user": "alice@acme.com"
}
```

- `must_mention` — facts a correct answer has to contain (case-insensitive).
- `expected_sources` — Cognee `node_set` tags the supporting context should
  carry; use them to score *cross-source* grounding, not just correctness.
- `as_user` — which user asks; lets one scenario file cover the access story
  (the same question with a different `as_user` and a different expectation).

Add fields freely — `expected_action`, `must_not_mention`, `max_latency_s`.
The scorer is yours.

## Scoring Rubric

Total: 100 points.

```text
30 - Company Brain quality
20 - Secure access story
20 - Evaluation
15 - Memory design
10 - Reproducibility
 5 - Demo
```

### Company Brain quality (30)

- answers stitch facts from ≥ 2 sources, with provenance
- solves a workflow a real team has (brief, triage, expert finder, decision
  archaeology, onboarding)
- takes a useful action through Scalekit, or clearly hands one off
- multiple users, not one

### Secure access story (20)

- per-user Scalekit connections; no shared tokens in code or `.env`
- Cognee datasets / permissions scoped to users, with
  `ENABLE_BACKEND_ACCESS_CONTROL=true` (or an equivalent, explained)
- demonstrates isolation, then a grant, then the changed result
- shows how access shaped the agent's behaviour (what it could not see, and
  what it did about it)

### Evaluation (20)

- scenario set checked in
- scorer independent of the agent (Respan evaluator: LLM judge, Python
  check, or human review)
- agent runs traced in Respan, scores attached to the runs
- before/after scores with the change named
- bonus: the evaluator also runs on live traffic during the demo

### Memory design (15)

- deliberate choice of what goes into the permanent graph vs session memory
- `node_set` tagging that keeps source / channel / owner provenance
- use of `improve()`, a custom graph model, an ontology, or feedback
- the graph explorer (`cognee-cli -ui`) shows a connected graph, not islands

### Reproducibility (10)

- a `README` that gets a judge from clone to eval score with their own keys
- `.env.example` lists every variable
- no hidden local state; sample data or a recorded pull for judges without
  the same SaaS accounts

### Demo (5)

- 3 minutes, live, all three layers shown
- the access story is visible on screen

## Safety

- never print or commit tokens; Scalekit holds them — keep it that way
- read-only scopes unless the agent genuinely needs to write
- no destructive actions (delete, archive, force-push, send to external
  addresses) without a human confirmation step in the agent; code changes go
  to a branch + PR, never straight to `main`
- route LLM calls through the Respan gateway so spend is visible per team;
  don't paste provider keys into the repo
- a `forget()` path for a user's data is a plus

## Suggested Team Split

Three people, three layers, meet in the middle at `cognee.remember`:

```text
Access    -> Scalekit connections, per-user pulls, the write-back action
Memory    -> ingestion + tagging, datasets per user, sharing, graph quality
Agents    -> the task agent, Respan tracing, scenario set, evaluator
```

Agree on the text format you `remember()` first (one line per Slack message
with channel/user/timestamp, one document per Drive file, one issue per
GitHub issue) — everything else can be built in parallel.

## Final Word

The best projects will make a judge say *"I'd use this on Monday."* Build for
the team you are on, with the tools you actually use, and let the eval prove
it works.
