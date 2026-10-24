"""LinkedIn-ready figures: each system alone vs the combined (Laya -> LLM) system. Numbers come from results/cascade_cv.json."""
import json
import pathlib
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = RES / "charts"
OUT.mkdir(exist_ok=True)
C_LAYA, C_LLM, C_COMBO = "#2563eb", "#6b7280", "#16a34a"
INK = "#111827"


def panel(task_key, title, subtitle, footer, fname, combo_label):
    d = json.loads((RES / "cascade_cv.json").read_text(encoding="utf-8"))[task_key]
    f = d["fixed"]
    acc = [100 * d["laya_acc"], 100 * d["llm_acc"], 100 * f["acc"]]
    dph = [3.6e6 / d["laya_lat"], 3.6e6 / d["llm_lat"], 3.6e6 / f["lat"]]
    llm_share = [0, 100, 100 * f["esc"]]
    names = [f"Laya alone\nLLM calls: {llm_share[0]:.0f}%", f"LLM alone\nLLM calls: {llm_share[1]:.0f}%",
             f"{combo_label}\nLLM calls: {llm_share[2]:.0f}%"]
    cols = [C_LAYA, C_LLM, C_COMBO]

    fig, axes = plt.subplots(1, 2, figsize=(8, 4.5), dpi=200)
    fig.patch.set_facecolor("white")
    for ax in axes:
        ax.set_facecolor("white")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=9, colors=INK)

    ax = axes[0]
    bars = ax.bar(range(3), acc, color=cols, width=0.62)
    ax.set_ylim(0, 105)
    ax.set_xticks(range(3)); ax.set_xticklabels(names)
    ax.set_title("Accuracy (%)", fontsize=11, color=INK, loc="left", fontweight="bold")
    for b, v in zip(bars, acc):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}", ha="center", fontsize=11, fontweight="bold", color=INK)

    ax = axes[1]
    bars = ax.bar(range(3), dph, color=cols, width=0.62)
    ax.set_ylim(0, max(dph) * 1.22)
    ax.set_xticks(range(3)); ax.set_xticklabels(names)
    ax.set_title("Decisions per hour (this laptop)", fontsize=11, color=INK, loc="left", fontweight="bold")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    for b, v in zip(bars, dph):
        ax.text(b.get_x() + b.get_width() / 2, v + max(dph) * 0.02, f"{v:,.0f}", ha="center", fontsize=11,
                fontweight="bold", color=INK)
    speed = dph[2] / dph[1]
    ax.text(2, dph[2] + max(dph) * 0.12, f"{speed:.1f}x the LLM", ha="center", fontsize=11, fontweight="bold",
            color=C_COMBO)

    fig.suptitle(title, fontsize=14, fontweight="bold", color=INK, x=0.04, ha="left", y=0.985)
    fig.text(0.04, 0.915, subtitle, fontsize=9.5, color="#374151", ha="left")
    fig.text(0.04, 0.012, textwrap.fill(footer, 135), fontsize=6.8, color="#6b7280", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.085, 1, 0.9))
    fig.savefig(OUT / fname)
    plt.close(fig)
    print("saved", fname, "| acc", [round(a, 1) for a in acc], "| decisions/h", [round(v) for v in dph],
          "| speed-up", round(speed, 2))


panel("routing|typed checkpoint + calibrated confidence",
      "Tool routing: each model alone vs combined",
      "Laya answers; the LLM is called only when Laya is under 70% sure.",
      "300 BFCL v3 routing decisions | Laya typed-decisions checkpoint, calibrated confidence | qwen3.5:4b via Ollama | "
      "single requests, GTX 1650 laptop | escalation threshold 0.7 was a round number from a fixed grid, picked after "
      "seeing results on the same items (out-of-sample estimate in the write-up)",
      "linkedin_routing.png", "Combined")
panel("docs|typed checkpoint + calibrated confidence",
      "Document typing: the combination barely pays off",
      "Same rule, but Laya is unsure on most pages, so the LLM still handles most of them.",
      "300 RVL-CDIP-N pages, 12 classes | Laya typed-decisions checkpoint, calibrated confidence | qwen3.5:4b via Ollama | "
      "single requests, GTX 1650 laptop",
      "linkedin_docs.png", "Combined")
