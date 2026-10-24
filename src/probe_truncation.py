"""What exactly does Laya truncate on the document task, and does shorter criteria text avoid it?"""
import pathlib
import statistics
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import laya
from common import load_task

agent = laya.load("convaiinnovations/laya")
items = load_task("docs", limit=40)

for style in ("full", "names"):
    rows = []
    for it in items:
        crit = dict(it["labels"]) if style == "full" else {k: k.replace("_", " ") for k in it["labels"]}
        res = agent.predict({"text": it["input"]},
                            {"q": {"type": "choice", "instructions": "Which type of document is this page?",
                                   "criteria": crit}})
        u = res["usage"]
        rows.append((u, res["answers"]["q"]["choice"] == it["answer"]))
    tr = [u for u, _ in rows if u.get("truncated")]
    print(f"\n=== criteria={style}  (n={len(rows)}) ===")
    print(f"truncated: {len(tr)}/{len(rows)} | acc {sum(ok for _, ok in rows) / len(rows):.2f}")
    print(f"input_tokens mean {statistics.mean(u['input_tokens'] for u, _ in rows):.0f} | "
          f"state_tokens mean {statistics.mean(u['state_tokens'] for u, _ in rows):.0f} max {max(u['state_tokens'] for u, _ in rows)} | "
          f"state_tokens_dropped mean {statistics.mean(u['state_tokens_dropped'] for u, _ in rows):.0f}")
    if tr:
        print("example truncated usage:", tr[0])
