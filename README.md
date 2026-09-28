## Freshness test: delete-then-upsert

**Goal:** prove that editing a document so it produces fewer chunks leaves no
orphaned (stale) chunks in the index.

**Method**

1. Ingested the corpus with `ingest_hybrid.py` and recorded the point counts.
2. Edited `asthma-overview.md` to remove content, so it produced fewer chunks.
3. Re-ran `ingest_hybrid.py`. The manifest detected the changed hash, deleted
   the file's old points by id, then upserted the new ones.
4. Counted points again and queried for a sentence from the deleted text
   using `check-orphans.py`.

**Results**

| Check | Before | After | Result |
|---|---|---|---|
| (a) Total points | 52 | 51 | No growth |
| (a) `asthma-overview.md` points | 5 | 4 | Old chunk removed |
| (b) Query for deleted sentence | n/a | Not in any returned chunk | No hit |

The total dropped by exactly the amount the asthma file dropped (1), so the
other 47 points were untouched and no stale chunk survived.

**Deleted sentence queried:**
> "Asthma is a chronic inflammatory disease of the airways characterized by variable and recurring symptoms of wheeze, shortness of breath, chest tightness, and cough, accompanied by variable airflow limitation that often reverses either spontaneously or with treatment. While frequently thought of as a childhood condition, a substantial proportion of asthma either persists into adulthood or first develops in adult life, sometimes referred to as adult-onset asthma, which tends to follow a somewhat different clinical course than childhood-onset disease.

The airway inflammation in asthma involves a complex interplay of immune cells, including eosinophils, mast cells, and T-helper lymphocytes, which release inflammatory mediators that cause bronchial smooth muscle contraction, mucus hypersecretion, and airway wall thickening over time. Repeated inflammatory episodes can lead to airway remodeling, a process involving structural changes such as subepithelial fibrosis and smooth muscle hypertrophy, which may contribute to a degree of fixed airflow obstruction in some patients with long-standing, poorly controlled disease."

`check-orphans.py` printed: `PASS: deleted sentence not in any returned chunk`

**Takeaway:** with stable ids and upsert alone, an edited file that
produces fewer chunks would leave its highest-indexed old chunks in the index,
and retrieval could still return text that no longer exists in the document.
Deleting a file's old points before upserting the new ones prevents that.

**Reproduce**

```powershell
uv run python check-orphans.py                      # counts before
# edit the document (asthma-overview.md), then:
uv run python ingest_hybrid.py                      # prints "1 files re-indexed"  

# counts after + retrieval check
uv run python check-orphans.py "Asthma is a chronic inflammatory disease of the airways characterized by variable and recurring symptoms of wheeze, shortness of breath, chest tightness, and cough, accompanied by variable airflow limitation that often reverses either spontaneously or with treatment. While frequently thought of as a childhood condition, a substantial proportion of asthma either persists into adulthood or first develops in adult life, sometimes referred to as adult-onset asthma, which tends to follow a somewhat different clinical course than childhood-onset disease.

The airway inflammation in asthma involves a complex interplay of immune cells, including eosinophils, mast cells, and T-helper lymphocytes, which release inflammatory mediators that cause bronchial smooth muscle contraction, mucus hypersecretion, and airway wall thickening over time. Repeated inflammatory episodes can lead to airway remodeling, a process involving structural changes such as subepithelial fibrosis and smooth muscle hypertrophy, which may contribute to a degree of fixed airflow obstruction in some patients with long-standing, poorly controlled disease."
```