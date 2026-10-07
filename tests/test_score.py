import json
from eval.score import score_answer, score_run, mean, main

SC = {"must_mention": ["Carol", "October 14"], "expected_sources": ["source:github", "source:slack"],
      "must_not_mention": ["secret"]}
REF = {"must_mention": [], "must_not_mention": ["Carol"], "expect_refusal": True}


def test_full_hit():
    r = score_answer(SC, "carol owns it, cutover october 14", ["source:github", "source:slack"])
    assert r["score"] == 1.0 and not r["leaked"]


def test_miss_partial():
    r = score_answer(SC, "Carol owns it", ["source:slack"])
    assert r["mention_hits"] == ["Carol"] and r["source_hits"] == ["source:slack"]
    assert abs(r["score"] - (0.7 * 0.5 + 0.3 * 0.5)) < 1e-9


def test_leak_is_zero():
    r = score_answer(SC, "Carol, October 14, the secret", ["source:github", "source:slack"])
    assert r["score"] == 0.0 and r["leaked"] == ["secret"]


def test_refusal():
    assert score_answer(REF, "I can't see that channel.", [])["score"] == 1.0
    assert score_answer(REF, "No idea.", [])["score"] == 0.0
    assert score_answer(REF, "I can't see it but Carol knows", [])["score"] == 0.0


def test_mean_and_cli(tmp_path, capsys):
    sc = [{"id": "a", **SC}, {"id": "b", **REF}]
    sp = tmp_path / "sc.json"; sp.write_text(json.dumps(sc))
    good = [{"id": "a", "answer": "Carol October 14", "sources": ["source:github", "source:slack"]},
            {"id": "b", "answer": "no access", "sources": []}]
    bad = [{"id": "a", "answer": "Carol", "sources": []}, {"id": "b", "answer": "Carol", "sources": []}]
    assert mean(score_run(good, sc)) == 1.0
    g, b = tmp_path / "g.json", tmp_path / "b.json"
    g.write_text(json.dumps(good)); b.write_text(json.dumps(bad))
    main(["--answers", str(g), "--scenarios", str(sp)])
    assert "mean 1.000" in capsys.readouterr().out
    main(["--compare", str(b), str(g), "--scenarios", str(sp)])
    assert "after 1.000" in capsys.readouterr().out
