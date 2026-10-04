"""The five clinical questions, in a model-neutral form."""
from __future__ import annotations

from dataclasses import dataclass, field

UNKNOWN_KEY = "unknown"


@dataclass
class Question:
    id: str
    kind: str                      # noul | score | choice
    instruction: str
    options: list[tuple[str, str]]  # (key, description), in answer order. noul: [("no", ..), ("yes", ..)]
    allow_unknown: bool = True
    variant: int = 0
    meta: dict = field(default_factory=dict)

    @property
    def keys(self) -> list[str]:
        return [k for k, _ in self.options]


def load(path, variant: int = 0) -> list[Question]:
    import yaml
    spec = yaml.safe_load(open(path))
    out = []
    for qid, q in spec["questions"].items():
        ins = q["instructions"][variant]
        if q["kind"] == "noul":
            opts = [("no", q["if_no"]), ("yes", q["if_yes"])]
        elif q["kind"] == "score":
            opts = list(zip(q["labels"], q["levels"][variant]))
        else:
            opts = [(k, v) for k, v in q["options"].items()]
        out.append(Question(qid, q["kind"], ins, opts, bool(q.get("allow_unknown", True)), variant,
                            {"unknown_option": spec.get("unknown_option", "unknown")}))
    return out


def n_variants(path) -> int:
    import yaml
    spec = yaml.safe_load(open(path))
    return min(len(q["instructions"]) for q in spec["questions"].values())
