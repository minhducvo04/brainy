import base64

import pytest
from types import SimpleNamespace

from brain import pull
from brain.cli import build_parser
from brain.records import build_records, tags_in_text


class Actions:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def execute_tool(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(data=self.responses.pop(0))


def test_gmail_fetch_detail_pagination_and_records():
    encoded = base64.urlsafe_b64encode(b'Use Postgres for transactions.').decode().rstrip('=')
    actions = Actions([
        {'messages': [{'id': 'm1'}], 'nextPageToken': 'next'},
        {'id': 'm1', 'payload': {'headers': [
            {'name': 'Subject', 'value': 'Database decision'},
            {'name': 'From', 'value': 'Dev <dev@example.test>'}],
            'mimeType': 'multipart/alternative', 'parts': [
                {'mimeType': 'text/plain', 'body': {'data': encoded}}]}},
        {'messages': []},
    ])
    emails = pull.pull_gmail(actions, 'gmail', 'alice', 'subject:Database', 5)
    records = build_records([], [], 'alice', gmail_items=emails)
    assert len(records) == 1
    assert records[0]['node_set'] == ['source:gmail', 'owner:alice']
    assert '[gmail | Database decision | Dev <dev@example.test>]' in records[0]['text']
    assert 'Use Postgres for transactions.' in records[0]['text']
    assert actions.calls[0]['tool_input']['query'] == 'subject:Database'
    assert actions.calls[1]['tool_input'] == {'message_id': 'm1', 'format': 'full'}
    assert actions.calls[2]['tool_input']['page_token'] == 'next'
    assert all(c['identifier'] == 'alice' and c['connection_name'] == 'gmail' for c in actions.calls)


def test_notion_page_nested_content_and_records():
    actions = Actions([
        {'results': [{'id': 'p1', 'object': 'page', 'url': 'https://notion.so/p1',
                      'properties': {'Name': {'type': 'title', 'title': [{'plain_text': 'Database plan'}]}}}]},
        {'results': [{'id': 'b1', 'type': 'toggle', 'has_children': True,
                      'toggle': {'rich_text': [{'text': {'content': 'Decision'}}]}}]},
        {'results': [{'id': 'b2', 'type': 'paragraph',
                      'paragraph': {'rich_text': [{'plain_text': 'Use Postgres.'}]}}],
         'has_more': True, 'next_cursor': 'c1'},
        {'results': [{'id': 'b3', 'type': 'paragraph',
                      'paragraph': {'rich_text': [{'plain_text': 'Approved.'}]}}]},
    ])
    pages = pull.pull_notion(actions, 'notion', 'bob', 'Database', 1)
    records = build_records([], [], 'bob', notion_items=pages)
    assert len(records) == 1
    assert records[0]['node_set'] == ['source:notion', 'owner:bob']
    assert '[notion | Database plan]' in records[0]['text']
    assert 'Decision\nUse Postgres.\nApproved.' in records[0]['text']
    assert actions.calls[-1]['tool_input']['start_cursor'] == 'c1'
    assert all(c['identifier'] == 'bob' and c['connection_name'] == 'notion' for c in actions.calls)


def test_cli_options_and_citation_tags():
    args = build_parser().parse_args(['pull', '--user', 'alice', '--gmail-query', 'subject:Demo', '--notion-query', 'Demo'])
    assert args.gmail_query == 'subject:Demo'
    assert args.notion_query == 'Demo'
    assert (args.gmail_connection, args.notion_connection) == ('gmail', 'notion')
    args = build_parser().parse_args(['ingest', '--user', 'alice', '--gmail', 'email.json', '--notion', 'page.json'])
    assert (args.gmail, args.notion) == ('email.json', 'page.json')
    assert tags_in_text('[gmail | Demo | Dev] body') == ['source:gmail']
    assert tags_in_text('[notion | Demo] body') == ['source:notion']


def test_pull_save_and_ingest_wiring(tmp_path, monkeypatch):
    import asyncio
    import sys
    from brain.cli import cmd_ingest, cmd_pull

    actions = Actions([
        {'messages': [{'id': 'm1', 'subject': 'Demo', 'from': 'Dev', 'body': 'Approved.'}]},
        {'results': [{'id': 'p1', 'title': 'Demo'}]},
        {'results': [{'type': 'paragraph', 'paragraph': {'rich_text': [{'plain_text': 'Ready.'}]}}]},
    ])
    authorized = []
    monkeypatch.setattr(pull, 'scalekit_actions', lambda: actions)
    monkeypatch.setattr(pull, 'ensure_authorized', lambda a, c, u: authorized.append((c, u)))
    parser = build_parser()
    args = parser.parse_args(['pull', '--user', 'alice', '--gmail-query', 'subject:Demo',
                              '--notion-query', 'Demo', '--save', str(tmp_path),
                              '--gmail-connection', 'work-mail', '--notion-connection', 'work-pages'])
    asyncio.run(cmd_pull(args))
    assert authorized == [('work-mail', 'alice'), ('work-pages', 'alice')]
    assert [c['connection_name'] for c in actions.calls] == ['work-mail', 'work-pages', 'work-pages']
    captured = []

    async def remember(records, user):
        captured.extend(records)
        assert user == 'alice'
        return {'count': len(records)}

    # No cognee import or credential loading in this CLI contract check.
    memory = SimpleNamespace(email_for=lambda u: u + '@example.test', remember=remember)
    monkeypatch.setitem(sys.modules, 'brain.memory', memory)
    import brain
    monkeypatch.setattr(brain, 'memory', memory, raising=False)
    args = parser.parse_args(['ingest', '--user', 'alice', '--gmail', str(tmp_path / 'alice-gmail.json'),
                              '--notion', str(tmp_path / 'alice-notion.json')])
    asyncio.run(cmd_ingest(args))
    assert len(captured) == 2
    assert all('owner:alice@example.test' in r['node_set'] for r in captured)
    assert {r['ref'] for r in captured} == {'gmail:m1', 'notion:p1'}


def test_limits_deduplication_and_repeated_cursor():
    actions = Actions([
        {'messages': [{'id': 'm1', 'body': 'One'}, {'id': 'm1', 'body': 'One'}], 'nextPageToken': 'same'},
        {'messages': [{'id': 'm1', 'body': 'One'}], 'nextPageToken': 'same'},
    ])
    assert len(pull.pull_gmail(actions, 'gmail', 'alice', '', 2)) == 1
    assert len(actions.calls) == 2
    assert pull.pull_gmail(Actions([]), 'gmail', 'alice', '', 0) == []
    actions = Actions([
        {'results': [{'id': 'db', 'object': 'database'}, {'id': 'p1', 'title': 'One'},
                     {'id': 'p2', 'title': 'Two'}]},
        {'results': []},
    ])
    assert len(pull.pull_notion(actions, 'notion', 'alice', '', 1)) == 1
    assert len(actions.calls) == 2


@pytest.mark.parametrize("failed_source", ["slack", "github", "gmail", "notion"])
@pytest.mark.parametrize("failure_stage", ["authorize", "pull"])
def test_source_failure_preserves_other_saved_results(tmp_path, monkeypatch, capsys,
                                                       failed_source, failure_stage):
    import json

    sources = ["slack", "github", "gmail", "notion"]
    actions = object()
    monkeypatch.setattr(pull, "scalekit_actions", lambda: actions)

    def authorize(a, connection, user):
        assert a is actions and user == "alice"
        if connection == failed_source and failure_stage == "authorize":
            raise RuntimeError("private error details")

    def fetch(a, connection, user, query, limit):
        assert a is actions and user == "alice"
        if connection == failed_source and failure_stage == "pull":
            raise RuntimeError("private error details")
        return [{"id": connection + "-1"}]

    monkeypatch.setattr(pull, "ensure_authorized", authorize)
    for source in sources:
        monkeypatch.setattr(pull, "pull_" + source, fetch)
    result = pull.pull("alice", slack_channels=["eng"], github_repo="demo/repo",
                       gmail_query="subject:Demo", notion_query="Demo", save_dir=str(tmp_path))
    assert set(result) == set(sources) - {failed_source}
    for source in sources:
        path = tmp_path / f"alice-{source}.json"
        assert path.exists() == (source != failed_source)
        if path.exists():
            assert json.loads(path.read_text()) == [{"id": source + "-1"}]
    output = capsys.readouterr().out
    assert f"{failed_source}: failed (RuntimeError)" in output
    assert "private error details" not in output
