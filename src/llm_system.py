"""Local general-purpose LLM via Ollama, constrained to answer with a valid label (structured output)."""
import json
import time
import requests

from common import prompts

OLLAMA = "http://localhost:11434/api/chat"


class LlmSystem:
    def __init__(self, model, num_ctx=4096):
        self.model = model
        self.name = f"llm:{model}"
        self.num_ctx = num_ctx
        self.warm()

    def warm(self):
        requests.post(OLLAMA, json={"model": self.model, "messages": [{"role": "user", "content": "hi"}],
                                    "stream": False, "think": False, "keep_alive": "60m",
                                    "options": {"num_ctx": self.num_ctx, "num_predict": 1}}, timeout=300)

    def predict(self, task, item):
        sys_p, user = prompts(task, item)
        schema = {"type": "object", "properties": {"choice": {"type": "string", "enum": list(item["labels"])}},
                  "required": ["choice"]}
        t0 = time.perf_counter()
        r = requests.post(OLLAMA, json={
            "model": self.model, "stream": False, "think": False, "keep_alive": "60m", "format": schema,
            "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user}],
            "options": {"temperature": 0, "num_ctx": self.num_ctx, "num_predict": 48},
        }, timeout=600)
        latency_ms = (time.perf_counter() - t0) * 1000
        r.raise_for_status()
        body = r.json()
        try:
            pred = json.loads(body["message"]["content"])["choice"]
        except Exception:
            pred = "PARSE_ERROR"
        return {"pred": pred, "latency_ms": round(latency_ms, 1), "confidence": None,
                "prompt_tokens": body.get("prompt_eval_count"), "output_tokens": body.get("eval_count")}
