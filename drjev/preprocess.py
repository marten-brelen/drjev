"""Stage 2: crop each photograph to the fundus disc, pad to a square, resize, hash."""
from __future__ import annotations

import hashlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def crop_fundus(im: Image.Image, tol: int = 12) -> Image.Image:
    """Crop to the bounding box of the non-black region, then pad to a square with black."""
    a = np.asarray(im.convert("RGB"))
    mask = a.max(axis=2) > tol
    if mask.mean() > 0.02:  # otherwise the image is almost entirely dark: leave it alone
        rows, cols = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
        a = a[rows[0]: rows[-1] + 1, cols[0]: cols[-1] + 1]
    h, w = a.shape[:2]
    s = max(h, w)
    out = np.zeros((s, s, 3), dtype=np.uint8)
    y, x = (s - h) // 2, (s - w) // 2
    out[y: y + h, x: x + w] = a
    return Image.fromarray(out)


def dhash(im: Image.Image, n: int = 16) -> str:
    """Difference hash (n*n bits) of the processed image; identical images share a hash."""
    g = np.asarray(im.convert("L").resize((n + 1, n), Image.Resampling.LANCZOS), dtype=np.int16)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return np.packbits(bits).tobytes().hex()


def thumb(im: Image.Image, n: int = 8) -> str:
    """n*n grey thumbnail as hex, used to confirm that two images with matching hashes really are the same."""
    return np.asarray(im.convert("L").resize((n, n), Image.Resampling.BOX), dtype=np.uint8).tobytes().hex()


def _one(args):
    image_id, src, dst, size, quality = args
    try:
        dst = Path(dst)
        if not dst.exists():
            with Image.open(src) as im:
                out = crop_fundus(im).resize((size, size), Image.Resampling.LANCZOS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            out.save(dst, "JPEG", quality=quality)
        with Image.open(dst) as im:
            h, t = dhash(im), thumb(im)
        return image_id, str(dst), h, t, hashlib.sha256(dst.read_bytes()).hexdigest(), ""
    except Exception as e:  # unreadable file: recorded, not fatal
        return image_id, "", "", "", "", f"{type(e).__name__}: {e}"


def run(cfg) -> pd.DataFrame:
    m = pd.read_csv(cfg.manifest_raw, dtype={"grade_raw": str})
    size, q = int(cfg.preprocess["size"]), int(cfg.preprocess["jpeg_quality"])
    out_root = cfg.work / "images"
    cache_file = cfg.work / "preprocess_cache.csv"
    cache = pd.read_csv(cache_file).set_index("image_id") if cache_file.exists() else None
    todo, done = [], {}
    for r in m.itertuples():
        dst = out_root / r.dataset / (r.image_id.split(":", 1)[1].replace("/", "_") + ".jpg")
        if cache is not None and r.image_id in cache.index and Path(str(cache.at[r.image_id, "path"])).exists():
            c = cache.loc[r.image_id]
            done[r.image_id] = (c["path"], c["dhash"], c["thumb"], c["sha256"], "")
        else:
            todo.append((r.image_id, r.raw_path, str(dst), size, q))
    workers = max(1, int(cfg.preprocess.get("workers") or cfg.machine["workers"]["preprocess"]))
    if todo:
        print(f"preprocess: {len(todo)} images to process ({len(done)} cached), {workers} workers")
        with Pool(workers) as pool:
            for k, res in enumerate(pool.imap_unordered(_one, todo, chunksize=32), 1):
                done[res[0]] = res[1:]
                if k % 5000 == 0:
                    print(f"  {k}/{len(todo)}")
    m["path"] = [done[i][0] for i in m["image_id"]]
    m["dhash"] = [done[i][1] for i in m["image_id"]]
    m["thumb"] = [done[i][2] for i in m["image_id"]]
    m["sha256"] = [done[i][3] for i in m["image_id"]]
    m["error"] = [done[i][4] for i in m["image_id"]]
    bad = m[m["error"] != ""]
    if len(bad):
        bad[["image_id", "raw_path", "error"]].to_csv(cfg.work / "preprocess_errors.csv", index=False)
        print(f"preprocess: {len(bad)} unreadable images listed in preprocess_errors.csv and dropped")
    m = m[m["error"] == ""].drop(columns=["error"])
    m[["image_id", "path", "dhash", "thumb", "sha256"]].to_csv(cache_file, index=False)
    m.to_csv(cfg.manifest_proc, index=False)
    print(f"preprocess: {len(m)} images at {size}x{size} -> {out_root}")
    return m
