"""The specialist classifier behind the common question interface.

It has no question-answering ability: referral and sight-threatening answers are read off its grade
probabilities, and it cannot abstain (its gradeability head answers Q1)."""
from __future__ import annotations

from pathlib import Path

from ..questions import Question
from .base import Adapter


class SpecialistAdapter(Adapter):
    explicit_unknown = False
    tested = True

    def load(self):
        import torch
        from torchvision import transforms as T

        from ..specialist import MEAN, STD, build_model
        ck = Path(self.run["checkpoint"])
        if not ck.is_absolute() and self.cfg is not None:
            ck = self.cfg.base / ck
        state = torch.load(ck, map_location="cpu")
        self.torch = torch
        self.device = self.run.get("device") or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = build_model(state["arch"], pretrained=False)
        self.model.load_state_dict(state["state"])
        self.model.to(self.device).eval()
        self.tf = T.Compose([T.Resize((state["image_size"],) * 2), T.ToTensor(), T.Normalize(MEAN, STD)])

    def _score_many(self, image_path, qs: list[Question]):
        from PIL import Image
        with Image.open(image_path) as im:
            x = self.tf(im.convert("RGB")).unsqueeze(0).to(self.device)
        with self.torch.no_grad():
            g, q, m = (o.softmax(1)[0].cpu().tolist() for o in self.model(x))
        out = []
        for qu in qs:
            if qu.id == "q1_gradeable":
                out.append((q, None))
            elif qu.id == "q2_grade":
                out.append((g, None))
            elif qu.id == "q3_maculopathy":
                out.append((m, None))
            else:
                p = sum(g[2:]) if qu.id == "q4_refer" else sum(g[3:])
                out.append(([1 - p, p], None))
        return out
