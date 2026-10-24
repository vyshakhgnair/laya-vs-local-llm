"""Build the tool-routing benchmarks from BFCL v3 (real queries, real tool schemas, ground truth).

Decision being tested: given a user request and N candidate tools (+ a "none" option),
which tool should be called? Only tool *selection* is scored, not argument filling.

Outputs
  data/routing.jsonl        core set: multiple (2-4 tools), live_multiple (2-37), irrelevance ("none")
  data/routing_sweep.jsonl  same 100 queries padded with distractor tools to 5/10/20/30 candidates
"""
import json
import pathlib
import random
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "data" / "bfcl"
SEED = 42
DESC_CHARS = 200


def jl(name):
    return [json.loads(l) for l in (B / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def query_of(row):
    turn = row["question"][0]
    return " ".join(m["content"] for m in turn if m["role"] == "user").strip()


def tools_of(row):
    return [{"name": f["name"], "description": (f.get("description") or "")[:DESC_CHARS].strip()}
            for f in row["function"]]


def truth_of(ans_row):
    calls = ans_row["ground_truth"]
    return next(iter(calls[0].keys())) if len(calls) == 1 else None


def load_relevant(stem):
    rows = jl(f"{stem}.json")
    ans = {a["id"]: truth_of(a) for a in jl(f"possible_answer__{stem}.json")}
    items, dropped = [], 0
    for r in rows:
        t = tools_of(r)
        gt = ans.get(r["id"])
        if gt is None or gt not in {x["name"] for x in t}:
            dropped += 1
            continue
        items.append({"id": r["id"], "source": stem.replace("BFCL_v3_", ""), "query": query_of(r),
                      "tools": t, "answer": gt})
    print(f"{stem}: kept {len(items)}, dropped {dropped}")
    return items


def load_irrelevant(stem, n, rng):
    rows = [r for r in jl(f"{stem}.json") if len(r["function"]) >= 1 and query_of(r)]
    rng.shuffle(rows)
    return [{"id": r["id"], "source": stem.replace("BFCL_v3_", ""), "query": query_of(r),
             "tools": tools_of(r), "answer": "none"} for r in rows[:n]]


def main():
    rng = random.Random(SEED)

    multiple = load_relevant("BFCL_v3_multiple")
    live = load_relevant("BFCL_v3_live_multiple")
    big = [x for x in live if len(x["tools"]) >= 7]
    small = [x for x in live if len(x["tools"]) < 7]
    rng.shuffle(small)
    live_sel = big + small[:150]

    none_items = load_irrelevant("BFCL_v3_irrelevance", 60, rng) + \
                 load_irrelevant("BFCL_v3_live_irrelevance", 60, rng)

    core = multiple + live_sel + none_items
    rng.shuffle(core)
    for i, x in enumerate(core):
        x["n_tools"] = len(x["tools"])
    out = ROOT / "data" / "routing.jsonl"
    out.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in core) + "\n", encoding="utf-8")

    print(f"\ncore routing set: {len(core)} items -> {out.name}")
    print("  by source:", dict(Counter(x["source"] for x in core)))
    print("  'none' share: %.0f%%" % (100 * sum(x['answer'] == 'none' for x in core) / len(core)))
    print("  tool-count buckets:", dict(sorted(Counter(min(x['n_tools'], 11) for x in core).items())))

    # Sweep: identical queries, growing candidate lists padded with real tools from other items
    pool = {}
    for x in multiple:
        for t in x["tools"]:
            pool[t["name"]] = t
    base = rng.sample(multiple, 100)
    sweep = []
    for size in (5, 10, 20, 30):
        for x in base:
            have = {t["name"] for t in x["tools"]}
            distractors = [t for n, t in pool.items() if n not in have]
            rng.shuffle(distractors)
            tools = x["tools"] + distractors[:max(0, size - len(x["tools"]))]
            rng.shuffle(tools)
            sweep.append({"id": f"{x['id']}@{size}", "base_id": x["id"], "source": "sweep", "query": x["query"],
                          "tools": tools, "answer": x["answer"], "n_tools": len(tools)})
    out2 = ROOT / "data" / "routing_sweep.jsonl"
    out2.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in sweep) + "\n", encoding="utf-8")
    print(f"\nsweep set: {len(sweep)} items (100 queries x sizes 5/10/20/30) -> {out2.name}")

    ex = core[0]
    print("\nexample:", json.dumps({k: ex[k] for k in ('source', 'query', 'answer', 'n_tools')}, ensure_ascii=False))


if __name__ == "__main__":
    main()
