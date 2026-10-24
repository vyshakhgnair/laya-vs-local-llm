"""Out-of-sample estimate for the Laya -> LLM combined system.

The earlier cascade tables pick the escalation threshold on the same items they score. Here the threshold is chosen on a
random half of the items by a fixed rule, then scored on the OTHER half; repeated for many random splits.

Rule: the lowest threshold (least escalation) whose accuracy on the selection half is within TOL points of the LLM-only
accuracy on that half. Also reports one pre-specified threshold (escalate when Laya is < 0.7 sure) with a McNemar test.
"""
import json
import math
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "results"
GRID = [round(0.30 + 0.05 * i, 2) for i in range(0, 14)] + [0.99]   # 0.30 ... 0.95, 0.99
TOL = 0.02
REPEATS = 500


def load(task, system_file):
    p = RES / f"{task}__{system_file}.jsonl"
    return {r["id"]: r for r in map(json.loads, p.read_text(encoding="utf-8").splitlines()) if r}


def cascade(ids, laya, llm, tau):
    n = len(ids)
    esc = [(laya[i]["confidence"] is None or laya[i]["confidence"] < tau) for i in ids]
    acc = sum((llm[i]["correct"] if e else laya[i]["correct"]) for i, e in zip(ids, esc)) / n
    lat = statistics.mean(laya[i]["latency_ms"] + (llm[i]["latency_ms"] if e else 0) for i, e in zip(ids, esc))
    return acc, sum(esc) / n, lat


def mcnemar_p(a, b):
    x = sum(1 for p, q in zip(a, b) if p and not q)
    y = sum(1 for p, q in zip(a, b) if q and not p)
    n = x + y
    if n == 0:
        return 1.0, x, y
    k = min(x, y)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n), x, y


def pct(v):
    return f"{100 * v:.1f}%"


def run(task, laya_file, llm_file, label):
    laya, llm = load(task, laya_file), load(task, llm_file)
    ids = sorted(set(laya) & set(llm))
    n = len(ids)
    llm_acc = sum(llm[i]["correct"] for i in ids) / n
    laya_acc = sum(laya[i]["correct"] for i in ids) / n
    llm_lat = statistics.mean(llm[i]["latency_ms"] for i in ids)
    laya_lat = statistics.mean(laya[i]["latency_ms"] for i in ids)
    print(f"\n=== {task}: {label}  (n={n}) ===")
    print(f"Laya alone  : {pct(laya_acc)}  mean {laya_lat:,.0f} ms  ({3.6e6 / laya_lat:,.0f} decisions/h)")
    print(f"LLM alone   : {pct(llm_acc)}  mean {llm_lat:,.0f} ms  ({3.6e6 / llm_lat:,.0f} decisions/h)")

    # pre-specified threshold
    tau = 0.7
    acc, esc, lat = cascade(ids, laya, llm, tau)
    casc_correct = [(llm[i]["correct"] if (laya[i]["confidence"] is None or laya[i]["confidence"] < tau) else laya[i]["correct"]) for i in ids]
    p_llm, x1, y1 = mcnemar_p(casc_correct, [llm[i]["correct"] for i in ids])
    p_laya, x2, y2 = mcnemar_p(casc_correct, [laya[i]["correct"] for i in ids])
    print(f"Combined, pre-specified threshold < {tau}: {pct(acc)}, escalates {pct(esc)}, mean {lat:,.0f} ms "
          f"({3.6e6 / lat:,.0f}/h, {llm_lat / lat:.1f}x LLM)")
    print(f"   vs LLM alone  : {x1} items only combined right, {y1} only LLM right (McNemar p = {p_llm:.3f})")
    print(f"   vs Laya alone : {x2} items only combined right, {y2} only Laya right (McNemar p = {p_laya:.4f})")

    # out-of-sample threshold selection
    rng = random.Random(11)
    out = {"acc": [], "esc": [], "lat": [], "llm_acc": [], "llm_lat": [], "tau": []}
    for _ in range(REPEATS):
        shuffled = ids[:]
        rng.shuffle(shuffled)
        sel, held = shuffled[: n // 2], shuffled[n // 2:]
        sel_llm = sum(llm[i]["correct"] for i in sel) / len(sel)
        chosen = GRID[-1]
        for t in GRID:
            if cascade(sel, laya, llm, t)[0] >= sel_llm - TOL:
                chosen = t
                break
        a, e, l = cascade(held, laya, llm, chosen)
        out["acc"].append(a); out["esc"].append(e); out["lat"].append(l); out["tau"].append(chosen)
        out["llm_acc"].append(sum(llm[i]["correct"] for i in held) / len(held))
        out["llm_lat"].append(statistics.mean(llm[i]["latency_ms"] for i in held))
    diff = sorted(a - b for a, b in zip(out["acc"], out["llm_acc"]))
    speed = sorted(b / a for a, b in zip(out["lat"], out["llm_lat"]))
    m = statistics.mean
    print(f"Out-of-sample over {REPEATS} random 50/50 splits (rule: within {int(TOL * 100)} pts of LLM on the selection half):")
    print(f"   combined accuracy {pct(m(out['acc']))} vs LLM {pct(m(out['llm_acc']))}; "
          f"difference {100 * m(diff):+.1f} pts (5th-95th pct {100 * diff[int(.05 * REPEATS)]:+.1f} to {100 * diff[int(.95 * REPEATS)]:+.1f})")
    print(f"   escalates {pct(m(out['esc']))} of decisions (LLM calls avoided: {pct(1 - m(out['esc']))}); mean latency "
          f"{m(out['lat']):,.0f} ms -> {m(speed):.1f}x faster than LLM (5th-95th pct {speed[int(.05 * REPEATS)]:.1f}x to {speed[int(.95 * REPEATS)]:.1f}x)")
    print(f"   typical chosen threshold: median {statistics.median(out['tau'])}")
    return {"n": n, "laya_acc": laya_acc, "llm_acc": llm_acc, "laya_lat": laya_lat, "llm_lat": llm_lat,
            "fixed": {"tau": tau, "acc": acc, "esc": esc, "lat": lat, "p_vs_llm": p_llm, "p_vs_laya": p_laya},
            "cv": {"acc": m(out["acc"]), "llm_acc": m(out["llm_acc"]), "esc": m(out["esc"]), "lat": m(out["lat"]),
                   "speedup": m(speed), "speed_lo": speed[int(.05 * REPEATS)], "speed_hi": speed[int(.95 * REPEATS)],
                   "diff": m(diff), "diff_lo": diff[int(.05 * REPEATS)], "diff_hi": diff[int(.95 * REPEATS)]}}


if __name__ == "__main__":
    results = {}
    for task in ("routing", "docs"):
        for laya_file, label in (("laya[typed,calib]", "typed checkpoint + calibrated confidence"),
                                 ("laya[calib]", "base checkpoint + calibrated confidence")):
            results[f"{task}|{label}"] = run(task, laya_file, "llm_qwen3.5_4b", label)
    (RES / "cascade_cv.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\nsaved results/cascade_cv.json")
