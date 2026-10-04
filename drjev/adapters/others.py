"""Adapters for the other Jev-style models.

UNTESTED: each was written from the model's published documentation (model card and repository,
read on 3 Oct 2026) and has not been run on a GPU. Run `drjev check-model <run>` on two images
before trusting any of them, and expect to adjust small details.

None of these models has its own "unknown" output, so questions that allow abstention reach them
as a single choice with an explicit "unknown" option (handled in base.Adapter)."""
from __future__ import annotations

import base64
import io
import sys

from ..questions import Question
from .base import Adapter
from .proc import ServerMixin


def _line(k: str, d: str) -> str:
    return f"{k}: {d}".replace("\n", " ") if d else k


class NeoHorse(Adapter):
    """TokenRhythm/NeoHorse-Jev-4B. Needs the wheel shipped in the model repo:
    pip install --no-deps <model_dir>/dist/neohorse_decision-1.0.0-py3-none-any.whl
    One image and one question per request."""

    def load(self):
        from neohorse_decision.vision import VisionDecisionEngine
        self.engine = VisionDecisionEngine(self.run["model_dir"])

    def _score(self, image_path, q: Question):
        from PIL import Image
        if q.kind == "noul":
            spec = {"type": "noul", "instructions": q.instruction}
        elif q.kind == "score":
            spec = {"type": "score", "instructions": q.instruction, "criteria": [d for _, d in q.options]}
        else:
            spec = {"type": "choice", "instructions": q.instruction, "criteria": {k: d for k, d in q.options}}
        with Image.open(image_path) as im:
            res = self.engine.predict({"model": "NeoHorse-Jev-4B", "state": "", "questions": {q.id: spec}}, im.convert("RGB"))
        probs = res["answers"][q.id]["probabilities"]
        if q.kind == "noul":
            return [float(probs["false"]), float(probs["true"])], None
        if q.kind == "score":
            return [float(probs[str(i)]) for i in range(len(q.options))], None
        return [float(probs[k]) for k in q.keys], None


class JevOmni(Adapter):
    """akhilaaa3/Jev-Omni (Gemma 4 12B). Options are plain strings; there is no question type."""

    def load(self):
        from huggingface_hub import snapshot_download
        path = snapshot_download(self.run["hf_repo"], revision=self.run.get("revision"))
        sys.path.insert(0, path)
        from jev_omni import load_jev_omni
        self.clf = load_jev_omni()

    def _score(self, image_path, q: Question):
        options = [_line(k, d) for k, d in q.options]
        res = self.clf.predict(state="", question=q.instruction, options=options, media=image_path, modality="image")
        return [float(res["probabilities"][o]) for o in options], None


class Jev27bHTTP(ServerMixin, Adapter):
    """autotrust/JEV-27B-VL behind its vLLM server (bash serve.sh; POST /v1/decide).
    Its decision head was trained on text; image decisions are zero-shot. Needs an 80 GB GPU."""

    def load(self):
        import requests
        self.session = requests.Session()
        self.url = self.run["url"]
        self.max_side = int(self.run.get("max_side", 448))   # the model card suggests 448 px or less
        self.start_server()

    def close(self):
        self.stop_server()

    def _image(self, path):
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((self.max_side, self.max_side))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=95)
        return {"image": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}

    def _score(self, image_path, q: Question):
        options = [_line(k, d) for k, d in q.options]
        body = {"kind": "choice", "state": ["Fundus photograph: ", self._image(image_path)],
                "question": q.instruction, "options": options}
        r = self.session.post(self.url, json=body, timeout=300)
        r.raise_for_status()
        j = r.json()
        got = dict(zip(j["options"], j["probabilities"]))
        return [float(got[o]) for o in options], None


class VisualJev(Adapter):
    """guanxuyu/visual-jev-4b-answer-sft: a LoRA on Qwen3-VL-4B, scored with the VDM class from
    github.com/guanxuyu-sv/Visual-Jev (clone it and set repo_dir). Choice questions only."""

    def load(self):
        import torch
        from peft import PeftModel
        sys.path.insert(0, str(self.cfg.base / self.run["repo_dir"] / "code") if self.cfg is not None else self.run["repo_dir"] + "/code")
        from vdm.models.vdm_model import VDM
        self.torch = torch
        self.model = VDM(self.run["base_model"], device="cuda", dtype=torch.bfloat16, with_heads=False)
        self.model.processor.image_processor.max_pixels = int(self.run.get("max_pixels", 200704))
        self.model.backbone = PeftModel.from_pretrained(self.model.backbone, self.run["hf_repo"],
                                                        revision=self.run.get("revision")).eval()

    def _score_many(self, image_path, qs):
        from PIL import Image
        questions = [{"qtype": "choice", "instruction": q.instruction, "candidates": [_line(k, d) for k, d in q.options]} for q in qs]
        with Image.open(image_path) as im:
            group = self.model.prepare_group(im.convert("RGB"), questions, shared_context="")
        run = self.model.run_independent if len(questions) == 1 else self.model.run_prefix_share_batch
        with self.torch.no_grad():
            out = run(group)
        res = []
        for i in range(len(qs)):
            logits = out["lm_option_logits"][i, : group.n_options[i]]
            res.append((self.torch.softmax(logits.float(), dim=-1).cpu().tolist(), None))
        return res


class GlanceAdapter(Adapter):
    """Glance: a frozen Qwen3-VL-4B read through the glance-vlm library (pip install glance-vlm).
    Nothing is trained, so this is the control for what Visual-Jev's adapter adds."""

    def load(self):
        from glance import Glance
        self.g = Glance()

    def _score(self, image_path, q: Question):
        question = q.instruction + " The photograph is `img0`."
        if q.kind == "noul":
            res = self.g.noul(image_path, question)
            y = float(res["noul"])
            return [1 - y, y], None
        options = [_line(k, d) for k, d in q.options]
        res = self.g.choice(image_path, question, options)
        return [float(res["probabilities"][o]) for o in options], None
