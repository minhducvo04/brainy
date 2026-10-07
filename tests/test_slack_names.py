from types import SimpleNamespace

from brain.pull import SLACK_HISTORY_TOOL, SLACK_USER_TOOL, pull_slack, save


class FakeActions:
    def __init__(self):
        self.user_calls = []

    def execute_tool(self, tool_name, tool_input, connection_name, identifier):
        if tool_name == SLACK_HISTORY_TOOL:
            return SimpleNamespace(data={"messages": [
                {"ts": "1.0", "user": "U111AAA", "text": "hi <@U222BBB> and <@U999ZZZ>"},
                {"ts": "2.0", "user": "U222BBB", "text": "yo"},
            ]})
        assert tool_name == SLACK_USER_TOOL
        uid = tool_input["user"]
        self.user_calls.append(uid)
        if uid == "U111AAA":
            return SimpleNamespace(data={"user": {"id": uid, "name": "a", "profile": {"display_name": "alice"}}})
        if uid == "U222BBB":
            return SimpleNamespace(data={"user": {"real_name": "Bob Lee"}})
        raise RuntimeError("user_not_found")


def test_ids_become_names_and_failures_keep_id(tmp_path):
    actions = FakeActions()
    msgs = pull_slack(actions, "slack", "alice", ["general"], threads=False)
    assert [m["user"] for m in msgs] == ["alice", "Bob Lee"]
    assert msgs[0]["text"] == "hi @Bob Lee and @U999ZZZ"
    assert sorted(actions.user_calls) == ["U111AAA", "U222BBB", "U999ZZZ"]  # cached: one call each
    path = save(msgs, tmp_path / "alice-slack.json")
    assert '"user": "alice"' in path.read_text()
