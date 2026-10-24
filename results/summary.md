# Results summary


## routing  (items answered by every system: 300)

| system | n | accuracy | 95% CI | median latency | p95 latency | decisions/hour | ECE |
|---|---|---|---|---|---|---|---|
| laya | 300 | 80.0% | 75.1%-84.1% | 498 ms | 748 ms | 6,824 | 0.058 |
| laya[calib] | 300 | 80.0% | 75.1%-84.1% | 521 ms | 787 ms | 6,599 | 0.051 |
| laya[typed,calib] | 300 | 84.3% | 79.8%-88.0% | 487 ms | 888 ms | 6,600 | 0.061 |
| laya[typed] | 300 | 84.3% | 79.8%-88.0% | 539 ms | 924 ms | 6,121 | 0.184 |
| llm:qwen3.5:4b | 300 | 89.7% | 85.7%-92.6% | 5,891 ms | 7,659 ms | 599 | n/a |

- laya vs laya[calib]: 0 items only the first got right, 0 only the second (McNemar exact p = 1.0000)

- laya vs laya[typed,calib]: 8 items only the first got right, 21 only the second (McNemar exact p = 0.0241)

- laya vs laya[typed]: 8 items only the first got right, 21 only the second (McNemar exact p = 0.0241)

- laya vs llm:qwen3.5:4b: 11 items only the first got right, 40 only the second (McNemar exact p = 0.0001)

- laya[calib] vs laya[typed,calib]: 8 items only the first got right, 21 only the second (McNemar exact p = 0.0241)

- laya[calib] vs laya[typed]: 8 items only the first got right, 21 only the second (McNemar exact p = 0.0241)

- laya[calib] vs llm:qwen3.5:4b: 11 items only the first got right, 40 only the second (McNemar exact p = 0.0001)

- laya[typed,calib] vs laya[typed]: 0 items only the first got right, 0 only the second (McNemar exact p = 1.0000)

- laya[typed,calib] vs llm:qwen3.5:4b: 10 items only the first got right, 26 only the second (McNemar exact p = 0.0113)

- laya[typed] vs llm:qwen3.5:4b: 10 items only the first got right, 26 only the second (McNemar exact p = 0.0113)

### Routing accuracy by slice (common items)

| system | 2-4 tools (multiple) | real queries, 2-10+ tools | 'none' cases (no tool applies) |
|---|---|---|---|
| laya | 93.6% (n=109) | 72.0% (n=125) | 72.7% (n=66) |
| laya[calib] | 93.6% (n=109) | 72.0% (n=125) | 72.7% (n=66) |
| laya[typed,calib] | 99.1% (n=109) | 84.0% (n=125) | 60.6% (n=66) |
| laya[typed] | 99.1% (n=109) | 84.0% (n=125) | 60.6% (n=66) |
| llm:qwen3.5:4b | 97.2% (n=109) | 91.2% (n=125) | 74.2% (n=66) |

### 'none' handling (knowing when NOT to call a tool)

| system | none recall | none precision | false-positive tool calls on 'none' |
|---|---|---|---|
| laya | 72.7% | 60.0% | 18 of 66 |
| laya[calib] | 72.7% | 60.0% | 18 of 66 |
| laya[typed,calib] | 60.6% | 88.9% | 26 of 66 |
| laya[typed] | 60.6% | 88.9% | 26 of 66 |
| llm:qwen3.5:4b | 74.2% | 89.1% | 17 of 66 |

## sweep  (items answered by every system: 160)

| system | n | accuracy | 95% CI | median latency | p95 latency | decisions/hour | ECE |
|---|---|---|---|---|---|---|---|
| laya | 160 | 84.4% | 78.0%-89.2% | 733 ms | 896 ms | 4,955 | 0.117 |
| laya[typed] | 160 | 90.6% | 85.1%-94.2% | 863 ms | 968 ms | 4,395 | 0.076 |
| llm:qwen3.5:4b | 160 | 96.2% | 92.1%-98.3% | 7,957 ms | 11.3 s | 425 | n/a |

- laya vs laya[typed]: 6 items only the first got right, 16 only the second (McNemar exact p = 0.0525)

- laya vs llm:qwen3.5:4b: 3 items only the first got right, 22 only the second (McNemar exact p = 0.0002)

- laya[typed] vs llm:qwen3.5:4b: 3 items only the first got right, 12 only the second (McNemar exact p = 0.0352)

### Accuracy vs number of candidate tools

| system | 5 tools | 10 tools | 20 tools | 30 tools |
|---|---|---|---|---|
| laya | 92.5% | 75.0% | 82.5% | 87.5% |
| laya[typed] | 97.5% | 95.0% | 80.0% | 90.0% |
| llm:qwen3.5:4b | 97.5% | 97.5% | 95.0% | 95.0% |

## docs  (items answered by every system: 300)

| system | n | accuracy | 95% CI | macro-F1 | median latency | p95 latency | decisions/hour | ECE |
|---|---|---|---|---|---|---|---|---|
| laya | 300 | 51.7% | 46.0%-57.3% | 0.575 | 1,703 ms | 1,760 ms | 2,245 | 0.342 |
| laya[calib] | 300 | 51.7% | 46.0%-57.3% | 0.575 | 1,636 ms | 1,722 ms | 2,319 | 0.080 |
| laya[names] | 300 | 57.7% | 52.0%-63.1% | 0.583 | 1,632 ms | 2,769 ms | 2,134 | 0.284 |
| laya[typed,calib] | 300 | 60.3% | 54.7%-65.7% | 0.646 | 1,848 ms | 2,785 ms | 1,897 | 0.061 |
| laya[typed] | 300 | 60.3% | 54.7%-65.7% | 0.646 | 1,835 ms | 2,676 ms | 1,937 | 0.089 |
| llm:qwen3.5:4b | 300 | 81.7% | 76.9%-85.6% | 0.832 | 6,568 ms | 10.4 s | 513 | n/a |

- laya vs laya[calib]: 0 items only the first got right, 0 only the second (McNemar exact p = 1.0000)

- laya vs laya[names]: 22 items only the first got right, 40 only the second (McNemar exact p = 0.0300)

- laya vs laya[typed,calib]: 13 items only the first got right, 39 only the second (McNemar exact p = 0.0004)

- laya vs laya[typed]: 13 items only the first got right, 39 only the second (McNemar exact p = 0.0004)

- laya vs llm:qwen3.5:4b: 9 items only the first got right, 99 only the second (McNemar exact p = 0.0000)

- laya[calib] vs laya[names]: 22 items only the first got right, 40 only the second (McNemar exact p = 0.0300)

- laya[calib] vs laya[typed,calib]: 13 items only the first got right, 39 only the second (McNemar exact p = 0.0004)

- laya[calib] vs laya[typed]: 13 items only the first got right, 39 only the second (McNemar exact p = 0.0004)

- laya[calib] vs llm:qwen3.5:4b: 9 items only the first got right, 99 only the second (McNemar exact p = 0.0000)

- laya[names] vs laya[typed,calib]: 34 items only the first got right, 42 only the second (McNemar exact p = 0.4222)

- laya[names] vs laya[typed]: 34 items only the first got right, 42 only the second (McNemar exact p = 0.4222)

- laya[names] vs llm:qwen3.5:4b: 4 items only the first got right, 76 only the second (McNemar exact p = 0.0000)

- laya[typed,calib] vs laya[typed]: 0 items only the first got right, 0 only the second (McNemar exact p = 1.0000)

- laya[typed,calib] vs llm:qwen3.5:4b: 22 items only the first got right, 86 only the second (McNemar exact p = 0.0000)

- laya[typed] vs llm:qwen3.5:4b: 22 items only the first got right, 86 only the second (McNemar exact p = 0.0000)

### Per-class recall (common items)

| class | n | laya | laya[calib] | laya[names] | laya[typed,calib] | laya[typed] | llm:qwen3.5:4b |
|---|---|---|---|---|---|---|---|
| budget | 17 | 82.4% | 82.4% | 82.4% | 88.2% | 88.2% | 94.1% |
| email | 10 | 70.0% | 70.0% | 50.0% | 80.0% | 80.0% | 100.0% |
| form | 21 | 42.9% | 42.9% | 66.7% | 52.4% | 52.4% | 95.2% |
| handwritten | 53 | 17.0% | 17.0% | 9.4% | 47.2% | 47.2% | 11.3% |
| invoice | 17 | 76.5% | 76.5% | 94.1% | 58.8% | 58.8% | 100.0% |
| letter | 45 | 31.1% | 31.1% | 24.4% | 44.4% | 44.4% | 88.9% |
| memo | 14 | 85.7% | 85.7% | 85.7% | 92.9% | 92.9% | 100.0% |
| news_article | 26 | 38.5% | 38.5% | 26.9% | 42.3% | 42.3% | 100.0% |
| questionnaire | 12 | 91.7% | 91.7% | 100.0% | 100.0% | 100.0% | 100.0% |
| resume | 55 | 52.7% | 52.7% | 87.3% | 50.9% | 50.9% | 100.0% |
| scientific_publication | 12 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| specification | 18 | 83.3% | 83.3% | 94.4% | 88.9% | 88.9% | 94.4% |

## Cascade on routing: laya first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 80.0% | 528 ms | 6,824 | 11.4x |
| < 0.5 | 8.3% | 84.3% | 1,039 ms | 3,463 | 5.8x |
| < 0.7 | 21.0% | 88.0% | 1,792 ms | 2,009 | 3.4x |
| < 0.8 | 30.7% | 87.3% | 2,393 ms | 1,504 | 2.5x |
| < 0.9 | 45.0% | 87.7% | 3,243 ms | 1,110 | 1.9x |
| < 0.95 | 59.3% | 88.0% | 4,074 ms | 884 | 1.5x |
| < 0.99 | 78.7% | 88.7% | 5,180 ms | 695 | 1.2x |
| always LLM (+Laya) | 100.0% | 89.7% | 6,533 ms | 551 | 0.9x |

LLM only: accuracy 89.7%, mean latency 6,005 ms

## Cascade on routing: laya[calib] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 80.0% | 546 ms | 6,599 | 11.0x |
| < 0.5 | 10.3% | 85.0% | 1,227 ms | 2,934 | 4.9x |
| < 0.7 | 27.7% | 88.7% | 2,319 ms | 1,552 | 2.6x |
| < 0.8 | 35.3% | 89.0% | 2,770 ms | 1,300 | 2.2x |
| < 0.9 | 49.3% | 88.7% | 3,601 ms | 1,000 | 1.7x |
| < 0.95 | 64.3% | 89.0% | 4,544 ms | 792 | 1.3x |
| < 0.99 | 80.3% | 89.0% | 5,414 ms | 665 | 1.1x |
| always LLM (+Laya) | 100.0% | 89.7% | 6,551 ms | 550 | 0.9x |

LLM only: accuracy 89.7%, mean latency 6,005 ms

## Cascade on routing: laya[typed,calib] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 84.3% | 545 ms | 6,600 | 11.0x |
| < 0.5 | 7.3% | 87.0% | 1,016 ms | 3,545 | 5.9x |
| < 0.7 | 24.0% | 88.7% | 2,019 ms | 1,783 | 3.0x |
| < 0.8 | 32.7% | 88.3% | 2,602 ms | 1,384 | 2.3x |
| < 0.9 | 46.7% | 88.7% | 3,463 ms | 1,039 | 1.7x |
| < 0.95 | 58.0% | 89.7% | 4,186 ms | 860 | 1.4x |
| < 0.99 | 78.7% | 90.0% | 5,383 ms | 669 | 1.1x |
| always LLM (+Laya) | 100.0% | 89.7% | 6,551 ms | 550 | 0.9x |

LLM only: accuracy 89.7%, mean latency 6,005 ms

## Cascade on routing: laya[typed] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 84.3% | 588 ms | 6,121 | 10.2x |
| < 0.5 | 17.7% | 86.7% | 1,707 ms | 2,109 | 3.5x |
| < 0.7 | 54.0% | 89.3% | 3,887 ms | 926 | 1.5x |
| < 0.8 | 75.3% | 89.7% | 5,183 ms | 695 | 1.2x |
| < 0.9 | 94.7% | 89.7% | 6,295 ms | 572 | 1.0x |
| < 0.95 | 99.0% | 89.7% | 6,520 ms | 552 | 0.9x |
| < 0.99 | 99.7% | 89.7% | 6,572 ms | 548 | 0.9x |
| always LLM (+Laya) | 100.0% | 89.7% | 6,593 ms | 546 | 0.9x |

LLM only: accuracy 89.7%, mean latency 6,005 ms

## Cascade on docs: laya first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 51.7% | 1,604 ms | 2,245 | 4.4x |
| < 0.5 | 7.3% | 54.7% | 2,112 ms | 1,705 | 3.3x |
| < 0.7 | 21.7% | 59.7% | 3,115 ms | 1,156 | 2.3x |
| < 0.8 | 31.7% | 65.7% | 3,818 ms | 943 | 1.8x |
| < 0.9 | 42.0% | 68.3% | 4,518 ms | 797 | 1.6x |
| < 0.95 | 48.7% | 70.7% | 4,934 ms | 730 | 1.4x |
| < 0.99 | 57.7% | 73.3% | 5,536 ms | 650 | 1.3x |
| always LLM (+Laya) | 100.0% | 81.7% | 8,615 ms | 418 | 0.8x |

LLM only: accuracy 81.7%, mean latency 7,011 ms

## Cascade on docs: laya[calib] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 51.7% | 1,553 ms | 2,319 | 4.5x |
| < 0.5 | 60.0% | 74.3% | 5,635 ms | 639 | 1.2x |
| < 0.7 | 73.0% | 79.0% | 6,574 ms | 548 | 1.1x |
| < 0.8 | 80.3% | 80.0% | 7,135 ms | 505 | 1.0x |
| < 0.9 | 91.7% | 81.0% | 7,966 ms | 452 | 0.9x |
| < 0.95 | 96.7% | 81.3% | 8,348 ms | 431 | 0.8x |
| < 0.99 | 99.0% | 81.3% | 8,500 ms | 424 | 0.8x |
| always LLM (+Laya) | 100.0% | 81.7% | 8,564 ms | 420 | 0.8x |

LLM only: accuracy 81.7%, mean latency 7,011 ms

## Cascade on docs: laya[names] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 57.7% | 1,687 ms | 2,134 | 4.2x |
| < 0.5 | 7.7% | 62.0% | 2,207 ms | 1,632 | 3.2x |
| < 0.7 | 20.3% | 67.0% | 3,079 ms | 1,169 | 2.3x |
| < 0.8 | 27.7% | 69.3% | 3,562 ms | 1,011 | 2.0x |
| < 0.9 | 39.3% | 73.7% | 4,317 ms | 834 | 1.6x |
| < 0.95 | 45.0% | 73.7% | 4,695 ms | 767 | 1.5x |
| < 0.99 | 54.7% | 76.7% | 5,433 ms | 663 | 1.3x |
| always LLM (+Laya) | 100.0% | 81.7% | 8,698 ms | 414 | 0.8x |

LLM only: accuracy 81.7%, mean latency 7,011 ms

## Cascade on docs: laya[typed,calib] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 60.3% | 1,898 ms | 1,897 | 3.7x |
| < 0.5 | 47.3% | 77.7% | 5,234 ms | 688 | 1.3x |
| < 0.7 | 69.0% | 80.0% | 6,673 ms | 539 | 1.1x |
| < 0.8 | 82.7% | 80.3% | 7,720 ms | 466 | 0.9x |
| < 0.9 | 93.7% | 81.0% | 8,502 ms | 423 | 0.8x |
| < 0.95 | 99.0% | 81.7% | 8,847 ms | 407 | 0.8x |
| < 0.99 | 100.0% | 81.7% | 8,909 ms | 404 | 0.8x |
| always LLM (+Laya) | 100.0% | 81.7% | 8,909 ms | 404 | 0.8x |

LLM only: accuracy 81.7%, mean latency 7,011 ms

## Cascade on docs: laya[typed] first, escalate to llm:qwen3.5:4b when its confidence < threshold  (n=300)

| threshold | escalated to LLM | accuracy | mean latency | decisions/hour | speed-up vs LLM-only |
|---|---|---|---|---|---|
| Laya only | 0.0% | 60.3% | 1,858 ms | 1,937 | 3.8x |
| < 0.5 | 28.0% | 72.0% | 3,777 ms | 953 | 1.9x |
| < 0.7 | 53.3% | 78.0% | 5,575 ms | 646 | 1.3x |
| < 0.8 | 62.7% | 80.0% | 6,202 ms | 580 | 1.1x |
| < 0.9 | 75.0% | 80.3% | 7,006 ms | 514 | 1.0x |
| < 0.95 | 87.0% | 80.7% | 7,955 ms | 453 | 0.9x |
| < 0.99 | 97.3% | 81.7% | 8,702 ms | 414 | 0.8x |
| always LLM (+Laya) | 100.0% | 81.7% | 8,870 ms | 406 | 0.8x |

LLM only: accuracy 81.7%, mean latency 7,011 ms

## Laya on the COMPLETE benchmarks (not subsampled)

| task | system | n | accuracy | 95% CI | median latency | decisions/hour | ECE |
|---|---|---|---|---|---|---|---|
| routing | laya | 548 | 81.4% | 77.9%-84.4% | 490 ms | 6,709 | 0.036 |
| sweep | laya | 400 | 85.0% | 81.2%-88.2% | 723 ms | 5,091 | 0.116 |
| docs | laya | 1002 | 51.4% | 48.3%-54.5% | 1,708 ms | 2,236 | 0.339 |
