"""Specialist baseline: an ordinary image classifier trained on the same images (protocol 4.2).

One backbone, three heads: grade (5 classes), gradeable (2) and maculopathy (2). An image contributes
to a head only where it has that label. Needs torch and torchvision (pip install drjev[train])."""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import metrics as M
from .splits import load_manifest
from .targets import target

MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


def build_model(arch: str, pretrained: bool):
    import torch.nn as nn
    import torchvision.models as tvm
    weights = "DEFAULT" if pretrained else None
    if arch.startswith("convnext"):
        net = getattr(tvm, arch)(weights=weights)
        dim = net.classifier[2].in_features
        net.classifier[2] = nn.Identity()
    elif arch.startswith("resnet"):
        net = getattr(tvm, arch)(weights=weights)
        dim = net.fc.in_features
        net.fc = nn.Identity()
    else:
        raise ValueError(f"Unsupported architecture '{arch}' (use a torchvision convnext_* or resnet*)")

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.body = net
            self.grade, self.gradable, self.mac = nn.Linear(dim, 5), nn.Linear(dim, 2), nn.Linear(dim, 2)

        def forward(self, x):
            h = self.body(x)
            return self.grade(h), self.gradable(h), self.mac(h)

    return Net()


def _labels(rows):
    """Per-image targets for the three heads; -1 where the image has no label for that head.
    Images from the maculopathy-training dataset teach the maculopathy head only, exactly as in the
    decision model's training file, so that both models learn grading from the same images."""
    y = np.full((len(rows), 3), -1, dtype=np.int64)
    for i, r in enumerate(rows.itertuples()):
        for j, q in enumerate(("q2_grade", "q1_gradeable", "q3_maculopathy")):
            if str(r.split).startswith("q3_") and q != "q3_maculopathy":
                continue
            t = target(q, r.grade, r.gradable, r.maculopathy)
            if isinstance(t, (int, np.integer)):
                y[i, j] = int(t)
    return y


def _dataset(paths, labels, size, augment):
    import torch
    from PIL import Image
    from torchvision import transforms as T
    aug = [T.RandomHorizontalFlip(), T.RandomVerticalFlip(), T.RandomRotation(15), T.ColorJitter(0.15, 0.15, 0.1)] if augment else []
    tf = T.Compose([T.Resize((size, size)), *aug, T.ToTensor(), T.Normalize(MEAN, STD)])

    class DS(torch.utils.data.Dataset):
        def __len__(self):
            return len(paths)

        def __getitem__(self, i):
            with Image.open(paths[i]) as im:
                return tf(im.convert("RGB")), torch.from_numpy(labels[i])

    return DS()


def train(cfg, run_name: str, device: str | None = None, pretrained: bool = True, max_epochs: int | None = None, workers: int | None = None,
          max_steps: int | None = None) -> Path | dict:
    """Train the specialist. With max_steps it only times that many steps and returns a projection (nothing is saved)."""
    import torch
    import torch.nn.functional as F
    spec = cfg.run(run_name)
    tr = spec.get("train") or {}
    workers = cfg.machine["workers"]["dataloader"] if workers is None else workers
    seed = int(spec.get("seed", 0))
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    man = load_manifest(cfg)
    size = tr.get("train_size", "full")
    train_rows = man[man["split"] == "train"]
    if size != "full":
        train_rows = train_rows[train_rows[f"eff_{int(size)}"]]
    import pandas as pd
    train_rows = pd.concat([train_rows, man[man["split"] == "q3_train"]])       # maculopathy labels come from their own dataset
    dev_rows = pd.concat([man[man["split"] == "dev"], man[man["split"] == "q3_dev"]])
    ytr, ydv = _labels(train_rows), _labels(dev_rows)
    img = int(tr.get("image_size", 512))
    bs = int(tr.get("batch_size") or cfg.machine["training"]["specialist"]["batch_size"])
    key = np.where(ytr[:, 1] == 0, 5, np.where(ytr[:, 0] >= 0, ytr[:, 0], 6))    # grade, ungradeable, or no grade
    w = 1.0 / np.bincount(key, minlength=7)[key]
    sampler = torch.utils.data.WeightedRandomSampler(torch.as_tensor(w, dtype=torch.double), num_samples=len(w), replacement=True,
                                                     generator=torch.Generator().manual_seed(seed))
    dl = torch.utils.data.DataLoader(_dataset(train_rows["path"].tolist(), ytr, img, True), batch_size=bs, sampler=sampler, num_workers=workers, drop_last=True)
    dv = torch.utils.data.DataLoader(_dataset(dev_rows["path"].tolist(), ydv, img, False), batch_size=bs, num_workers=workers)
    model = build_model(tr.get("arch", "convnext_tiny"), pretrained).to(device)
    epochs = int(max_epochs or tr.get("epochs", 20))
    opt = torch.optim.AdamW(model.parameters(), lr=float(tr.get("lr", 1e-4)), weight_decay=0.05)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=float(tr.get("lr", 1e-4)), total_steps=max(1, epochs * len(dl)), pct_start=0.1)
    amp = device.startswith("cuda")
    scaler = torch.amp.GradScaler(enabled=amp)
    out = cfg.base / Path(spec["checkpoint"]).parent if not Path(spec["checkpoint"]).is_absolute() else Path(spec["checkpoint"]).parent
    out.mkdir(parents=True, exist_ok=True)

    def loss_fn(outs, y):
        total = 0.0
        for o, col in zip(outs, range(3)):
            m = y[:, col] >= 0
            if m.any():
                total = total + F.cross_entropy(o[m], y[m, col])
        return total

    best, log, patience = -1.0, [], 0
    if max_steps:                                            # timing probe
        model.train()
        marks = []
        for k, (x, y) in enumerate(dl):
            x, y = x.to(device), y.to(device)
            with torch.autocast(device_type="cuda" if amp else "cpu", enabled=amp):
                loss = loss_fn(model(x), y)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            marks.append(time.time())
            if k + 1 >= max_steps:
                break
        if len(marks) < 3:
            return {"run": run_name, "status": f"only {len(marks)} training steps available; too few to time"}
        per_step = (marks[-1] - marks[1]) / (len(marks) - 2)   # the first step includes start-up
        total = epochs * len(dl)
        return {"run": run_name, "status": "ok", "steps_timed": len(marks) - 2, "seconds_per_step": round(per_step, 3), "steps_total": total,
                "examples_per_second": round(bs / per_step, 1), "hours_total": round(per_step * total / 3600, 2), "device": device}
    for ep in range(epochs):
        model.train()
        t0, run_loss = time.time(), 0.0
        for x, y in dl:
            x, y = x.to(device), y.to(device)
            with torch.autocast(device_type="cuda" if amp else "cpu", enabled=amp):
                loss = loss_fn(model(x), y)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            run_loss += float(loss.detach())
        model.eval()
        pg = []
        with torch.no_grad():
            for x, _ in dv:
                pg.append(model(x.to(device))[0].argmax(1).cpu().numpy())
        pg = np.concatenate(pg)
        m = ydv[:, 0] >= 0
        k = M.qwk(ydv[m, 0], pg[m])
        log.append({"epoch": ep + 1, "train_loss": run_loss / max(1, len(dl)), "dev_qwk": k, "seconds": round(time.time() - t0, 1)})
        print(f"[{run_name}] epoch {ep + 1}/{epochs} loss {log[-1]['train_loss']:.3f} dev QWK {k:.3f}")
        if np.isnan(k) or k > best:
            best, patience = (k if not np.isnan(k) else best), 0
            torch.save({"state": model.state_dict(), "arch": tr.get("arch", "convnext_tiny"), "image_size": img, "dev_qwk": k, "epoch": ep + 1}, out / "best.pt")
        else:
            patience += 1
            if patience >= int(tr.get("patience", 5)):
                break
    (out / "train_log.json").write_text(json.dumps({"run": run_name, "train_images": len(train_rows), "log": log}, indent=2) + "\n")
    print(f"[{run_name}] best dev QWK {best:.3f} -> {out / 'best.pt'}")
    return out / "best.pt"


def probe(cfg, run_name: str, steps: int = 30, device=None, pretrained: bool = True, workers=None) -> dict:
    """Time a few training steps and project the full run (upper bound: early stopping may end it sooner)."""
    return train(cfg, run_name, device=device, pretrained=pretrained, workers=workers, max_steps=steps)
