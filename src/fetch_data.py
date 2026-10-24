"""Download the two public datasets used in the study.

- BFCL v3 (Berkeley Function Calling Leaderboard): real user queries + candidate functions + ground truth
- RVL-CDIP-N (stefan-hf/rvlcdip-n): 1,002 real scanned business documents with OCR text, 16 classes
"""
import json
import pathlib
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
(DATA / "bfcl").mkdir(parents=True, exist_ok=True)

BFCL_BASE = "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/resolve/main"
BFCL_FILES = [
    "BFCL_v3_simple.json", "BFCL_v3_multiple.json", "BFCL_v3_live_multiple.json",
    "BFCL_v3_irrelevance.json", "BFCL_v3_live_irrelevance.json",
    "possible_answer/BFCL_v3_simple.json", "possible_answer/BFCL_v3_multiple.json",
    "possible_answer/BFCL_v3_live_multiple.json",
]


def fetch_bfcl():
    for name in BFCL_FILES:
        out = DATA / "bfcl" / name.replace("/", "__")
        if out.exists():
            continue
        r = requests.get(f"{BFCL_BASE}/{name}", timeout=120)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"bfcl  {name}: {len(r.content) / 1024:.0f} KB")


def fetch_docs():
    """Only the label + OCR text are needed, so grab metadata.jsonl and skip the 1,002 JPEGs."""
    out = DATA / "docs_rvlcdip_n.jsonl"
    if out.exists():
        print("docs already downloaded")
        return
    url = "https://huggingface.co/datasets/stefan-hf/rvlcdip-n/resolve/main/test/metadata.jsonl"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    rows = []
    for i, line in enumerate(r.content.decode("utf-8").splitlines()):
        if not line.strip():
            continue
        item = json.loads(line)
        rows.append({"id": i, "file": item.get("file_name", ""), "label": item["label"],
                     "text": item.get("text") or ""})
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"docs  {len(rows)} rows, keys in source: {sorted(item.keys())}")


if __name__ == "__main__":
    fetch_bfcl()
    fetch_docs()
