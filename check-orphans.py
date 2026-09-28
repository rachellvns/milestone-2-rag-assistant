# check_orphans.py
import sys
from qdrant_client import models
from store import client, HYBRID_COLLECTION_NAME, retrieve_hybrid

FILE = "asthma-overview.md"

def counts():
    total = client.count(HYBRID_COLLECTION_NAME, exact=True).count
    per_file = client.count(
        HYBRID_COLLECTION_NAME,
        count_filter=models.Filter(must=[
            models.FieldCondition(key="source", match=models.MatchValue(value=FILE))
        ]),
        exact=True,
    ).count
    return total, per_file

if __name__ == "__main__":
    total, per_file = counts()
    print(f"total points: {total} | {FILE} points: {per_file}")

    if len(sys.argv) > 1:
        phrase = sys.argv[1]
        hits = retrieve_hybrid(phrase)
        print(f"query: {phrase!r}")
        for h in hits:
            print(f"  {h.payload['source']} #{h.payload['chunk']} | score {h.score:.3f}")
            print(f"    {h.payload['text'][:100]}...")
        found = [h for h in hits if phrase[:60] in h.payload["text"]]
        print("DELETED TEXT STILL RETRIEVABLE" if found else "PASS: deleted sentence not in any returned chunk")