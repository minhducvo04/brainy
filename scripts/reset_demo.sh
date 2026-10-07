#!/usr/bin/env bash
# Run from the repository root. Preserve old cognee state before re-ingesting.
set -euo pipefail

if [[ ! -x .venv/bin/python || ! -f brain/cli.py ]]; then
    printf 'Run this script from the repo root with .venv installed.\n' >&2
    exit 1
fi

# Check CLI compatibility before moving any live state. Keep tool output private.
if ! ingest_help="$(.venv/bin/python -m brain.cli ingest --help 2>/dev/null)"; then
    printf 'Cannot read ingest help; demo state was not moved.\n' >&2
    exit 1
fi
alice_sources=(--github sample_data/github.json --slack sample_data/slack.json --channels eng,general)
if [[ -f sample_data/gmail.json && -f sample_data/notion.json && "$ingest_help" == *--gmail* ]]; then
    alice_sources+=(--gmail sample_data/gmail.json --notion sample_data/notion.json)
fi

if [[ -e .cognee_system || -L .cognee_system || -e .cognee_data || -L .cognee_data ]]; then
    mkdir -p runs
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

# Do not echo ingestion output: dependency logs may contain credentials.
if .venv/bin/python -m brain.cli ingest --user alice "${alice_sources[@]}" >/dev/null 2>&1; then
    printf 'alice: demo samples re-ingested.\n'
else
    printf 'alice: ingest failed; any previous state remains in the backup.\n' >&2
    exit 1
fi
if .venv/bin/python -m brain.cli ingest --user bob --slack sample_data/slack.json --channels general >/dev/null 2>&1; then
    printf 'bob: general Slack samples re-ingested.\n'
else
    printf 'bob: ingest failed; any previous state remains in the backup.\n' >&2
    exit 1
fi
