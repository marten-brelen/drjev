"""The synthetic demo must give the same numbers wherever it is run.

Found on 8 Oct 2026: the mock models keyed their noise to each image's absolute file path, so the same
demo run in two folders (a laptop and the sandbox) gave different results. The data stages were already
identical; only the mock answers moved."""
from drjev import adapters, questions, splits


def _answers(ws, monkeypatch, prefix=None):
    m = splits.load_manifest(ws)
    if prefix:                                    # the same workspace, as if it lived in another folder
        moved = m.assign(path=prefix + m["path"])
        monkeypatch.setattr(splits, "load_manifest", lambda cfg, include_excluded=False: moved)
        m = moved
    run = dict(ws.run("mock_jev_zs"))
    a = adapters.make(run, ws, in_process=True)
    a.load()
    qs = questions.load(ws.questions_file, 0)
    out = {}
    for r in m.head(40).itertuples():
        out[r.image_id] = [ans.p for ans in a.answer(r.path, qs)]
    monkeypatch.undo()
    return out


def test_mock_answers_do_not_depend_on_the_folder(ws, monkeypatch):
    here = _answers(ws, monkeypatch)
    elsewhere = _answers(ws, monkeypatch, prefix="/some/other/folder")
    assert here.keys() == elsewhere.keys()
    for k in here:
        assert here[k] == elsewhere[k], k
