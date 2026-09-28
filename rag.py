# rag.py
from anthropic import Anthropic
from config import API_KEY, BASE_URL, MODEL
from store import client, retrieve_hybrid
from timing import timed, TIMINGS

llm = Anthropic(api_key=API_KEY, base_url=BASE_URL)

SYSTEM = ("Answer ONLY from the numbered sources provided."
          "Cite like [1] or [2] [3] after each claim."
          "If the sources do not contain the answer, reply exactly: "
          "'I don't have that in the knowledge base.'"
          "Never use outside knowledge.")

def retrieve(q: str, doc_type: str | None = None):
    query_filter = None
    if doc_type:
        query_filter = models.Filter(
            must=[models.FieldCondition(key="doc_type", match=models.MatchValue(value=doc_type))]
        )
    return client.query_points(
        collection_name=HYBRID_COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=models.Document(text=q, model=EMBEDDING_MODEL),
                using="dense",
                filter=query_filter,
                limit=20,
            ),
            models.Prefetch(
                query=models.Document(text=q, model=BM25_MODEL),
                using="bm25",
                filter=query_filter,
                limit=20,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=5,
    ).points


def call_llm(system: str, user: str, temperature: float = 0.0, max_tokens: int = 2000, thinking: bool = False) -> str:
    kwargs = dict(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    if not thinking:
        kwargs["thinking"] = {"type": "disabled"}
    response = llm.messages.create(**kwargs)
    for block in response.content:
        if block.type == "text":
            return block.text
    raise RuntimeError(f"No text block in response. Content types: {[b.type for b in response.content]}")

def answer(q: str, doc_type: str | None = None, retriever=None) -> tuple[str, list]:
    retriever = retriever or retrieve_hybrid
    
    with timed("retrieve"):
        hits = retriever(q, doc_type=doc_type)

    context = "\n\n".join(
        f"[{i+1}] ({h.payload['source']} #{h.payload['chunk']})"
        f"\n{h.payload['text']}"
        for i, h in enumerate(hits)
    )
    
    with timed("llm"):
        reply = call_llm(system=SYSTEM, user=f"Sources:\n{context}\n\nQuestion: {q}")

    return reply, hits


# if __name__ == "__main__":
    # reply, hits = answer("What increases a person's risk of developing this condition?")
    # print(TIMINGS)
    # for i, h in enumerate(hits):
    #     print(f"[{i+1}] {h.payload['source']} #{h.payload['chunk']} ({h.payload['doc_type']})")