"""Synthetic datasets in the real folder layouts, for testing the pipeline without any patient data.

The images are drawn shapes, not retinas. Anything computed from them is meaningless clinically;
they exist to prove that every stage runs and that the numbers are computed correctly."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter

P_GRADE = [0.60, 0.10, 0.18, 0.06, 0.06]


def fake_fundus(rng, grade, gradable=True, mac=False) -> Image.Image:
    w, h = int(rng.integers(300, 420)), int(rng.integers(220, 300))
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(min(w, h) * 0.46)
    cx, cy = w // 2, h // 2
    base = (int(rng.integers(150, 200)), int(rng.integers(60, 100)), int(rng.integers(20, 50)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=base)
    dx, dy = cx + r // 2 + int(rng.integers(-8, 9)), cy + int(rng.integers(-10, 11))
    for _ in range(14):                                                                       # "vessels": make every image distinct
        x, y, pts = float(dx), float(dy), []
        a = rng.uniform(0, 2 * np.pi)
        for _ in range(int(rng.integers(6, 14))):
            pts.append((x, y))
            a += rng.normal(0, 0.45)
            x, y = x + 14 * np.cos(a), y + 14 * np.sin(a)
        d.line(pts, fill=(int(base[0] * 0.6), int(base[1] * 0.45), base[2] // 2), width=int(rng.integers(1, 4)))
    d.ellipse([dx - 12, dy - 12, dx + 12, dy + 12], fill=(240, 220, 150))                     # "disc"
    for _ in range(int(grade or 0) * 14):                                                      # "lesions"
        a, rr = rng.uniform(0, 2 * np.pi), rng.uniform(0, r * 0.85)
        x, y = cx + rr * np.cos(a), cy + rr * np.sin(a)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(90, 10, 10))
    if mac:
        for _ in range(10):
            x, y = cx - r // 3 + rng.normal(0, 6), cy + rng.normal(0, 6)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(250, 240, 120))
    if not gradable:
        im = im.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.35))
    return im


def _grades(rng, n):
    return rng.choice(5, size=n, p=P_GRADE)


def make(root: Path, scale: int = 1, seed: int = 0) -> Path:
    """Write small synthetic copies of every dataset under root. scale=1 gives about 3,000 images."""
    rng = np.random.default_rng(seed)
    root = Path(root)

    def save(folder: Path, name: str, grade, gradable=True, mac=False):
        folder.mkdir(parents=True, exist_ok=True)
        fake_fundus(rng, grade, gradable, mac).save(folder / name, quality=90)

    # ---- EyePACS: two eyes per patient, grades correlated within a patient ----
    ep = root / "eyepacs"
    for part, csv, n_pat in (("train", "trainLabels.csv", 350 * scale), ("test", "retinopathy_solution.csv", 600 * scale)):
        rows, eyeq = [], []
        for pid in range(n_pat):
            g0 = int(_grades(rng, 1)[0])
            for eye in ("left", "right"):
                g = int(np.clip(g0 + rng.choice([-1, 0, 0, 0, 1]), 0, 4))
                name = f"{pid + (0 if part == 'train' else 100000)}_{eye}"
                bad = rng.random() < 0.06
                save(ep / part, name + ".jpeg", g, gradable=not bad)
                rows.append({"image": name, "level": g, **({"Usage": "Private"} if part == "test" else {})})
                if rng.random() < 0.8:
                    eyeq.append({"image": name + ".jpeg", "quality": 2 if bad else int(rng.integers(0, 2)), "DR_grade": g})
        pd.DataFrame(rows).to_csv(ep / csv, index=False)
        pd.DataFrame(eyeq).to_csv(ep / f"Label_EyeQ_{part}.csv", index=False)

    # ---- Messidor-2 ----
    ms = root / "messidor2"
    rows = []
    for i, g in enumerate(_grades(rng, 220 * scale)):
        ok = rng.random() > 0.02
        mac = bool(ok and rng.random() < 0.05 + 0.12 * g)
        name = f"IM{i:06d}.JPG" if i % 2 else f"2005_{i:05d}_0100_PP.png"
        save(ms / "IMAGES", name, g, ok, mac)
        rows.append({"image_id": name, "adjudicated_dr_grade": g if ok else "", "adjudicated_dme": int(mac) if ok else "", "adjudicated_gradable": int(ok)})
    pd.DataFrame(rows).to_csv(ms / "messidor_data.csv", index=False)

    # ---- DDR: txt label files, class 5 = ungradeable ----
    dd = root / "ddr" / "DR_grading"
    for part, n in (("train", 120 * scale), ("valid", 60 * scale), ("test", 400 * scale)):
        lines = []
        for i, g in enumerate(_grades(rng, n)):
            bad = rng.random() < 0.08
            name = f"007-{part}-{i:04d}-000.jpg"
            save(dd / part, name, g, gradable=not bad)
            lines.append(f"{name} {5 if bad else g}")
        (dd / f"{part}.txt").write_text("\n".join(lines) + "\n")

    # ---- APTOS ----
    ap = root / "aptos2019"
    rows = []
    for i, g in enumerate(_grades(rng, 300 * scale)):
        name = f"{rng.integers(16 ** 11, 16 ** 12):012x}"
        save(ap / "train_images", name + ".png", g)
        rows.append({"id_code": name, "diagnosis": g})
    pd.DataFrame(rows).to_csv(ap / "train.csv", index=False)

    # ---- IDRiD: long folder names, a column name with a trailing space ----
    idr = root / "idrid" / "B. Disease Grading"
    (idr / "2. Groundtruths").mkdir(parents=True, exist_ok=True)
    k = 0
    for sub, csv, n in (("a. Training Set", "a. IDRiD_Disease Grading_Training Labels.csv", 80 * scale),
                        ("b. Testing Set", "b. IDRiD_Disease Grading_Testing Labels.csv", 40 * scale)):
        rows = []
        for g in rng.choice(5, size=n, p=[0.33, 0.05, 0.32, 0.18, 0.12]):
            k += 1
            mac = int(rng.choice([0, 1, 2], p=[0.5, 0.15, 0.35])) if g else 0
            save(idr / "1. Original Images" / sub, f"IDRiD_{k:03d}.jpg", g, mac=mac > 0)
            rows.append({"Image name": f"IDRiD_{k:03d}", "Retinopathy grade": g, "Risk of macular edema ": mac})
        pd.DataFrame(rows).to_csv(idr / "2. Groundtruths" / csv, index=False)

    # ---- mBRSET and BRSET: patient column, yes/no maculopathy, some missing grades ----
    for name, n_pat, folder, cols in (("mbrset", 90 * scale, "images", ("file", "patient", "final_icdr", "final_edema")),
                                      ("brset", 150 * scale, "fundus_photos", ("image_id", "patient_id", "DR_ICDR", "macular_edema"))):
        rows = []
        for pid in range(n_pat):
            g0 = int(_grades(rng, 1)[0])
            for j in range(4 if name == "mbrset" else 2):
                g = int(np.clip(g0 + rng.choice([-1, 0, 0, 1]), 0, 4))
                missing = name == "mbrset" and rng.random() < 0.05
                mac = bool(rng.random() < 0.04 + 0.1 * g) and not missing
                fn = f"{pid}.{j}.jpg" if name == "mbrset" else f"img{pid:05d}{j}"
                save(root / name / folder, fn if name == "mbrset" else fn + ".jpg", g, gradable=not missing, mac=mac)
                rows.append(dict(zip(cols, (fn, pid, "" if missing else g, ("yes" if mac else "no") if name == "mbrset" else int(mac)))))
        pd.DataFrame(rows).to_csv(root / name / "labels.csv", index=False)

    # ---- deliberate problems the pipeline must catch ----
    src = sorted((ep / "train").glob("*.jpeg"))[:3]
    for i, p in enumerate(src):                         # the same photographs also sit in APTOS (cross-dataset duplicates)
        (ap / "train_images" / f"dupdupdup{i:03d}.png").write_bytes(b"")  # placeholder, replaced below
        Image.open(p).save(ap / "train_images" / f"dupdupdup{i:03d}.png")
    a = pd.read_csv(ap / "train.csv")
    a = pd.concat([a, pd.DataFrame({"id_code": [f"dupdupdup{i:03d}" for i in range(3)], "diagnosis": [0, 0, 0]})])
    a.to_csv(ap / "train.csv", index=False)
    (ap / "train_images" / "corrupt000000.png").write_bytes(b"not an image")   # an unreadable file
    pd.concat([a, pd.DataFrame({"id_code": ["corrupt000000", "missing000000"], "diagnosis": [1, 2]})]).to_csv(ap / "train.csv", index=False)
    return root
