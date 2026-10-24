"""Aggregate results/*.jsonl into tables (results/summary.md) and charts (results/charts/*.png).

Fairness rule: the headline comparison uses only items answered by EVERY system on that task.
"""
import json
import math
import pathlib
import statistics
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
CH = RES / "charts"
CH.mkdir(exist_ok=True)


def load(full=False):
    """full=False: matched-subset runs. full=True: the *__full.jsonl runs on the complete benchmarks."""
    data = defaultdict(lambda: defaultdict(dict))  # task -> system -> id -> rec
    for p in sorted(RES.glob("*.jsonl")):
        if "__pilot" in p.name or (("__full" in p.name) != full):
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                data[r["task"]][r["system"]][r["id"]] = r
    return data


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def mcnemar_p(a_correct, b_correct):
    """Exact two-sided McNemar test on paired per-item correctness."""
    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)
    c = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)
    n = b + c
    if n == 0:
        return 1.0, b, c
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n * 2
    return min(1.0, p), b, c


def macro_f1(recs):
    labels = sorted({r["answer"] for r in recs})
    f1s = []
    for lab in labels:
        tp = sum(1 for r in recs if r["answer"] == lab and r["pred"] == lab)
        fp = sum(1 for r in recs if r["answer"] != lab and r["pred"] == lab)
        fn = sum(1 for r in recs if r["answer"] == lab and r["pred"] != lab)
        pr = tp / (tp + fp) if tp + fp else 0
        rc = tp / (tp + fn) if tp + fn else 0
        f1s.append(2 * pr * rc / (pr + rc) if pr + rc else 0)
    return sum(f1s) / len(f1s)


def pct(x):
    return f"{100 * x:.1f}%"


def latency_stats(recs):
    L = sorted(r["latency_ms"] for r in recs if r.get("latency_ms"))
    if not L:
        return None
    return {"median": statistics.median(L), "p95": L[min(len(L) - 1, int(0.95 * len(L)))], "mean": statistics.mean(L)}


def ece(recs, bins=10):
    pts = [(r["confidence"], r["correct"]) for r in recs if r.get("confidence") is not None]
    if not pts:
        return None
    tot, err = len(pts), 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(c, ok) for c, ok in pts if (lo <= c < hi) or (b == bins - 1 and c == 1.0)]
        if sel:
            err += len(sel) / tot * abs(sum(ok for _, ok in sel) / len(sel) - sum(c for c, _ in sel) / len(sel))
    return err


def fmt_ms(x):
    return f"{x:,.0f} ms" if x < 10000 else f"{x / 1000:,.1f} s"


def main():
    data = load()
    out = ["# Results summary\n"]
    for task in ("routing", "sweep", "docs"):
        systems = data.get(task, {})
        if not systems:
            continue
        common = set.intersection(*[set(v) for v in systems.values()])
        out.append(f"\n## {task}  (items answered by every system: {len(common)})\n")
        out.append("| system | n | accuracy | 95% CI | " + ("macro-F1 | " if task == "docs" else "") +
                   "median latency | p95 latency | decisions/hour | ECE |")
        out.append("|---|---|---|---|" + ("---|" if task == "docs" else "") + "---|---|---|---|")
        order = sorted(systems)
        for s in order:
            recs = [systems[s][i] for i in sorted(common)]
            k = sum(r["correct"] for r in recs)
            lo, hi = wilson(k, len(recs))
            ls = latency_stats(recs)
            e = ece(recs)
            row = f"| {s} | {len(recs)} | {pct(k / len(recs))} | {pct(lo)}-{pct(hi)} | "
            if task == "docs":
                row += f"{macro_f1(recs):.3f} | "
            row += (f"{fmt_ms(ls['median'])} | {fmt_ms(ls['p95'])} | {3.6e6 / ls['mean']:,.0f} | "
                    if ls else "- | - | - | ")
            row += (f"{e:.3f} |" if e is not None else "n/a |")
            out.append(row)

        if len(order) >= 2:
            ids = sorted(common)
            for i in range(len(order)):
                for j in range(i + 1, len(order)):
                    a = [systems[order[i]][x]["correct"] for x in ids]
                    b = [systems[order[j]][x]["correct"] for x in ids]
                    p, only_a, only_b = mcnemar_p(a, b)
                    out.append(f"\n- {order[i]} vs {order[j]}: {only_a} items only the first got right, "
                               f"{only_b} only the second (McNemar exact p = {p:.4f})")

        if task == "routing":
            out.append("\n### Routing accuracy by slice (common items)\n")
            out.append("| system | " + " | ".join(["2-4 tools (multiple)", "real queries, 2-10+ tools", "'none' cases (no tool applies)"]) + " |")
            out.append("|---|---|---|---|")
            for s in order:
                recs = [systems[s][i] for i in sorted(common)]
                def acc(sel):
                    sel = list(sel)
                    return f"{pct(sum(r['correct'] for r in sel) / len(sel))} (n={len(sel)})" if sel else "-"
                out.append(f"| {s} | {acc(r for r in recs if r['source'] == 'multiple')} | "
                           f"{acc(r for r in recs if r['source'] == 'live_multiple')} | "
                           f"{acc(r for r in recs if r['answer'] == 'none')} |")
            out.append("\n### 'none' handling (knowing when NOT to call a tool)\n")
            out.append("| system | none recall | none precision | false-positive tool calls on 'none' |")
            out.append("|---|---|---|---|")
            for s in order:
                recs = [systems[s][i] for i in sorted(common)]
                gold_none = [r for r in recs if r["answer"] == "none"]
                pred_none = [r for r in recs if r["pred"] == "none"]
                tp = sum(1 for r in gold_none if r["pred"] == "none")
                rec_ = tp / len(gold_none) if gold_none else 0
                prec = tp / len(pred_none) if pred_none else 0
                out.append(f"| {s} | {pct(rec_)} | {pct(prec)} | {len(gold_none) - tp} of {len(gold_none)} |")

        if task == "sweep":
            out.append("\n### Accuracy vs number of candidate tools\n")
            sizes = sorted({r["n_tools"] for s in systems.values() for r in s.values()})
            out.append("| system | " + " | ".join(f"{z} tools" for z in sizes) + " |")
            out.append("|---|" + "---|" * len(sizes))
            curve = {}
            for s in order:
                recs = [systems[s][i] for i in sorted(common)]
                cells = []
                curve[s] = []
                for z in sizes:
                    sel = [r for r in recs if r["n_tools"] == z]
                    a = sum(r["correct"] for r in sel) / len(sel) if sel else float("nan")
                    curve[s].append(a)
                    cells.append(pct(a) if sel else "-")
                out.append(f"| {s} | " + " | ".join(cells) + " |")
            try:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                plt.figure(figsize=(6.4, 4))
                for s in order:
                    plt.plot(sizes, [100 * v for v in curve[s]], marker="o", label=s)
                plt.xlabel("candidate tools offered"); plt.ylabel("routing accuracy (%)")
                plt.title("Tool-routing accuracy as the tool list grows"); plt.ylim(0, 102)
                plt.grid(alpha=.3); plt.legend(); plt.tight_layout()
                plt.savefig(CH / "sweep_accuracy.png", dpi=160); plt.close()
            except Exception as e:
                out.append(f"\n(chart skipped: {e})")

        if task == "docs":
            out.append("\n### Per-class recall (common items)\n")
            classes = sorted({r["answer"] for s in systems.values() for r in s.values()})
            out.append("| class | n | " + " | ".join(order) + " |")
            out.append("|---|---|" + "---|" * len(order))
            for c in classes:
                row = []
                n_c = 0
                for s in order:
                    sel = [systems[s][i] for i in sorted(common) if systems[s][i]["answer"] == c]
                    n_c = len(sel)
                    row.append(pct(sum(r["correct"] for r in sel) / len(sel)) if sel else "-")
                out.append(f"| {c} | {n_c} | " + " | ".join(row) + " |")

    # Latency / throughput figure across tasks
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        tasks = [t for t in ("routing", "docs") if t in data]
        if tasks:
            fig, axes = plt.subplots(1, len(tasks), figsize=(5.2 * len(tasks), 3.8))
            axes = axes if len(tasks) > 1 else [axes]
            for ax, t in zip(axes, tasks):
                names = sorted(data[t])
                med = [latency_stats(list(data[t][s].values()))["median"] for s in names]
                ax.bar(range(len(names)), med)
                ax.set_xticks(range(len(names)))
                ax.set_xticklabels([n.replace("llm:", "") for n in names], rotation=15)
                ax.set_ylim(0, max(med) * 1.12)
                ax.set_ylabel("median latency per decision (ms)"); ax.set_title(t)
                for i, m in enumerate(med):
                    ax.text(i, m, f"{m:,.0f}", ha="center", va="bottom", fontsize=8)
            plt.tight_layout(); plt.savefig(CH / "latency.png", dpi=160); plt.close()
    except Exception as e:
        out.append(f"\n(latency chart skipped: {e})")

    # ---- Cascade: Laya answers when confident, otherwise escalate to the LLM ----
    for task in ("routing", "docs"):
        systems = data.get(task, {})
        for laya_name, llm in [(a, b) for a in systems if a.startswith("laya") for b in systems if b.startswith("llm:")]:
            ids = sorted(set(systems[laya_name]) & set(systems[llm]))
            if len(ids) < 30:
                continue
            L = [systems[laya_name][i] for i in ids]
            M = [systems[llm][i] for i in ids]
            out.append(f"\n## Cascade on {task}: {laya_name} first, escalate to {llm} when its confidence < threshold  (n={len(ids)})\n")
            out.append("| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |")
            out.append("|---|---|---|---|---|---|")
            llm_lat = statistics.mean(m["latency_ms"] for m in M)
            pts = []
            for tau in (0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.01):
                esc = [(l["confidence"] is None or l["confidence"] < tau) for l in L]
                correct = [m["correct"] if e else l["correct"] for l, m, e in zip(L, M, esc)]
                lat = statistics.mean(l["latency_ms"] + (m["latency_ms"] if e else 0) for l, m, e in zip(L, M, esc))
                label = "Laya only" if tau == 0.0 else ("always LLM (+Laya)" if tau > 1 else f"< {tau}")
                acc = sum(correct) / len(correct)
                pts.append((lat, acc, label))
                out.append(f"| {label} | {pct(sum(esc) / len(esc))} | {pct(acc)} | {fmt_ms(lat)} | {3.6e6 / lat:,.0f} | {llm_lat / lat:.1f}x |")
            llm_acc = sum(m["correct"] for m in M) / len(M)
            out.append(f"\nLLM only: accuracy {pct(llm_acc)}, mean latency {fmt_ms(llm_lat)}")
            try:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                plt.figure(figsize=(6.4, 4))
                plt.plot([p[0] for p in pts[:-1]], [100 * p[1] for p in pts[:-1]], marker="o", label=f"{laya_name} -> LLM cascade")
                plt.scatter([llm_lat], [100 * llm_acc], color="red", zorder=5, label="LLM only")
                plt.xscale("log"); plt.xlabel("mean latency per decision (ms, log)"); plt.ylabel("accuracy (%)")
                plt.title(f"{task}: accuracy vs latency"); plt.grid(alpha=.3); plt.legend(); plt.tight_layout()
                safe_name = laya_name.replace("[", "_").replace("]", "").replace(",", "_")
                plt.savefig(CH / f"cascade_{task}_{safe_name}.png", dpi=160); plt.close()
            except Exception as e:
                out.append(f"(cascade chart skipped: {e})")

    full = load(full=True)
    if full:
        out.append("\n## Laya on the COMPLETE benchmarks (not subsampled)\n")
        out.append("| task | system | n | accuracy | 95% CI | median latency | decisions/hour | ECE |")
        out.append("|---|---|---|---|---|---|---|---|")
        for task in ("routing", "sweep", "docs"):
            for s, recs_by_id in sorted(full.get(task, {}).items()):
                recs = list(recs_by_id.values())
                k = sum(r["correct"] for r in recs)
                lo, hi = wilson(k, len(recs))
                ls = latency_stats(recs)
                e = ece(recs)
                out.append(f"| {task} | {s} | {len(recs)} | {pct(k / len(recs))} | {pct(lo)}-{pct(hi)} | "
                           f"{fmt_ms(ls['median']) if ls else '-'} | {3.6e6 / ls['mean']:,.0f} | "
                           f"{(f'{e:.3f}' if e is not None else 'n/a')} |")

    (RES / "summary.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
