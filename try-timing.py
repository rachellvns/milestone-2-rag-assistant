import statistics
from rag import answer
from timing import TIMINGS

# test 10 questions
QUESTIONS = [
    "What are the typical symptoms of type 2 diabetes at presentation?",
    "Which first-line drug classes are used for hypertension, and how do comorbidities affect the choice?",
    "What are the common triggers of asthma?",
    "Which warning signs after a knee replacement should prompt urgent medical attention?",
    "What mechanisms do bacteria use to develop antibiotic resistance?",
    "What preventive treatment options exist for frequent migraines?",
    "How is chronic kidney disease staged?",
    "What dietary changes are recommended to protect heart health?", 
    "How are PHQ-9 scores interpreted?",
    "Which vaccines are recommended for adults aged 65 and older?"
]

answer(QUESTIONS[0])

results = []
for i,q in enumerate(QUESTIONS, start=1):
    reply, hits = answer(q)
    t = dict(TIMINGS)
    t["total"] = t["retrieve"] + t["llm"]
    results.append(t)
    print(f"{i:>2}. retrieve {t['retrieve']:>5} ms | llm {t['llm']:>5} ms | total {t['total']:>5} ms | {q[:50]}")
    print(f"    → {reply[:120]}...")
    print(f"    sources: {[h.payload['source'] for h in hits]}")
    
print("Summary")
for stage in ["retrieve", "llm", "total"]:
    values = sorted(r[stage] for r in results)
    print(
        f"{stage:>8}: median {statistics.median(values):.0f} | "
        f"mean {statistics.mean(values):.0f} | "
        f"min {values[0]} | max {values[-1]}"
    )