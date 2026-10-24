"""Shared task definitions: identical inputs and label descriptions are given to every system."""
import json
import pathlib
import random
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

DOC_CHARS = 1500  # every system sees the same first 1,500 characters of OCR text

# Generic definitions derived only from the category names (not tuned on the data).
DOC_LABELS = {
    "budget": "a financial budget, spending plan or fiscal table with amounts",
    "email": "an email message with headers such as From, To, Subject",
    "form": "a structured form with labelled fields to fill in",
    "handwritten": "handwritten notes or handwritten text",
    "invoice": "a bill requesting payment, with line items, amounts and a due date",
    "letter": "a formal or personal letter with a salutation and sign-off",
    "memo": "an internal memorandum with To, From, Date and Subject lines",
    "news_article": "a news or magazine article",
    "questionnaire": "a survey or questionnaire made up of questions",
    "resume": "a CV or resume listing work experience, education and skills",
    "scientific_publication": "an academic paper with abstract, methods and citations",
    "specification": "a technical specification or requirements document",
}

NONE_DESC = "no listed tool is appropriate for this request"


def load_jsonl(path):
    return [json.loads(l) for l in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def load_task(task, limit=None, seed=42):
    """Return a list of items: {id, input, labels:{label:description}, answer, meta}."""
    items = []
    if task in ("routing", "sweep"):
        fn = "routing.jsonl" if task == "routing" else "routing_sweep.jsonl"
        for x in load_jsonl(DATA / fn):
            labels = {t["name"]: t["description"] or "(no description)" for t in x["tools"]}
            labels["none"] = NONE_DESC
            items.append({"id": x["id"], "input": x["query"], "labels": labels, "answer": x["answer"],
                          "meta": {"source": x["source"], "n_tools": x["n_tools"], "base_id": x.get("base_id")}})
    elif task == "docs":
        rows = load_jsonl(DATA / "docs_rvlcdip_n.jsonl")
        for r in rows:
            items.append({"id": str(r["id"]), "input": r["text"][:DOC_CHARS], "labels": DOC_LABELS,
                          "answer": r["label"], "meta": {"source": "rvlcdip_n", "n_tools": len(DOC_LABELS)}})
    else:
        raise ValueError(task)
    if limit and limit < len(items):
        if task == "sweep":
            # keep a query's four candidate-list sizes together (paired design): limit counts total decisions
            bases = sorted({it["meta"]["base_id"] for it in items})
            random.Random(seed).shuffle(bases)
            keep = set(bases[:max(1, limit // 4)])
            items = [it for it in items if it["meta"]["base_id"] in keep]
        else:
            items = stratified_sample(items, limit, seed)
    return items


def stratified_sample(items, n, seed):
    """Deterministic sample keeping the answer-class mix, so every system sees the same subset."""
    rng = random.Random(seed)
    groups = defaultdict(list)
    for it in items:
        groups[it["answer"] if it["meta"]["source"] == "rvlcdip_n" else it["meta"]["source"]].append(it)
    picked = []
    for g in groups.values():
        rng.shuffle(g)
        picked += g[:max(1, round(n * len(g) / len(items)))]
    rng.shuffle(picked)
    return picked[:n]


def prompts(task, item):
    """System + user text for the LLM."""
    if task == "docs":
        sys_p = ("You are a document-type classifier. Read the OCR text of a scanned page and choose the single "
                 "best document type from the list.")
        user = "Document types:\n" + "\n".join(f"- {k}: {v}" for k, v in item["labels"].items()) + \
               f"\n\nOCR text of the page:\n\"\"\"\n{item['input']}\n\"\"\"\n\nWhich document type is it?"
    else:
        sys_p = ("You are a tool router for an AI agent. Given a user request and a list of tools, choose the single "
                 "best tool to call. If no listed tool can fulfil the request, choose \"none\".")
        user = "Tools:\n" + "\n".join(f"- {k}: {v}" for k, v in item["labels"].items()) + \
               f"\n\nUser request: {item['input']}\n\nWhich tool should be called?"
    return sys_p, user
