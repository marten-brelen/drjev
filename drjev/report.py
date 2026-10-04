"""Stage 7: tables, figures and a results summary, written from the analysis outputs.

Everything in results/ is regenerated on each run. Tables come as .csv (numbers) and .md (formatted)."""
from __future__ import annotations

import datetime
import json
import platform
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import __version__, frames
from . import metrics as M
from .splits import load_manifest

# Categorical colours in a fixed order (colour-blind-checked set); a model keeps its colour in every figure.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dc"
STAMP = "SYNTHETIC DEMO DATA: mock models on drawn images. Not study results."
ARM_NAMES = {"Z": "zero-shot", "A": "language LoRA", "B": "language + vision LoRA", "C": "base + LoRA", "G": "generative", "S": "specialist"}


def _fmt(v, lo=None, hi=None, d=3) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    s = f"{v:.{d}f}"
    if lo is not None and not np.isnan(lo):
        s += f" ({lo:.{d}f} to {hi:.{d}f})"
    return s


def _md(df: pd.DataFrame, title: str, note: str = "", stamp: bool = False) -> str:
    lines = [f"### {title}", ""]
    if stamp:
        lines += [f"**{STAMP}**", ""]
    lines += ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join("–" if (isinstance(x, float) and np.isnan(x)) else str(x) for x in row) + " |" for row in df.itertuples(index=False)]
    if note:
        lines += ["", note]
    return "\n".join(lines) + "\n"


class Reporter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.res = cfg.results
        self.tab = self.res / "tables"
        self.fig = self.res / "figures"
        for d in (self.tab, self.fig):
            d.mkdir(parents=True, exist_ok=True)
        m = pd.read_csv(self.res / "metrics_long.csv")
        self.raw = m[~m["calibrated"]]
        self.m = m[m["calibrated"]]
        self.units = list(dict.fromkeys(self.m["unit"]))
        order = [u for u in cfg.units() if u in self.units]            # colour follows the model, in registry order
        self.color = {u: PALETTE[i % len(PALETTE)] for i, u in enumerate(order)}
        self.marker = {u: MARKERS[i % len(MARKERS)] for i, u in enumerate(order)}
        self.arm = dict(zip(self.m["unit"], self.m["arm"]))
        self.synthetic = bool(self.m["synthetic"].any())
        self.datasets = [d for d in dict.fromkeys(self.m.sort_values("split")["dataset"]) if d != "pooled_external"]
        self.man = load_manifest(cfg)
        self.md_parts: list[str] = []

    # ---- helpers ----
    def cell(self, unit, dataset, metric, ci=True, d=3) -> str:
        r = self.m[(self.m["unit"] == unit) & (self.m["dataset"] == dataset) & (self.m["metric"] == metric)]
        if r.empty:
            return "–"
        r = r.iloc[0]
        return _fmt(r["value"], r["ci_low"] if ci else None, r["ci_high"], d)

    def val(self, unit, dataset, metric) -> float:
        r = self.m[(self.m["unit"] == unit) & (self.m["dataset"] == dataset) & (self.m["metric"] == metric)]
        return float(r["value"].iloc[0]) if len(r) else float("nan")

    def n(self, unit, dataset, metric="n") -> str:
        v = self.val(unit, dataset, metric)
        return "–" if np.isnan(v) else str(int(round(v)))

    def write(self, name: str, df: pd.DataFrame, title: str, note: str = ""):
        df.to_csv(self.tab / f"{name}.csv", index=False)
        md = _md(df, title, note, self.synthetic)
        (self.tab / f"{name}.md").write_text(md)
        self.md_parts.append(md)

    def label(self, u) -> str:
        return f"{u} ({ARM_NAMES.get(self.arm.get(u, ''), self.arm.get(u, ''))})"

    def by_arm(self, arms) -> list[str]:
        return [u for u in self.units if self.arm.get(u) in arms]

    # ---- tables ----
    def table0(self):
        t = pd.read_csv(self.cfg.work / "split_summary.csv")
        self.write("table0_datasets", t, "Table 0. Images by dataset, split and label after exclusions",
                   "Duplicates across datasets are listed in work/duplicates.csv; unreadable files in work/preprocess_errors.csv.")

    def table1(self):
        rows = []
        for u in self.by_arm(["Z"]):
            for ds in self.datasets:
                if np.isnan(self.val(u, ds, "qwk")):
                    continue
                rows.append({"Model": u, "Dataset": ds, "Gradeable images": self.n(u, ds, "n_gradable"), "QWK (95% CI)": self.cell(u, ds, "qwk"),
                             "Referable AUROC (95% CI)": self.cell(u, ds, "ref_auroc"), "Grade ECE": self.cell(u, ds, "ece_grade", ci=False),
                             "Abstained on gradeable images": self.cell(u, ds, "false_abst_rate", ci=False)})
        if rows:
            self.write("table1_zero_shot", pd.DataFrame(rows), "Table 1. Zero-shot performance of released models",
                       "QWK: quadratic weighted kappa on five grades. Referable: grade 2 or worse (grade-only definition). Probabilities temperature-scaled on the EyePACS calibration split.")

    def table2(self):
        rows = []
        for u in self.by_arm(["A", "B", "C", "G", "S"]):
            for ds in self.datasets + ["pooled_external"]:
                if np.isnan(self.val(u, ds, "qwk")):
                    continue
                rows.append({"Model": u, "Arm": ARM_NAMES.get(self.arm[u], self.arm[u]), "Dataset": ds, "Gradeable images": self.n(u, ds, "n_gradable"),
                             "QWK": self.cell(u, ds, "qwk"), "Referable AUROC": self.cell(u, ds, "ref_auroc"),
                             "Referable sensitivity": self.cell(u, ds, "ref_sens"), "Referable specificity": self.cell(u, ds, "ref_spec"),
                             "Grade ECE": self.cell(u, ds, "ece_grade"), "AURC": self.cell(u, ds, "aurc_grade")})
        if rows:
            self.write("table2_main", pd.DataFrame(rows), "Table 2. Fine-tuned decision models, specialist and generative baselines",
                       "Values are point estimates with 95% patient-clustered bootstrap intervals. Sensitivity and specificity use the threshold fixed on the "
                       "calibration split for 90% sensitivity. Seeds of one arm are pooled.")

    def table3(self):
        rows = []
        for u in self.units:
            for ds in self.datasets:
                if not self.val(u, ds, "n_ungradable") > 0:
                    continue
                rows.append({"Model": u, "Dataset": ds, "Ungradeable images": self.n(u, ds, "n_ungradable"),
                             "Gradeability AUROC (Q1)": self.cell(u, ds, "grad_auroc"), "Ungradeable detected (Q1)": self.cell(u, ds, "grad_sens"),
                             "Gradeable kept (Q1)": self.cell(u, ds, "grad_spec"), "Unknown-probability AUROC (Q2)": self.cell(u, ds, "abst_auroc"),
                             "Abstained on ungradeable (Q2)": self.cell(u, ds, "abst_rate_ungradable"),
                             "Abstained on gradeable (Q2)": self.cell(u, ds, "false_abst_rate")})
        if rows:
            self.write("table3_abstention", pd.DataFrame(rows), "Table 3. Gradeability and abstention on ungradeable images")

    def table3b(self):
        rows = []
        for u in self.units:
            for ds in self.datasets + ["pooled_external"]:
                if np.isnan(self.val(u, ds, "qwk")):
                    continue
                has_mac = self.val(u, ds, "n_mac") > 0
                rows.append({"Model": u, "Dataset": ds,
                             "Refer, grade-only: sens / spec": f"{self.cell(u, ds, 'ref_sens', ci=False)} / {self.cell(u, ds, 'ref_spec', ci=False)}",
                             "Refer, action rule: sens / spec": f"{self.cell(u, ds, 'ref_sens_action', ci=False)} / {self.cell(u, ds, 'ref_spec_action', ci=False)}",
                             "Share referred under action rule": self.cell(u, ds, "referral_rate_action", ci=False),
                             "Sight-threatening, grade-only: AUROC": self.cell(u, ds, "st_auroc"),
                             "Sight-threatening, grade-only: sens / spec": f"{self.cell(u, ds, 'st_sens', ci=False)} / {self.cell(u, ds, 'st_spec', ci=False)}",
                             "Maculopathy AUROC": self.cell(u, ds, "mac_auroc") if has_mac else "no labels",
                             "Refer, full definition: AUROC": self.cell(u, ds, "reffull_auroc_direct") if has_mac else "no labels",
                             "Sight-threatening, full definition: AUROC": self.cell(u, ds, "stfull_auroc_direct") if has_mac else "no labels"})
        if rows:
            self.write("table3b_clinical", pd.DataFrame(rows), "Table 3b. Clinical decisions: referral, sight-threatening disease and maculopathy",
                       "Action rule: refer if referable disease, ungradeable, or the model abstains. Full definition adds maculopathy and is reported only where maculopathy is labelled.")

    def table3c(self):
        rows = []
        for u in self.units:
            for ds in self.datasets:
                if np.isnan(self.val(u, ds, "qwk")):
                    continue
                rows.append({"Model": u, "Dataset": ds, "Coherent answers": self.cell(u, ds, "coherence"),
                             "Referable AUROC, direct": self.cell(u, ds, "ref_auroc_direct", ci=False),
                             "Referable AUROC, derived": self.cell(u, ds, "ref_auroc_derived", ci=False),
                             "Direct minus derived": self.cell(u, ds, "ref_auroc_dir_minus_der"),
                             "Patient-level refer: sens / spec": f"{self.cell(u, ds, 'patient_ref_sens', ci=False)} / {self.cell(u, ds, 'patient_ref_spec', ci=False)}"})
        if rows:
            self.write("table3c_coherence", pd.DataFrame(rows), "Table 3c. Coherence of the five answers, direct versus derived referral, patient-level referral",
                       "Coherent: the referral and sight-threatening answers agree with the grade and maculopathy answers. Patient level uses the worse eye and equals image level where a dataset has no patient identifiers.")

    def table4(self):
        f = self.res / "prompt_sensitivity.csv"
        ps = pd.read_csv(f) if f.exists() and f.stat().st_size > 5 else pd.DataFrame()
        if len(ps):
            t = ps[["unit", "dataset", "metric", "n_wordings", "mean", "min", "max", "range"]].round(3)
            t.columns = ["Model", "Dataset", "Metric", "Wordings", "Mean", "Lowest", "Highest", "Range"]
            self.write("table4a_prompt_sensitivity", t, "Table 4a. Sensitivity to question wording (fixed subset of each test set)")
        rows = []
        for u in self.units:
            for ds in self.datasets:
                r = self.raw[(self.raw["unit"] == u) & (self.raw["dataset"] == ds)].set_index("metric")["value"]
                if r.empty:
                    continue
                rows.append({"Model": u, "Dataset": ds, "Grade ECE, raw": _fmt(r.get("ece_grade")), "Grade ECE, calibrated": self.cell(u, ds, "ece_grade", ci=False),
                             "Referable ECE, raw": _fmt(r.get("ece_ref")), "Referable ECE, calibrated": self.cell(u, ds, "ece_ref", ci=False),
                             "AURC, raw": _fmt(r.get("aurc_grade")), "AURC, calibrated": self.cell(u, ds, "aurc_grade", ci=False)})
        if rows:
            self.write("table4b_calibration_effect", pd.DataFrame(rows), "Table 4b. Effect of temperature scaling fitted on the EyePACS calibration split")

    def table5(self):
        f = self.res / "deployment.csv"
        if f.exists() and f.stat().st_size > 5:
            t = pd.read_csv(f).drop(columns=["synthetic"]).round(1)
            t.columns = ["Model", "Arm", "Adapter", "Repository", "Revision", "Decisions timed", "Median ms per decision", "95th percentile ms"]
            self.write("table5_deployment", t, "Table 5. Latency as measured during prediction",
                       "Wall-clock time per question on the hardware used for the run; record that hardware alongside this table.")

    def tests(self):
        f = self.res / "comparisons.csv"
        if not f.exists() or f.stat().st_size < 5:
            return None
        c = pd.read_csv(f)
        c["passed"] = c["passed"].astype(str) == "True"      # the csv holds True / False / empty
        rows = []
        for r in c.itertuples():
            if r.status != "ok":
                rows.append({"Test": r.id, "Type": r.test, "Metric": r.metric, "Dataset": r.dataset, "Model": r.model, "Reference": r.reference,
                             "Model value": "–", "Reference value": "–", "Advantage (95% CI)": "–", "Margin": "–", "p": "–", "Holm p": "–", "Result": r.status})
                continue
            res = ("non-inferior" if r.passed else "not shown non-inferior") if r.test == "noninferiority" else ("superior" if r.passed else "not shown superior")
            rows.append({"Test": r.id, "Type": r.test, "Metric": r.metric, "Dataset": r.dataset, "Model": r.model, "Reference": r.reference,
                         "Model value": _fmt(r.model_value), "Reference value": _fmt(r.reference_value),
                         "Advantage (95% CI)": _fmt(r.advantage, r.ci_low, r.ci_high), "Margin": _fmt(r.margin, d=2) if r.test == "noninferiority" else "–",
                         "p": _fmt(r.p_value, d=4), "Holm p": _fmt(r.p_holm, d=4) if r.primary else "not primary", "Result": res + (" (Holm)" if r.primary else "")})
        self.write("hypothesis_tests", pd.DataFrame(rows), "Pre-specified comparisons",
                   "Advantage is model minus reference, sign-flipped for metrics where lower is better, so positive favours the model. Tests are one-sided at 2.5%, "
                   "from the paired patient-level bootstrap. Primary tests are decided on the Holm-adjusted p-value over the whole pre-specified primary family; "
                   "a primary test that could not be run counts as failed. Intervals are unadjusted.")
        return c

    # ---- figures ----
    def _axes(self, n, title, xlabel, ylabel, w=3.1, h=2.9):
        cols = min(n, 3)
        rws = int(np.ceil(n / cols))
        fig, axes = plt.subplots(rws, cols, figsize=(w * cols + 0.6, h * rws + 0.9), squeeze=False)
        for ax in axes.flat:
            ax.set_visible(False)
        fig.suptitle(title + (f"\n{STAMP}" if self.synthetic else ""), fontsize=10, color=INK, x=0.02, ha="left")
        for k in range(n):
            ax = axes.flat[k]
            if k // cols == (n - 1) // cols or k + cols >= n:
                ax.set_xlabel(xlabel, fontsize=8, color=MUTED)
            if k % cols == 0:
                ax.set_ylabel(ylabel, fontsize=8, color=MUTED)
        return fig, axes

    @staticmethod
    def _style(ax, title):
        ax.set_visible(True)
        ax.set_title(title, fontsize=9, color=INK, loc="left")
        ax.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=8, length=0)

    def _save(self, fig, name, handles_from=None):
        fig.tight_layout()
        if handles_from is not None:
            h, l = handles_from.get_legend_handles_labels()
            if len(h) > 1:                                  # one series needs no legend: the title names it
                fig.legend(h, l, loc="upper center", ncol=min(4, len(h)), fontsize=8, frameon=False, labelcolor=INK, bbox_to_anchor=(0.5, 0.0))
        for ext in ("png", "pdf"):
            fig.savefig(self.fig / f"{name}.{ext}", dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    def figure_units(self) -> list[str]:
        """Models drawn in the line figures: the first full-data model of each arm, so panels stay readable."""
        out = []
        for a in ("B", "A", "C", "S", "G", "Z"):
            c = [u for u in self.by_arm([a]) if self.full_data(u)]
            out += c[:1]
        return out

    def full_data(self, u) -> bool:
        size = (self.cfg.runs[self.cfg.units()[u][0]].get("train") or {}).get("train_size")
        return size in (None, "full")

    def _frames(self, units, ds, split):
        runs = self.cfg.units()
        out = {}
        for u in units:
            f = frames.unit_frame(self.cfg, self.man, [r for r in runs[u] if (self.cfg.preds_dir / r).exists()], ds, split)
            if f is not None:
                ev = f["grade"].notna() & (f["gradable"] != 0)
                out[u] = f[ev]
        return out

    def fig_reliability_and_risk(self):
        sets = [(d, "test_internal" if (self.m[(self.m["dataset"] == d)]["split"] == "test_internal").any() else "test") for d in self.datasets]
        units = self.figure_units()
        if not units or not sets:
            return
        bins = 10                                            # display bins; the ECE in the tables uses the protocol's bins
        fig1, ax1 = self._axes(len(sets), "Figure 1. Reliability of the grade answer", "Stated confidence in the chosen grade", "Share of answers that were correct")
        fig2, ax2 = self._axes(len(sets), "Figure 2. Selective prediction: error among the most confident answers", "Share of images answered (most confident first)", "Grading error rate")
        last1 = last2 = None
        for k, (ds, split) in enumerate(sets):
            fr = self._frames(units, ds, split)
            a1, a2 = ax1.flat[k], ax2.flat[k]
            self._style(a1, ds)
            self._style(a2, ds)
            a1.plot([0, 1], [0, 1], color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
            for u, f in fr.items():
                pg = f[[f"pg{i}" for i in range(5)]].to_numpy()
                conf, ok = pg.max(1), (pg.argmax(1) == f["grade"].to_numpy(int)).astype(float)
                b = np.minimum((conf * bins).astype(int), bins - 1)
                cnt = np.bincount(b, minlength=bins)
                keep = cnt >= max(5, 0.01 * len(conf))
                x = np.bincount(b, weights=conf, minlength=bins)[keep] / cnt[keep]
                y = np.bincount(b, weights=ok, minlength=bins)[keep] / cnt[keep]
                a1.plot(x, y, color=self.color[u], marker=self.marker[u], markersize=4, linewidth=1.6, label=u)
                sel = conf * (1 - np.nan_to_num(f["u2"].to_numpy(float), nan=0.0))
                risk = M._risk_curve(sel, ok)
                cov = np.arange(1, len(risk) + 1) / len(risk)
                start = max(1, int(0.05 * len(risk)))
                a2.plot(cov[start:], risk[start:], color=self.color[u], linewidth=1.6, label=u)
                idx = np.linspace(start, len(risk) - 1, 5).astype(int)
                a2.plot(cov[idx], risk[idx], linestyle="none", marker=self.marker[u], markersize=4, color=self.color[u])
            a1.set_xlim(0.15, 1.02)
            a1.set_ylim(0, 1.02)
            a2.set_xlim(0, 1.02)
            a2.set_ylim(bottom=0)
            last1, last2 = a1, a2
        self._save(fig1, "fig1_reliability", last1)
        self._save(fig2, "fig2_risk_coverage", last2)

    def fig_zero_shot(self):
        units = self.by_arm(["Z"])
        if not units:
            return
        fig, axes = self._axes(len(self.datasets), "Figure S1. Zero-shot grading agreement by dataset", "Quadratic weighted kappa (95% CI)", "")
        for k, ds in enumerate(self.datasets):
            ax = axes.flat[k]
            self._style(ax, ds)
            for i, u in enumerate(units):
                r = self.m[(self.m["unit"] == u) & (self.m["dataset"] == ds) & (self.m["metric"] == "qwk")]
                if r.empty:
                    continue
                r = r.iloc[0]
                ax.plot([r["ci_low"], r["ci_high"]], [i, i], color=self.color[u], linewidth=1.6)
                ax.plot(r["value"], i, marker=self.marker[u], color=self.color[u], markersize=6)
            ax.set_yticks(range(len(units)))
            ax.set_yticklabels(units if k % 3 == 0 else [""] * len(units), fontsize=8, color=INK)
            ax.set_ylim(-0.6, len(units) - 0.4)
            ax.invert_yaxis()
            ax.set_xlim(min(0, ax.get_xlim()[0]), 1)
        self._save(fig, "figS1_zero_shot_qwk")

    def fig_efficiency(self):
        n_full = int(((self.man["split"] == "train")).sum())
        pts = []
        for u, runs in self.cfg.units().items():
            if u not in self.units:
                continue
            size = (self.cfg.runs[runs[0]].get("train") or {}).get("train_size")
            if size is None:
                continue
            pts.append((self.arm[u], n_full if size == "full" else int(size), u))
        arms = sorted({a for a, _, _ in pts})
        if not pts or max(len([p for p in pts if p[0] == a]) for a in arms) < 2:
            return
        sets = [d for d in self.cfg.analysis["primary_datasets"] + ["pooled_external"] if d in set(self.m["dataset"])]
        fig, axes = self._axes(len(sets), "Figure 3. Grading agreement by number of training images", "Training images (log scale)", "Quadratic weighted kappa (95% CI)")
        last = None
        for k, ds in enumerate(sets):
            ax = axes.flat[k]
            self._style(ax, ds)
            for j, a in enumerate(arms):
                p = sorted((n, u) for aa, n, u in pts if aa == a)
                rows = [self.m[(self.m["unit"] == u) & (self.m["dataset"] == ds) & (self.m["metric"] == "qwk")] for _, u in p]
                if any(r.empty for r in rows):
                    continue
                x = [n for n, _ in p]
                y = [r["value"].iloc[0] for r in rows]
                lo = [r["value"].iloc[0] - r["ci_low"].iloc[0] for r in rows]
                hi = [r["ci_high"].iloc[0] - r["value"].iloc[0] for r in rows]
                big = p[-1][1]                              # the arm wears the colour of its full-data model in every figure
                ax.errorbar(x, y, yerr=[lo, hi], color=self.color[big], marker=self.marker[big], markersize=5, linewidth=1.6, capsize=2, label=ARM_NAMES.get(a, a))
            ax.set_xscale("log")
            ticks = sorted({n for _, n, _ in pts})
            ax.set_xticks(ticks)
            ax.set_xticklabels([f"{t:,}" for t in ticks])
            ax.minorticks_off()
            last = ax
        self._save(fig, "fig3_data_efficiency", last)

    def fig_confusion(self):
        units = (self.by_arm(["B"]) or self.by_arm(["A"]) or self.units)[:1] + self.by_arm(["S"])[:1]
        sets = [(d, "test") for d in self.cfg.analysis["primary_datasets"] if d in self.datasets]
        if not units or not sets:
            return
        fig, axes = plt.subplots(len(units), len(sets), figsize=(3.3 * len(sets) + 0.5, 3.1 * len(units) + 0.8), squeeze=False)
        fig.suptitle("Figure S2. Confusion matrices, row-normalised (reference grade in rows)" + (f"\n{STAMP}" if self.synthetic else ""), fontsize=10, color=INK, x=0.02, ha="left")
        for i, u in enumerate(units):
            for j, (ds, split) in enumerate(sets):
                ax = axes[i][j]
                f = self._frames([u], ds, split).get(u)
                if f is None:
                    ax.set_visible(False)
                    continue
                cm = np.zeros((5, 5))
                np.add.at(cm, (f["grade"].to_numpy(int), f[[f"pg{k}" for k in range(5)]].to_numpy().argmax(1)), 1)
                rn = cm / np.maximum(cm.sum(1, keepdims=True), 1)
                ax.imshow(rn, cmap="Blues", vmin=0, vmax=1)
                for a in range(5):
                    for b in range(5):
                        ax.text(b, a, f"{int(cm[a, b])}", ha="center", va="center", fontsize=7, color="white" if rn[a, b] > 0.55 else INK)
                pooled = " (seeds pooled)" if f["run"].nunique() > 1 else ""
                ax.set_title(f"{u}: {ds}{pooled}", fontsize=9, color=INK, loc="left")
                ax.set_xticks(range(5))
                ax.set_yticks(range(5))
                ax.tick_params(colors=MUTED, labelsize=8, length=0)
                ax.set_xlabel("Model grade", fontsize=8, color=MUTED)
                ax.set_ylabel("Reference grade", fontsize=8, color=MUTED)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(self.fig / f"figS2_confusion.{ext}", dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    # ---- per-image release and provenance ----
    def per_image(self):
        out = self.res / "per_image"
        out.mkdir(exist_ok=True)
        runs = self.cfg.units()
        cols = ["image_id", "run", "grade", "gradable", "maculopathy", "pg0", "pg1", "pg2", "pg3", "pg4", "u2", "pgrad", "pmac", "u3", "pref", "u4", "pst", "u5"]
        for u in self.units:
            parts = []
            for ds in self.datasets:
                for split in ("test", "test_internal"):
                    f = frames.unit_frame(self.cfg, self.man, [r for r in runs[u] if (self.cfg.preds_dir / r).exists()], ds, split)
                    if f is not None:
                        parts.append(f[cols].assign(dataset=ds, split=split))
            if parts:
                pd.concat(parts).round(5).to_csv(out / f"{u}.csv.gz", index=False)

    def manifest(self):
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.cfg.base, capture_output=True, text=True).stdout.strip()
        except OSError:
            commit = ""
        lock = json.loads(self.cfg.lock_file.read_text()) if self.cfg.lock_file.exists() else None
        info = {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "pipeline_version": __version__, "pipeline_commit": commit,
                "python": platform.python_version(), "synthetic": self.synthetic, "seed": self.cfg.seed, "lock": lock,
                "analysis": self.cfg.analysis, "splits": self.cfg.splits,
                "runs": {r: {k: v for k, v in s.items() if k != "server"} for r, s in self.cfg.runs.items() if (self.cfg.preds_dir / r).exists()}}
        log = self.cfg.work / "test_access_log.jsonl"
        if log.exists():
            info["test_set_reads"] = [json.loads(x) for x in log.read_text().splitlines() if x.strip()]
        (self.res / "run_manifest.json").write_text(json.dumps(info, indent=2, default=str) + "\n")

    def summary(self, comps):
        L = ["# Results summary", ""]
        if self.synthetic:
            L += [f"**{STAMP}**", ""]
        L += [f"Generated {datetime.date.today().isoformat()} by drjev {__version__}. Models analysed: {len(self.units)}. Test sets: {', '.join(self.datasets)}.", ""]
        prim = [d for d in self.cfg.analysis["primary_datasets"] if d in self.datasets]
        if comps is not None and len(comps):
            ok = comps[comps["status"] == "ok"]
            L += ["## Pre-specified tests", ""]
            for r in ok.itertuples():
                word = {("noninferiority", True): "non-inferior to", ("noninferiority", False): "not shown non-inferior to",
                        ("superiority", True): "better than", ("superiority", False): "not shown better than"}[(r.test, bool(r.passed))]
                L.append(f"- **{r.id}** ({r.dataset}, {r.metric}): {r.model} was {word} {r.reference}; {r.model_value:.3f} versus {r.reference_value:.3f}, "
                         f"advantage {r.advantage:+.3f} (95% CI {r.ci_low:+.3f} to {r.ci_high:+.3f})" + (f", margin {r.margin:.2f}" if r.test == "noninferiority" else "") + ".")
            for r in comps[comps["status"] != "ok"].itertuples():
                L.append(f"- **{r.id}** ({r.dataset}): {r.status}.")
            prim_rows = comps[comps["primary"]]
            if len(prim_rows):
                good = lambda d: (d["status"] == "ok") & (d["passed"].astype(str) == "True")
                h2 = prim_rows[prim_rows["id"].str.startswith("H2")]
                other = comps[comps["id"].str.startswith(("H3", "H4"))]
                L += ["", "## Decision gate G3", ""]
                if len(h2) and good(h2).all() and good(other).any():
                    L.append("Every primary H2 test passed after Holm adjustment and at least one H3 or H4 test passed: the positive-paper condition is met on these data.")
                else:
                    L.append("The positive-paper condition (every primary H2 test passed after Holm adjustment, plus at least one H3 or H4 test) is **not** met on these data; "
                             "the pre-planned alternative is the negative-result paper.")
            L.append("")
        if prim:
            L += ["## Headline numbers on the primary external test sets", ""]
            for u in [x for x in self.by_arm(["B", "A", "S", "G"]) + self.by_arm(["Z"]) if self.full_data(x)]:
                bits = [f"{ds}: QWK {self.cell(u, ds, 'qwk')}, referable AUROC {self.cell(u, ds, 'ref_auroc')}, grade ECE {self.cell(u, ds, 'ece_grade', ci=False)}" for ds in prim
                        if not np.isnan(self.val(u, ds, "qwk"))]
                if bits:
                    L.append(f"- {self.label(u)}. " + "; ".join(bits) + ".")
            L.append("")
        inc = self.res / "incomplete.csv"
        if inc.exists() and inc.stat().st_size > 80:
            L += ["## Models left out for missing predictions", ""] + [f"- {r.unit} on {r.dataset}: {r.predicted_images} of {r.expected_images} images" for r in pd.read_csv(inc).itertuples()] + [""]
        notes = []
        cal = json.loads((self.res / "calibration.json").read_text()) if (self.res / "calibration.json").exists() else {}
        for r, c in cal.items():
            notes += [f"- {r}: {n}" for n in c.get("notes", [])]
        if notes:
            L += ["## Calibration notes", ""] + notes + [""]
        L += ["## Files", "", "- `tables/`: every table as .csv and .md", "- `figures/`: every figure as .png and .pdf",
              "- `metrics_long.csv`: every metric, model and dataset with intervals", "- `comparisons.csv`: the pre-specified tests",
              "- `per_image/`: calibrated per-image predictions (image identifiers only, no images)", "- `run_manifest.json`: configuration, model revisions, lock and test-set access log", ""]
        (self.res / "summary.md").write_text("\n".join(L))
        (self.res / "all_tables.md").write_text("\n".join(self.md_parts))


def run(cfg):
    r = Reporter(cfg)
    r.table0()
    r.table1()
    r.table2()
    r.table3()
    r.table3b()
    r.table3c()
    r.table4()
    r.table5()
    comps = r.tests()
    r.fig_reliability_and_risk()
    r.fig_zero_shot()
    r.fig_efficiency()
    r.fig_confusion()
    r.per_image()
    r.manifest()
    r.summary(comps)
    print(f"report: tables, figures and summary -> {cfg.results}")


def status(cfg):
    print(f"workspace: {cfg.base}")
    if not cfg.manifest.exists():
        print("  manifest: not built (run `drjev ingest`, `preprocess`, `split`, or `drjev run`)")
        return
    man = load_manifest(cfg)
    print(f"  manifest: {len(man)} images; " + ", ".join(f"{k} {v}" for k, v in man["split"].value_counts().items()))
    print(f"  protocol lock: {'yes' if cfg.lock_file.exists() else 'NO (test sets cannot be read)'}")
    for name, spec in cfg.runs.items():
        d = cfg.preds_dir / name
        n = sum(1 for f in d.glob("*__v0.jsonl")) if d.exists() else 0
        cal = "calibrated" if (cfg.calib_dir / f"{name}.json").exists() else "not calibrated"
        print(f"  {name:28s} arm {spec.get('arm', '?')}  enabled={bool(spec.get('enabled'))}  prediction files={n}  {cal}")
    print(f"  results: {'present' if (cfg.results / 'metrics_long.csv').exists() else 'none yet'}")
