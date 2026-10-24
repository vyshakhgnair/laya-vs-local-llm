"""Run one system on one task, saving every decision (resumable).

  python src/run_eval.py --task routing --system laya
  python src/run_eval.py --task docs --system llm:qwen3.5:4b --limit 300
"""
import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import load_task, RESULTS


def make_system(spec):
    if spec == "laya":
        from laya_system import LayaSystem
        return LayaSystem()
    if spec == "laya-names":
        from laya_system import LayaSystem
        return LayaSystem(criteria="names")
    if spec == "laya-typed":
        from laya_system import LayaSystem
        return LayaSystem(checkpoint="typed")
    if spec == "laya-typed-names":
        from laya_system import LayaSystem
        return LayaSystem(checkpoint="typed", criteria="names")
    if spec.startswith("llm:"):
        from llm_system import LlmSystem
        return LlmSystem(spec[4:])
    raise ValueError(f"unknown system {spec}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["routing", "sweep", "docs"])
    ap.add_argument("--system", required=True)
    ap.add_argument("--limit", type=int, default=None, help="stratified subset (same subset for every system)")
    ap.add_argument("--tag", default="", help="suffix for the results file (e.g. pilot)")
    args = ap.parse_args()

    items = load_task(args.task, args.limit)
    system = make_system(args.system)
    safe = system.name.replace(":", "_").replace("/", "_")
    out = RESULTS / f"{args.task}__{safe}{('__' + args.tag) if args.tag else ''}.jsonl"
    done = {json.loads(l)["id"] for l in out.read_text(encoding="utf-8").splitlines() if l.strip()} if out.exists() else set()
    todo = [it for it in items if it["id"] not in done]
    print(f"{args.task} / {system.name}: {len(items)} items, {len(done)} already done, {len(todo)} to run", flush=True)

    start, correct, n = time.time(), 0, 0
    with out.open("a", encoding="utf-8") as f:
        for it in todo:
            try:
                res = system.predict(args.task, it)
            except Exception as e:
                res = {"pred": "ERROR", "latency_ms": None, "confidence": None, "error": str(e)[:200]}
            rec = {"id": it["id"], "task": args.task, "system": system.name, "answer": it["answer"],
                   "correct": res["pred"] == it["answer"], "n_tools": it["meta"]["n_tools"],
                   "source": it["meta"]["source"], **res}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            correct += rec["correct"]
            if n % 25 == 0 or n == len(todo):
                el = time.time() - start
                print(f"  {n}/{len(todo)}  running acc {correct / n:.3f}  elapsed {el / 60:.1f} min", flush=True)
    print(f"done -> {out.name}", flush=True)


if __name__ == "__main__":
    main()
