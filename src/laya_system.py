"""Laya (open-source System One decision model): one forward pass -> typed answer + probabilities.

checkpoint='base'  -> convaiinnovations/laya (English, 512-token window; what the first study used)
checkpoint='typed' -> convaiinnovations/laya subfolder typed-decisions (1,024-token window, trained on more decision types)
criteria='full'    -> every option carries its description; 'names' -> label name only
"""
import time

QUESTION = {
    "docs": "Which type of document is this page?",
    "routing": "Which tool should be called to handle this request?",
    "sweep": "Which tool should be called to handle this request?",
}


def build_query(task, item, criteria="full"):
    state = {"text": item["input"]} if task == "docs" else {"request": item["input"]}
    if criteria == "names":
        crit = {k: k.replace("_", " ") for k in item["labels"]}
    else:
        crit = dict(item["labels"])
    return state, {"q": {"type": "choice", "instructions": QUESTION[task], "criteria": crit}}


def load_agent(checkpoint="base"):
    import laya
    if checkpoint == "typed":
        return laya.load("convaiinnovations/laya", subfolder="typed-decisions")
    return laya.load("convaiinnovations/laya")


def system_name(criteria="full", checkpoint="base", extra=None):
    parts = ([checkpoint] if checkpoint != "base" else []) + ([criteria] if criteria != "full" else []) + \
            ([extra] if extra else [])
    return "laya" if not parts else "laya[" + ",".join(parts) + "]"


class LayaSystem:
    def __init__(self, criteria="full", checkpoint="base", extra=None, agent=None):
        self.criteria = criteria
        self.name = system_name(criteria, checkpoint, extra)
        self.agent = agent or load_agent(checkpoint)
        self.predict("routing", {"input": "warm up", "labels": {"a": "first", "b": "second"}})  # not recorded

    def predict(self, task, item):
        state, questions = build_query(task, item, self.criteria)
        t0 = time.perf_counter()
        res = self.agent.predict(state, questions)
        latency_ms = (time.perf_counter() - t0) * 1000
        a = res["answers"]["q"]
        probs = sorted(a.get("probabilities", {}).items(), key=lambda kv: -kv[1])[:3]
        u = res.get("usage", {})
        return {"pred": a["choice"], "latency_ms": round(latency_ms, 1), "confidence": a.get("answer_confidence"),
                "top3": probs, "prompt_tokens": u.get("input_tokens"), "output_tokens": 0,
                "truncated": u.get("truncated")}
