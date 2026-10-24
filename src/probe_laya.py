"""One-off probe: what does Laya's API return, how fast is it, and where does it run?"""
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import torch
import laya

from common import load_task

print("laya", getattr(laya, "__version__", "?"), "| torch", torch.__version__, "| cuda:", torch.cuda.is_available())

t0 = time.perf_counter()
agent = laya.load("convaiinnovations/laya")
print(f"load time: {time.perf_counter() - t0:.1f}s | type: {type(agent).__name__}")
print("public attrs:", [a for a in dir(agent) if not a.startswith("_")][:30])
try:
    n_params = sum(p.numel() for p in agent.model.parameters())
    print(f"parameters: {n_params / 1e6:.1f}M")
except Exception as e:
    print("param count unavailable:", e)

for task in ("routing", "docs"):
    item = load_task(task, limit=3)[0]
    state = {"request": item["input"]} if task != "docs" else {"text": item["input"]}
    questions = {"choice_q": {"type": "choice", "instructions": "Pick the best option.",
                              "criteria": dict(item["labels"])}}
    for k in range(3):
        t = time.perf_counter()
        res = agent.predict(state, questions)
        ms = (time.perf_counter() - t) * 1000
        print(f"\n[{task}] call {k + 1}: {ms:.0f} ms | gold={item['answer']} | n_labels={len(item['labels'])}")
    print(json.dumps(res, indent=1, default=str)[:1800])
