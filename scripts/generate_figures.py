"""Regenerate the article figures in English from the MonitorSystem datasets.

Run with the Visualizer virtualenv (monitorviz installed, editable):

    /home/yisus/PycharmProjects/Visualizer/.venv/bin/python scripts/generate_figures.py

Reads data from the Visualizer repo (read-only) and writes PNGs into
figures/ at the root of this conversion project. Differences with respect to
the thesis figures:
  * all labels/legends in English, no in-figure suptitles (captions carry them)
  * model labels cleaned ("ministral (L)" -> "Ministral-3B")
  * perplexity figure drops the non-K-quant (Q4_0/Q8_0) bars of DeepSeek,
    consistent with their exclusion from the E1 analysis (model collapse)
"""

from __future__ import annotations

import json
import re
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D

VIS_ROOT = Path("/home/yisus/PycharmProjects/Visualizer")
DATA = VIS_ROOT / "data" / "TFG-DATA"
OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(exist_ok=True)

sys.path.insert(0, str(VIS_ROOT / "src"))
from monitorviz.io import load_collection  # noqa: E402
from monitorviz.transforms.collection import RunCollection  # noqa: E402
from monitorviz.transforms.fom import compute_fom_full, compute_usability  # noqa: E402
from monitorviz.viz import setup_style  # noqa: E402

warnings.filterwarnings("ignore")
setup_style()
matplotlib.rcParams["figure.dpi"] = 300
DPI = 300

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

CLEAN_LABELS = {
    "deepseek": "DeepSeek-R1-1.5B",
    "llama-3.2-1b": "Llama-3.2-1B",
    "llama-3.2-3b": "Llama-3.2-3B",
    "gemma": "Gemma-3n",
    "granite": "Granite-4.0-H",
    "ministral": "Ministral-3B",
}


def clean_label(label: str) -> str:
    low = str(label).lower()
    for key, val in CLEAN_LABELS.items():
        if key in low:
            return val
    return str(label)


def save(fig: plt.Figure, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {path}")


MARKER_POOL = ["o", "s", "^", "D", "v", "P", "X", "*", "h", "<"]
FAN_COLORS = {True: "steelblue", False: "tomato"}
FAN_LABELS = {True: "Fan", False: "No fan"}

# ---------------------------------------------------------------------------
# E0 — load collections (FAN + NOFAN), build summary/hw/pm, FoM, usability
# ---------------------------------------------------------------------------

print("Loading E0 ...")
runs_fan = [r for r in load_collection(DATA / "E0-FAN").runs
            if r.summary.inference_engine == "LLAMA"]
runs_nofan = [r for r in load_collection(DATA / "E0-NOFAN").runs
              if r.summary.inference_engine == "LLAMA"]
coll0 = RunCollection(runs_fan + runs_nofan)
summary0 = coll0.summary_df()
hw0 = coll0.hw_metrics_df()
pm0 = coll0.prompt_metrics_df()

fom0 = compute_fom_full(summary0)
if not pm0.empty:
    fom0, _ = compute_usability(fom0, pm0)
fom0["model_clean"] = fom0["model_label"].map(clean_label)

# runtime RAM per run from hardware samples
ram_rt = hw0.groupby("run_id")["mem_used_bytes"].mean().reset_index()
ram_rt["ram_used_gb"] = ram_rt["mem_used_bytes"] / 1e9
fom0 = fom0.merge(ram_rt[["run_id", "ram_used_gb"]], on="run_id", how="left")

# ---------------------------------------------------------------------------
# Figure 1 — E0 Pareto frontier (throughput vs RAM footprint)
# ---------------------------------------------------------------------------


def pareto_front(df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    pts = df[[x_col, y_col]].to_numpy()
    n = len(pts)
    dom = [False] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if (pts[j, 0] <= pts[i, 0] and pts[j, 1] >= pts[i, 1]
                    and (pts[j, 0] != pts[i, 0] or pts[j, 1] != pts[i, 1])):
                dom[i] = True
                break
    return df.iloc[[not d for d in dom]].sort_values(x_col)


pd_par = fom0.dropna(subset=["ram_used_gb", "tokens_per_s_mean"]).copy()
models0 = sorted(pd_par["model_clean"].unique())
mk_map0 = {m: MARKER_POOL[i % len(MARKER_POOL)] for i, m in enumerate(models0)}

fig, ax = plt.subplots(figsize=(10, 6))
for fan_val in [True, False]:
    sub = pd_par[pd_par["fan"] == fan_val]
    for _, row in sub.iterrows():
        sz = float(row["fom_full"]) * 400 if pd.notna(row.get("fom_full")) else 150
        ax.scatter(row["ram_used_gb"], row["tokens_per_s_mean"],
                   s=max(sz, 30), c=FAN_COLORS[fan_val],
                   marker=mk_map0[row["model_clean"]],
                   alpha=0.80, zorder=3, edgecolors="white", linewidths=0.7)

front = pareto_front(pd_par, "ram_used_gb", "tokens_per_s_mean")
if len(front) > 1:
    ax.step(front["ram_used_gb"], front["tokens_per_s_mean"],
            where="post", color="black", lw=1.5, ls="--", zorder=2)

t_hum_mean = float(pd_par["T_hum"].mean()) if "T_hum" in pd_par.columns else None
if t_hum_mean is not None and np.isfinite(t_hum_mean):
    ax.axhline(t_hum_mean, ls=":", lw=2, color="darkorange", zorder=1)

handles = [Line2D([0], [0], marker=mk_map0[m], color="gray", ls="None",
                  markersize=8, label=m) for m in models0]
handles += [mpatches.Patch(facecolor=FAN_COLORS[v], edgecolor="white",
                           linewidth=0.7, label=FAN_LABELS[v])
            for v in [True, False]]
handles += [Line2D([0], [0], color="black", ls="--", lw=1.5, label="Pareto frontier")]
if t_hum_mean is not None and np.isfinite(t_hum_mean):
    handles += [Line2D([0], [0], color="darkorange", ls=":", lw=2,
                       label=f"$T_{{hum}} \\approx {t_hum_mean:.1f}$ tok/s")]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1),
          fontsize=8, framealpha=0.9)
ax.set_xlabel("Runtime RAM footprint (GBytes)")
ax.set_ylabel("Throughput (tok/s)")
ax.grid(True, alpha=0.3)
fig.tight_layout()
save(fig, "e0_pareto.png")

# ---------------------------------------------------------------------------
# Figure 2 — E0 FoM decomposition (5 panels, fan vs no fan)
# ---------------------------------------------------------------------------

FOM_AXES = {
    "fom_T_norm": ("$\\tilde{T}$", "Normalized throughput"),
    "fom_MBU_norm": ("$\\widetilde{MBU}$", "Bandwidth utilization"),
    "fom_eta_norm": ("$\\tilde{\\eta}$", "CPU efficiency"),
    "fom_eps_norm": ("$\\tilde{\\varepsilon}$", "Energy efficiency"),
    "fom_full": ("$FoM_{full}$", "Overall figure of merit"),
}
PANEL = ["(a)", "(b)", "(c)", "(d)", "(e)"]

fom0["_fan_label"] = fom0["fan"].map(FAN_LABELS)
avail = [c for c in FOM_AXES if c in fom0.columns and fom0[c].notna().any()]
ncols = 3
nrows = (len(avail) + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 4.2))
axes_flat = axes.flatten()
for idx, (ax, col) in enumerate(zip(axes_flat, avail)):
    d = fom0.dropna(subset=[col])
    sns.barplot(data=d, x="model_clean", y=col, hue="_fan_label",
                hue_order=["Fan", "No fan"], ax=ax)
    math_lbl, desc_lbl = FOM_AXES[col]
    ax.set_title(f"{PANEL[idx]} {desc_lbl}\n{math_lbl}",
                 fontsize=10, fontweight="bold", loc="left", pad=6)
    ax.set_xlabel("")
    ax.set_ylabel(math_lbl, fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right", fontsize=8)
    ax.axhline(1.0, ls="--", color="gray", alpha=0.5, lw=1)
    ax.grid(True, axis="y", alpha=0.25)
    if ax.get_legend():
        ax.get_legend().remove()
for ax in axes_flat[len(avail):]:
    ax.set_visible(False)
h, lab = axes_flat[0].get_legend_handles_labels()
if not h:
    h = [mpatches.Patch(color=sns.color_palette()[i], label=v)
         for i, v in enumerate(["Fan", "No fan"])]
    lab = ["Fan", "No fan"]
fig.legend(h, lab, loc="upper center", bbox_to_anchor=(0.5, 1.04),
           ncol=2, fontsize=10)
fig.tight_layout(pad=2.0)
save(fig, "e0_fom_decomposition.png")

# ---------------------------------------------------------------------------
# Figure 3 — E0 cooling impact (throughput increase fan vs no fan)
# ---------------------------------------------------------------------------

summary0["model_clean"] = summary0["model_label"].map(clean_label)
fan_mean = summary0[summary0["fan"]].groupby("model_clean")["tokens_per_s_mean"].mean()
nofan_mean = summary0[~summary0["fan"]].groupby("model_clean")["tokens_per_s_mean"].mean()
common = fan_mean.index.intersection(nofan_mean.index)
diff_pct = (fan_mean.loc[common] - nofan_mean.loc[common]) / nofan_mean.loc[common] * 100
diff_pct = diff_pct.sort_values()

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["forestgreen" if v > 0 else "firebrick" for v in diff_pct]
ax.barh(diff_pct.index.tolist(), diff_pct.values, color=colors, alpha=0.85)
ax.axvline(0, color="black", lw=1)
ax.set_xlabel("Throughput increase (%), fan vs. no fan")
ax.grid(True, axis="x", alpha=0.3)
fig.tight_layout()
save(fig, "e0_cooling_impact.png")

# ---------------------------------------------------------------------------
# Figure 4 — E0 per-phase duration breakdown (load / prefill / decode),
# log scale, fan vs no fan; (a) mean per prompt, (b) total per run
# ---------------------------------------------------------------------------

PHASES_PER_PROMPT = [("load_s", "Load", "#bcbd22"),
                     ("prefill_s", "Prefill", "#17becf"),
                     ("decode_s", "Decode", "#ff7f0e")]
PHASES_TOTAL = [("load_total_s", "Load", "#bcbd22"),
                ("prefill_total_s", "Prefill", "#17becf"),
                ("decode_total_s", "Decode", "#ff7f0e")]

phase_rows = []
for run in coll0.runs:
    meta = summary0[summary0["run_id"] == run.run_id]
    if meta.empty:
        continue
    non_empty = [p for p in run.prompts if not p.is_empty_generation]
    if not non_empty:
        continue
    load = np.array([p.load_duration_ns / 1e9 for p in non_empty])
    prefill = np.array([p.prompt_eval_duration_ns / 1e9 for p in non_empty])
    decode = np.array([p.eval_duration_ns / 1e9 for p in non_empty])
    phase_rows.append(dict(
        model_clean=clean_label(meta["model_label"].values[0]),
        fan=bool(meta["fan"].values[0]),
        load_s=load.mean(), prefill_s=prefill.mean(), decode_s=decode.mean(),
        load_total_s=load.sum(), prefill_total_s=prefill.sum(),
        decode_total_s=decode.sum(),
    ))
pf = pd.DataFrame(phase_rows)

models_ph = sorted(pf["model_clean"].unique())
BAR_H = 0.30      # bar height
GAP = 0.05        # fan / no-fan separation inside a model group
SEP = 0.45        # separation between model groups
STEP = 2 * BAR_H + GAP + SEP
FLOOR = 1e-4      # positive origin for the log scale

fig, axes = plt.subplots(1, 2, figsize=(11, max(4.5, len(models_ph) * 0.9)))
for ax, phases, subtitle in [
    (axes[0], PHASES_PER_PROMPT, "(a) Mean per prompt"),
    (axes[1], PHASES_TOTAL, "(b) Total per run"),
]:
    ax.set_xscale("log")
    yticks, ylabels = [], []
    for mi, model in enumerate(models_ph):
        y_group = mi * STEP
        yticks.append(y_group + BAR_H + GAP / 2)
        ylabels.append(model)
        for fi, (fan_val, hatch) in enumerate([(True, ""), (False, "///")]):
            sub = pf[(pf["model_clean"] == model) & (pf["fan"] == fan_val)]
            if sub.empty:
                continue
            y_pos = y_group + fi * (BAR_H + GAP)
            left = FLOOR
            for col, _lbl, color in phases:
                val = max(float(sub[col].values[0]), FLOOR)
                ax.barh(y_pos, val, height=BAR_H, left=left, color=color,
                        hatch=hatch, edgecolor="grey", linewidth=0.4, alpha=0.9)
                left += val
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=12)
    ax.tick_params(axis="x", labelsize=11)
    ax.set_xlabel("Duration (s)", fontsize=12)
    ax.set_title(subtitle, fontsize=12)
    ax.grid(True, axis="x", alpha=0.3, which="both")
    ax.invert_yaxis()

ph_handles = [mpatches.Patch(color=c, label=lbl) for _, lbl, c in PHASES_PER_PROMPT]
cond_handles = [
    mpatches.Patch(facecolor="lightgrey", edgecolor="grey", label="Fan"),
    mpatches.Patch(facecolor="lightgrey", edgecolor="grey", hatch="///",
                   label="No fan"),
]
sep_handle = Line2D([0], [0], color="none", label=" ")
fig.legend(handles=ph_handles + [sep_handle] + cond_handles,
           loc="upper center", bbox_to_anchor=(0.5, 1.14),
           ncol=len(ph_handles) + 1 + len(cond_handles), fontsize=11,
           title="Phase  \u2502  Cooling condition", title_fontsize=11,
           frameon=True, edgecolor="grey")
fig.tight_layout()
save(fig, "e0_phase_breakdown.png")

# report the ranges quoted in the text
for col, lbl in [("load_s", "load"), ("prefill_s", "prefill"), ("decode_s", "decode")]:
    print(f"  {lbl} per prompt: {pf[col].min():.2f}-{pf[col].max():.2f} s "
          f"(fan only: {pf[pf['fan']][col].min():.2f}-{pf[pf['fan']][col].max():.2f} s)")

# ---------------------------------------------------------------------------
# Figure 5 — E1 FoM vs bits per weight (load collection, exclude collapsed
# DeepSeek runs)
# ---------------------------------------------------------------------------

print("Loading E1 ...")
coll1_raw = load_collection(DATA / "E1")


def is_invalid_e1(run) -> bool:
    try:
        mi = run.summary.model_info or {}
        quant = (mi.get("quantization") or "").upper() or run.model_short.upper()
        return "deepseek" in run.model_short.lower() and quant in {"Q4_0", "Q8_0"}
    except Exception:
        return False


coll1 = RunCollection([r for r in coll1_raw.runs if not is_invalid_e1(r)])
ex1 = coll1.summary_df()
pm1 = coll1.prompt_metrics_df()

if "quantization" not in ex1.columns:
    ex1["quantization"] = [(r.summary.model_info or {}).get("quantization")
                           for r in coll1.runs]
if "bits_per_weight" not in ex1.columns:
    from monitorviz.transforms.aggregations import _GGUF_BPW

    ex1["bits_per_weight"] = [
        (r.summary.model_info or {}).get("bits_per_weight")
        or _GGUF_BPW.get(((r.summary.model_info or {}).get("quantization") or "").upper())
        for r in coll1.runs
    ]

fom1 = compute_fom_full(ex1)
if not pm1.empty:
    fom1, _ = compute_usability(fom1, pm1)
else:
    fom1["usable"] = False
fom1["model_clean"] = fom1["model_label"].map(clean_label)

fd = fom1.dropna(subset=["quantization", "bits_per_weight", "fom_full", "model_clean"])
med_bpw = fd.groupby("quantization")["bits_per_weight"].median().sort_values(
    ascending=False)
quant_order = med_bpw.index.tolist()  # highest bits per weight on the left
q2pos = {q: i for i, q in enumerate(quant_order)}
models1 = sorted(fd["model_clean"].unique())
mk_map1 = {m: MARKER_POOL[i % len(MARKER_POOL)] for i, m in enumerate(models1)}

fig, ax = plt.subplots(figsize=(11, 5))
for m in models1:
    sub = fd[fd["model_clean"] == m].copy()
    sub["_xpos"] = sub["quantization"].map(q2pos)
    sub = sub.sort_values("_xpos")
    ax.plot(sub["_xpos"], sub["fom_full"], marker=mk_map1[m], ms=7, lw=2, label=m)
ax.axhline(1.0, color="gray", ls="--", lw=1.2, alpha=0.7, label="Reference (FoM = 1)")
us = fd[fd["usable"]].copy()
if not us.empty:
    us["_xpos"] = us["quantization"].map(q2pos)
    ax.scatter(us["_xpos"], us["fom_full"], s=220, marker="*", color="gold",
               zorder=5, edgecolors="darkorange", lw=1,
               label="Usable ($\\geq T_{hum}$)")
ax.set_xticks(list(range(len(quant_order))))
ax.set_xticklabels([f"{q}\n({med_bpw[q]:.1f} bpw)" for q in quant_order], fontsize=9)
ax.set_xlabel("Quantization (median bits per weight)", fontsize=11)
ax.set_ylabel("$FoM_{full}$ (normalized to reference)", fontsize=11)
ax.grid(True, alpha=0.3)
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9, framealpha=0.9)
fig.tight_layout()
save(fig, "e1_fom_bpw.png")

# ---------------------------------------------------------------------------
# Figure 6 — E1 WikiText-2 perplexity per model and quantization
# (drops DeepSeek non-K-quant bars: Q4_0 / Q8_0 collapse)
# ---------------------------------------------------------------------------

print("Loading perplexity runs ...")
PPL_DIR = DATA / "Perplejidad"
QUANT_RE = re.compile(r"-(BF16|Q\d+[_K]*[_0M]*)(?:-GGUF)?\.gguf$", re.IGNORECASE)
QUANT_ORDER_PPL = ["Q3_K_M", "Q4_0", "Q4_K_M", "Q5_K_M", "Q8_0", "BF16"]
MODEL_SHORT = {
    "DeepSeek-R1-Distill-Qwen-1.5B": "DeepSeek-R1-1.5B",
    "gemma-4.5B-3n-E2B-it": "Gemma-3n",
    "granite-4.0-h-micro": "Granite-4.0-H",
    "Llama-3.2-1B-Instruct": "Llama-3.2-1B",
    "Llama-3.2-3B-Instruct": "Llama-3.2-3B",
    "Ministral-3-3B-Instruct-2512": "Ministral-3B",
}

rows = []
for run_dir in sorted(PPL_DIR.iterdir()):
    rjson = run_dir / "resumen.json"
    if not rjson.is_file():
        continue
    r = json.loads(rjson.read_text())
    fname = Path(r["model"]["path"]).name
    m = QUANT_RE.search(fname)
    if m:
        quant = m.group(1).upper()
        base = fname[: m.start()]
    else:
        quant = r["model"].get("quantization", "?")
        base = fname.replace(".gguf", "")
    rows.append(dict(run_id=run_dir.name, model_base=base, quant=quant,
                     context=r["annotations"]["context"],
                     ppl=r["result"]["perplexity"],
                     ppl_stderr=r["result"]["ppl_stderr"]))

dfp = pd.DataFrame(rows)
dfp["quant"] = pd.Categorical(dfp["quant"], categories=QUANT_ORDER_PPL, ordered=True)
dfp["model_short"] = dfp["model_base"].map(MODEL_SHORT).fillna(dfp["model_base"])
dfp = dfp.sort_values("run_id")
dfp = dfp[~dfp.duplicated(subset=["model_base", "quant", "context", "ppl"], keep="first")]
dfp = dfp[dfp["context"] == 512].copy()

# Drop DeepSeek non-K-quant entries (model collapse in E1)
mask_drop = dfp["model_short"].str.contains("DeepSeek") & dfp["quant"].isin(["Q4_0", "Q8_0"])
print(f"Dropping {mask_drop.sum()} DeepSeek non-K-quant perplexity rows")
dfp = dfp[~mask_drop]

quants_present = [q for q in QUANT_ORDER_PPL if q in dfp["quant"].values]
palette = dict(zip(quants_present, sns.color_palette("tab10", len(quants_present))))
models_p = sorted(dfp["model_short"].unique())
x_pos = np.arange(len(models_p))
width = 0.8 / max(len(quants_present), 1)

fig, ax = plt.subplots(figsize=(9, 5))
for i, q in enumerate(quants_present):
    qdata = dfp[dfp["quant"] == q]
    vals, errs = [], []
    for mname in models_p:
        v = qdata[qdata["model_short"] == mname]["ppl"].values
        e = qdata[qdata["model_short"] == mname]["ppl_stderr"].values
        vals.append(v[0] if len(v) else np.nan)
        errs.append(e[0] if len(e) else np.nan)
    offset = (i - len(quants_present) / 2 + 0.5) * width
    ax.bar(x_pos + offset, vals, width=width * 0.9, color=palette[q], label=q, zorder=3)
    ax.errorbar(x_pos + offset, vals, yerr=errs, fmt="none", color="black",
                capsize=3, linewidth=1, zorder=4)
ax.set_xticks(x_pos)
ax.set_xticklabels(models_p, rotation=25, ha="right", fontsize=9)
ax.set_ylabel("Perplexity (PPL)")
ax.set_xlabel("")
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
handles = [mpatches.Patch(color=palette[q], label=q) for q in quants_present]
ax.legend(handles=handles, title="Quantization", fontsize=9, title_fontsize=9,
          loc="upper right")
fig.tight_layout()
save(fig, "e1_perplexity.png")

# ---------------------------------------------------------------------------
# Figure 7 — E2 throughput vs context size
# ---------------------------------------------------------------------------

print("Loading E2 ...")
coll2 = load_collection(DATA / "E2")
sum2 = coll2.summary_df()
pm2 = coll2.prompt_metrics_df()
ex2 = sum2[sum2["accelerator"] == False].copy()  # noqa: E712
if "TYPE_2" in ex2["test_type"].values:
    ex2 = ex2[ex2["test_type"] == "TYPE_2"].copy()
elif "TYPE_1" in ex2["test_type"].values:
    ex2 = ex2[ex2["test_type"] == "TYPE_1"].copy()
ex2["model_clean"] = ex2["model_label"].map(clean_label)

ex_t = ex2.dropna(subset=["context_size", "tokens_per_s_mean"]).sort_values("context_size")
fom2 = compute_fom_full(ex2)
thum2 = {}
if not pm2.empty:
    fom2, _ = compute_usability(fom2, pm2)
    fom2["model_clean"] = fom2["model_label"].map(clean_label)
    thum2 = fom2.groupby("model_clean")["T_hum"].first().to_dict()

fig, ax = plt.subplots(figsize=(9, 5))
for i, m in enumerate(sorted(ex_t["model_clean"].unique())):
    sub = ex_t[ex_t["model_clean"] == m]
    ax.plot(sub["context_size"], sub["tokens_per_s_mean"],
            marker=MARKER_POOL[i % len(MARKER_POOL)], lw=2, ms=8, label=m)
    if m in thum2 and pd.notna(thum2[m]):
        ax.axhline(thum2[m], ls=":", lw=1.2, alpha=0.6,
                   color=ax.lines[-1].get_color())
ax.set_xlabel("Context size (tokens)", fontsize=11)
ax.set_ylabel("Throughput (tok/s)", fontsize=11)
ax.grid(True, alpha=0.3)
handles, labels = ax.get_legend_handles_labels()
handles.append(Line2D([0], [0], color="gray", ls=":", lw=1.2))
labels.append("$T_{hum}$ (per model)")
ax.legend(handles, labels, bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
fig.tight_layout()
save(fig, "e2_throughput.png")

print("All figures generated.")
