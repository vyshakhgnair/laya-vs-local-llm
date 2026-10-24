"""Level 2: refit Laya's confidence temperature on held-out labelled items, then score the matched test subset.

No weights change, so accuracy is identical by construction; only the confidence (and therefore the
Laya->LLM cascade) can improve. Calibration items are drawn from the pool DISJOINT from the test subset.

  python src/calibrate_laya.py --checkpoint base --tasks docs routing
"""
import argparse
import json
import pathlib
import sys
import time
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load_task, stratified_sample, RESULTS
from laya_system import build_query, load_agent, system_name

TEST_LIMIT = {"docs": 300, "routing": 300}
N_CALIB = {"docs": 300, "routing": 248}


def one_hot(labels, answer):
    keys = list(labels)
    v = [0.0] * len(keys)
    v[keys.index(answer)] = 1.0
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", choices=["base", "typed"], default="base")
    ap.add_argument("--tasks", nargs="+", default=["docs", "routing"])
    args = ap.parse_args()

    from laya.calibrate import records_from_labeled
    agent = load_agent(args.checkpoint)
    name = system_name(checkpoint=args.checkpoint, extra="calib")

    for task in args.tasks:
        test = load_task(task, limit=TEST_LIMIT[task])
        test_ids = {it["id"] for it in test}
        pool = [it for it in load_task(task) if it["id"] not in test_ids]
        calib = stratified_sample(pool, N_CALIB[task], seed=7) if len(pool) > N_CALIB[task] else pool
        assert not ({it["id"] for it in calib} & test_ids), "calibration/test overlap"
        print(f"[{name}] {task}: {len(calib)} calibration items (disjoint pool of {len(pool)}), "
              f"{len(test)} test items", flush=True)

        t0 = time.time()
        pairs = []
        for it in calib:
            state, questions = build_query(task, it)
            pairs.append((state, questions, {"q": one_hot(it["labels"], it["answer"])}))
        records = records_from_labeled(agent, pairs)
        fit = agent.fit_temperatures(records)
        info = {"task": task, "checkpoint": args.checkpoint, "n_calibration": len(records),
                "temperature": fit.get("temperature"), "temperature_by_options": fit.get("temperature_by_options"),
                "temperature_clamped": fit.get("temperature_clamped"), "n_by_bucket": fit.get("n_by_bucket")}
        print(f"  fitted in {(time.time() - t0) / 60:.1f} min: {json.dumps(info, default=str)}", flush=True)
        (RESULTS / f"calibration_{task}_{args.checkpoint}.json").write_text(
            json.dumps(info, indent=1, default=str), encoding="utf-8")

        out = RESULTS / f"{task}__{name}.jsonl"
        out.write_text("", encoding="utf-8")
        correct = 0
        with out.open("a", encoding="utf-8") as f:
            for i, it in enumerate(test, 1):
                state, questions = build_query(task, it)
                t1 = time.perf_counter()
                res = agent.predict(state, questions)
                ms = (time.perf_counter() - t1) * 1000
                a = res["answers"]["q"]
                u = res.get("usage", {})
                rec = {"id": it["id"], "task": task, "system": name, "answer": it["answer"],
                       "correct": a["choice"] == it["answer"], "n_tools": it["meta"]["n_tools"],
                       "source": it["meta"]["source"], "pred": a["choice"], "latency_ms": round(ms, 1),
                       "confidence": a.get("answer_confidence"), "prompt_tokens": u.get("input_tokens"),
                       "output_tokens": 0, "truncated": u.get("truncated")}
                correct += rec["correct"]
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if i % 50 == 0 or i == len(test):
                    print(f"  test {i}/{len(test)} acc {correct / i:.3f}", flush=True)
        print(f"  done -> {out.name}", flush=True)


if __name__ == "__main__":
    main()
