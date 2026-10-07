# Hackathon: instructions for every agent

One rulebook for Claude Code (through `CLAUDE.md`), Codex, Cursor and any other agent in this folder.
Owner: Duc (Minh Duc Vo). Event: Build a Company Brain (cognee + Scalekit + Respan), 2026-10-07, deadline 6:00 PM PT; see `docs/event.md` and `docs/plans/2026-10-07-company-brain.md`.
Goal: a working, demoable project by the deadline. Speed matters, but a demo that breaks is worse than a smaller one that works.

## 1. Hard rules
1. **Never print secrets.** No `cat`, `grep` or `echo` of `.env` or a key; check length or prefix only. `.env` is gitignored.
2. **Nothing goes public without Duc's yes**: no push to a public repo, no submission, no post, no message, no deploy to a public URL.
3. **No personal data from Kyra.** Do not copy anything from `~/Projects/kyra/data/` or Kyra's `.env` into this folder.
4. **Git safety.** Never force push, rewrite pushed history, `git add -A` or `git add -f`. Add explicit paths.
5. **Hackathon rules win.** If the event bans prebuilt code, a tool or a model, follow the event rules; record them in `docs/event.md`.
6. **Honest status.** Say first what is not verified. Use built, verified, merged, deployed exactly.

## 2. The flow (hackathon speed)
1. **Duc gives the idea.** The planner (Claude home chat) asks at most 3 questions, each with a guess attached: who it is for, what the demo shows, what the judging criteria are. Everything else is defaulted and written as assumptions.
2. **Plan in 10 minutes.** `docs/plans/<date>-<topic>.md`: the demo script first, then packages written `[step] -> verify: [check]`. Each package names its files; no two open packages share a file.
3. **Build in parallel.** One package per lane, each in its own worktree under `.worktrees/<lane>-<topic>` (see section 3).
4. **Review fast.** A non-author checks each package against its verify line and runs it once for real. Fix-first findings go back to the author.
5. **Merge to `main`** only after the package's check and one real run pass. Keep `main` demoable at all times.
6. **Demo check every merge.** Run the demo script end to end. If it breaks, fix that before anything new.
7. **Final hour:** freeze features, polish the demo path, write the README and submission text (humanized, no em dashes).

## 3. Lanes
| Lane | Who | Use for |
|---|---|---|
| Planner | Claude home chat | Plan, split, review, merge, demo checks |
| Builders | Codex lanes (Sol), Claude subagents | UI and backend packages |
| Mentor | Codex Astra lane | Reviews, hard bugs, teaching notes |
| Workers | Cursor (`cursor-agent -p` in a trusted folder) | Tests, docs, small scoped code |
| Local | Qwen on the Mac | Cheap evals and log reading only |

- Read `~/Projects/kyra/.claude/skills/lane-routing/SKILL.md` before dispatching. Sent is not started: confirm each worker began within 5 minutes.
- Briefs name: goal, files allowed, verify line, what not to touch, where to write the result.

## 4. Tests
Per package: its verify line, and one real run (browser, API call, or device) with the proof named in the commit. Unit tests only where a bug would kill the demo. Before each merge, run the project's test command once.

## 5. Where things are
| Path | Holds |
|---|---|
| `docs/event.md` | Event name, rules, deadline, judging criteria, submission link |
| `docs/plans/` | Plans and the demo script |
| `docs/log/` | One dated line per decision or merge |
| `.worktrees/` | One worktree per open package (gitignored) |

## 6. Working basics
Simplicity first, surgical changes, match the existing style. Commit messages say what was verified.
End every substantive reply with `Finished: <part>. Next: <part>. Suggested: <model> / <effort>.`
