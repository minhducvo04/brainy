#!/usr/bin/env bash
# Run from the repository root. Reset the demo brains: alice answers, bob is refused, no shares.
#   bash scripts/reset_demo.sh            fast: copy the verified golden brains back (seconds)
#   bash scripts/reset_demo.sh --rebuild  slow: re-ingest the samples (several minutes), verify, save a new golden
# Shares cannot be revoked in cognee, so reset before every run of the demo.
# Old state is always moved to runs/, never deleted. A failed reset puts the old state back.
set -euo pipefail

if [[ ! -x .venv/bin/python || ! -f brain/cli.py ]]; then
    printf 'Run this script from the repo root with .venv installed.\n' >&2
    exit 1
fi

golden="runs/demo-golden"
mode="fast"
if [[ "${1:-}" == "--rebuild" || ! -d "$golden/.cognee_system" ]]; then
    mode="rebuild"
fi

# Tool output goes to a local log under runs/ (gitignored), never the terminal:
# dependency logs may contain credentials. Each step has a time limit.
mkdir -p runs
log="runs/reset-$(date +%H%M%S).log"
limited() {
    local seconds="$1"
    shift
    perl -e 'alarm shift; exec @ARGV' "$seconds" "$@"
}

# Check CLI compatibility before moving any live state.
if ! ingest_help="$(.venv/bin/python -m brain.cli ingest --help 2>/dev/null)"; then
    printf 'Cannot read ingest help; demo state was not moved.\n' >&2
    exit 1
fi
alice_sources=(--github sample_data/github.json --slack sample_data/slack.json --channels eng,general)
if [[ -f sample_data/gmail.json && -f sample_data/notion.json && "$ingest_help" == *--gmail* ]]; then
    alice_sources+=(--gmail sample_data/gmail.json --notion sample_data/notion.json)
fi

backup=""
if [[ -e .cognee_system || -L .cognee_system || -e .cognee_data || -L .cognee_data ]]; then
    backup_base="runs/cognee-backup-$(date +%H%M%S)"
    backup="$backup_base"
    suffix=0
    while [[ -e "$backup" || -L "$backup" ]]; do
        suffix=$((suffix + 1))
        backup="${backup_base}-${suffix}"
    done
    mkdir "$backup"
    for state in .cognee_system .cognee_data; do
        if [[ -e "$state" || -L "$state" ]]; then
            mv -- "$state" "$backup/"
        fi
    done
fi

# On any failure put the previous brains back, so a failed reset never leaves the demo empty.
fail() {
    trap - INT TERM
    printf '%s\n' "$1" >&2
    if [[ -n "$backup" ]]; then
        mkdir -p "$backup/failed"
        for state in .cognee_system .cognee_data; do
            if [[ -e "$state" || -L "$state" ]]; then
                mv -- "$state" "$backup/failed/"
            fi
            if [[ -e "$backup/$state" || -L "$backup/$state" ]]; then
                mv -- "$backup/$state" .
            fi
        done
        printf 'Restored the previous brains from %s.\n' "$backup" >&2
    fi
    printf 'Details: %s\n' "$log" >&2
    exit 1
}
trap 'fail "interrupted."' INT TERM

if [[ "$mode" == "fast" ]]; then
    printf 'Copying the verified golden brains from %s...\n' "$golden"
    cp -R "$golden/.cognee_system" "$golden/.cognee_data" . || fail 'copy from golden failed.'
else
    printf 'Rebuilding: alice ingest (up to 15 min while the gateway is slow)...\n'
    limited 900 .venv/bin/python -m brain.cli ingest --user alice "${alice_sources[@]}" >>"$log" 2>&1 \
        || fail 'alice: ingest failed or timed out.'
    printf 'Rebuilding: bob ingest...\n'
    limited 600 .venv/bin/python -m brain.cli ingest --user bob --slack sample_data/slack.json --channels general >>"$log" 2>&1 \
        || fail 'bob: ingest failed or timed out.'
fi

# The ingest command reports counts even when cognee stored nothing, so prove it
# with real asks: alice must answer from her brain, bob must be refused from his own.
question="Why did we switch to Postgres and who owns the migration?"
printf 'Checking: alice answers, bob is refused (about 30 s)...\n'
alice_out="$(limited 180 .venv/bin/python -m brain.cli ask --user alice "$question" 2>>"$log")" \
    || fail 'check: alice ask failed or timed out.'
bob_out="$(limited 180 .venv/bin/python -m brain.cli ask --user bob "$question" 2>>"$log")" \
    || fail 'check: bob ask failed or timed out.'
printf '%s\n' "$alice_out" | .venv/bin/python -c '
import json, sys
d = json.load(sys.stdin)
sys.exit(0 if d["sources"] and not d["answer"].startswith("I can'"'"'t see that") and "alice-brain" in d["datasets"] else 1)
' 2>/dev/null || fail 'check: alice got no answer from alice-brain (the brain is empty).'
printf '%s\n' "$bob_out" | .venv/bin/python -c '
import json, sys
d = json.load(sys.stdin)
sys.exit(0 if d["answer"].startswith("I can'"'"'t see that") and d["datasets"] == ["bob-brain"] else 1)
' 2>/dev/null || fail 'check: bob is not refused, or bob-brain is missing.'

if [[ "$mode" == "rebuild" ]]; then
    old_golden=""
    if [[ -d "$golden" ]]; then
        old_golden="runs/demo-golden-old-$(date +%H%M%S)"
        mv -- "$golden" "$old_golden"
    fi
    mkdir -p "$golden"
    cp -R .cognee_system .cognee_data "$golden/" \
        || { printf 'Reset OK, but saving the golden copy failed; run --rebuild before the next fast reset.\n' >&2; exit 1; }
    printf 'Saved a new golden copy in %s%s.\n' "$golden" "${old_golden:+ (previous one moved to $old_golden)}"
fi

printf 'Reset OK (%s): alice answers, bob is refused, no shares. Log: %s\n' "$mode" "$log"
