# Laya vs a local LLM: tool routing and document classification

Is a small open-source "System One" decision model ([Laya](https://github.com/NandhaKishorM/laya), 421M params, Apache 2.0) worth using instead of a local LLM (qwen3.5:4b via Ollama) for two jobs agents and document pipelines do constantly?

1. **Tool-call routing:** pick the right tool (or "none") for a request. Data: [BFCL v3](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard) (real queries, real tool schemas, ground truth).
2. **Document typing:** classify a page from its OCR text into 12 classes. Data: [RVL-CDIP-N](https://huggingface.co/datasets/stefan-hf/rvlcdip-n) (1,002 real pages, NeurIPS 2022).

No hand-written data. Both systems get identical inputs and label descriptions. Full write-up: [blog-post.md](blog-post.md).

## Headline results (matched subsets, same items for both systems)

| Task | Laya (base) | Laya (typed-decisions) | qwen3.5:4b | Laya latency vs LLM |
|---|---|---|---|---|
| Routing (n=300) | 80.0% | 84.3% | **89.7%** | 0.5 s vs 5.9 s |
| Tool-count sweep (n=160) | 84.4% | 90.6% | **96.2%** | 0.7 s vs 8.0 s |
| Document types (n=300) | 51.7% (57.7% with name-only options) | 60.3% | **81.7%** | 1.7 s vs 6.6 s |

All Laya numbers are zero-shot; Laya was **not fine-tuned** on this data.

- **Cascade** (Laya answers when confident, else escalate to the LLM): with the typed checkpoint and calibrated confidence, escalating 24% of routing decisions gives 88.7% accuracy at 3.0x the LLM's speed. For documents, even calibrated confidence shows Laya is unsure about about half the pages: escalating 47% gives 77.7% for a 1.3x speed-up.
- **Combined system, out of sample** (`src/cascade_cv.py`: choose the escalation threshold on a random half, score the other half, 500 splits): routing lands about 2.6 points below the LLM (5th-95th pct -6.7 to +0.7) and ~5.6x faster with ~87% fewer LLM calls; documents about 2.9 points below and only ~1.2x faster. Figures for posts: `src/make_figures.py` -> `results/charts/linkedin_*.png`.
- **Calibration refit** (no weight changes, fitted on items disjoint from the test set) cut expected calibration error from 0.342 to 0.080 on documents (base checkpoint) and from 0.184 to 0.061 on routing (typed checkpoint). Accuracy is unchanged by construction.
- Laya has a **512-token input window shared by the input and the option text**; 68% of document decisions were truncated with long option descriptions (24% with names only).
- Laya warns on load that its confidence is uncalibrated for questions with 11 or more options, which is what the 12-class document task hits.

All numbers, confidence intervals, McNemar tests, per-class recall and the cascade tables are in [results/summary.md](results/summary.md); charts are in `results/charts/`.

## Reproduce

```bash
python -m venv .venv && .venv\Scripts\activate
pip install laya requests pandas scikit-learn matplotlib
ollama pull qwen3.5:4b

python src/fetch_data.py          # downloads BFCL v3 + RVL-CDIP-N labels/OCR text
python src/build_benchmarks.py    # builds the routing and sweep sets

# the same stratified subset is used for every system
python src/run_eval.py --task routing --system llm:qwen3.5:4b --limit 300
python src/run_eval.py --task sweep   --system llm:qwen3.5:4b --limit 160
python src/run_eval.py --task docs    --system llm:qwen3.5:4b --limit 300
python src/run_eval.py --task routing --system laya --limit 300
python src/run_eval.py --task sweep   --system laya --limit 160
python src/run_eval.py --task docs    --system laya --limit 300
python src/run_eval.py --task docs    --system laya-names --limit 300   # name-only option text
python src/run_eval.py --task routing --system laya --tag full          # complete benchmarks (also sweep, docs)

# larger-window typed-decisions checkpoint, and the calibration refit (calibration items are disjoint from the test subset)
python src/run_eval.py --task routing --system laya-typed --limit 300   # also sweep --limit 160, docs --limit 300
python src/calibrate_laya.py --checkpoint base  --tasks docs routing
python src/calibrate_laya.py --checkpoint typed --tasks docs routing

python src/analyze.py             # tables -> results/summary.md, charts -> results/charts/
```

The runner saves every decision and resumes where it stopped. Run systems one at a time on an idle machine, otherwise the latency numbers are meaningless.

## Layout

```
src/fetch_data.py         download datasets
src/build_benchmarks.py   routing + tool-count-sweep sets from BFCL
src/common.py             task definitions, identical prompts/labels for every system
src/llm_system.py         Ollama LLM, constrained to a valid label (structured output)
src/laya_system.py        Laya adapter (base or typed-decisions checkpoint; full or name-only option text)
src/calibrate_laya.py     refit Laya's confidence temperature on held-out items, then score the test subset
src/run_eval.py           resumable runner
src/analyze.py            accuracy + CIs, McNemar, calibration, cascade, charts
src/cascade_cv.py         out-of-sample estimate for the Laya -> LLM combined system
src/make_figures.py       side-by-side "alone vs combined" figures for posts
src/probe_*.py            probes: Laya's output format and its truncation behaviour
results/                  every saved decision (*.jsonl), summary.md, charts/
```

## Limitations

Laya was never fine-tuned on this data (zero-shot only); a fair fine-tuning test needs a leak-free split, since consecutive pages of a document are near-duplicates and source-PDF identity is not recoverable from the file names. One LLM only. Laya ran on CPU (CPU-only torch wheel) while the LLM used a 4GB GPU with CPU offload; Laya on a GPU was not tested. Latency is single-request, not batched. Subsets of 300 keep intervals wide. Cascade thresholds and the name-only variant were chosen after seeing results on the same data. Both benchmarks are public and may overlap with training data. Only tool selection is scored, not argument filling. Jev was excluded (paid API key).
