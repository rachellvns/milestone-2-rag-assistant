# COSTS.md

## Latency
Measured with `uv run python try-timing.py` on 10 questions, non-streaming.
Times in ms. Retriever: hybrid (dense + BM25, RRF fusion).

### Per question
| #  | Question                                              | Retrieve |  LLM | Total |
|---:|-------------------------------------------------------|---------:|-----:|------:|
|  1 | What are the typical symptoms of type 2 diabetes a…   |       16 | 1608 |  1624 |
|  2 | Which first-line drug classes are used for hyperte…   |       16 | 2277 |  2293 |
|  3 | What are the common triggers of asthma?               |       23 | 2492 |  2515 |
|  4 | Which warning signs after a knee replacement shoul…   |       21 | 2392 |  2413 |
|  5 | What mechanisms do bacteria use to develop antibio…   |       11 | 2603 |  2614 |
|  6 | What preventive treatment options exist for freque…   |       11 | 4308 |  4319 |
|  7 | How is chronic kidney disease staged?                 |       10 | 2763 |  2773 |
|  8 | What dietary changes are recommended to protect he…   |       17 | 8501 |  8518 |
|  9 | How are PHQ-9 scores interpreted?                     |       10 | 6140 |  6150 |
| 10 | Which vaccines are recommended for adults aged 65…    |       13 | 3710 |  3723 |

### Summary (n=10)
| Stage    | Median | Mean | Min  | Max  |
|----------|-------:|-----:|-----:|-----:|
| retrieve |     14 |   15 |   10 |   23 |
| llm      |   2683 | 3679 | 1608 | 8501 |
| total    |   2694 | 3694 | 1624 | 8518 |

### Observations
- The LLM call is ~99.5% of total latency; retrieval (~14 ms median) is negligible.
- Median total is ~2.7 s. Without streaming, the user waits this long before
  seeing any text, above the ~2 s time-to-first-token budget.
- LLM time varies from 1.6 s (Q1) to 8.5 s (Q8). The two slowest (Q8, Q9)
  produced longer or formatted answers; generation time is not yet verified
  against answer length.
- Hybrid fills all 5 slots even when only some chunks are relevant (e.g. Q1
  also pulled `ckd-overview.md` and `asthma-overview.md`). Answers still cited
  the right sources, but the extra chunks cost prompt tokens.
- Time-to-first-token: not measured yet (needs streaming).