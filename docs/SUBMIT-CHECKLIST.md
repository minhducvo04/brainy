# Submission handoff

Official sources checked on 2026-10-07:
- https://github.com/topoteretes/cognee-hackathons/blob/main/cognee-companybrain-scalekit-respan-hackathon-2026-10-07/templates/SUBMISSION.md
- https://github.com/topoteretes/cognee-hackathons/tree/main/cognee-companybrain-scalekit-respan-hackathon-2026-10-07#submission

## Before sending

- Confirm the human participants in SUBMISSION.md. Do not assume that someone who helped with workspace access is a team participant.
- Add a judge-accessible Respan trace/eval link. Open it as a judge would and verify access. Keep credential-bearing URLs and private source content out of the public submission.
- Ask the planner for the saved before/after evaluation artifacts and the worst-case example. Attach reviewed evidence or leave the explicit evidence gap; do not fabricate it or rerun a held-out evaluation casually.
- Review the local `codex/judge-demo-guide` branch. It includes the UI, screenshots, README, and submission docs. It has not been merged or pushed by this agent.
- Publish the reviewed files to your project repository before sending its link. Confirm GitHub renders README images and includes `brain/demo_ui.py` and `SUBMISSION.md`.
- A local URL is not reachable by remote judges. Use the written run instructions or record a three-minute walkthrough and add its link. The template accepts local instructions; a video is useful but no video URL was found to be mandatory.
- Review private `cognee-feedback.md` and hand it to the organizers using their announced channel. Never add it to Git.

## Submit by either route

**Fast route:** hand the public project link and SUBMISSION.md link to an organizer, with the three-minute demo ready.

**PR route:** fork `topoteretes/cognee-hackathons`, create a branch, and add your filled submission at:

```text
cognee-companybrain-scalekit-respan-hackathon-2026-10-07/submissions/brainy/SUBMISSION.md
```

Use the filled project SUBMISSION.md, with absolute links to project screenshots/docs if adding any more links. Open a PR back to `topoteretes/cognee-hackathons` and send the PR URL to the organizer. Do not put the application code or secrets into the event repo.

The published deadline is October 7, 2026 at 6:00 PM Pacific. If it has passed, contact an organizer immediately about accepting the link; do not imply an extension exists.

## Honest demo scope

The implementation has per-user datasets and explicit sharing, not company hierarchy. Live two-app/two-user connector evidence is incomplete. The harder evaluation regressed, so the change was reverted. Show what works and keep those limitations visible.
