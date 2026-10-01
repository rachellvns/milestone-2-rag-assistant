# store.py
from qdrant_client import QdrantClient, models
from config import EMBEDDING_MODEL, QDRANT_PATH

client = QdrantClient(path=QDRANT_PATH)

HYBRID_COLLECTION_NAME = "corpus_hybrid"
BM25_MODEL = "Qdrant/bm25"

def ensure_hybrid(name: str = HYBRID_COLLECTION_NAME) -> None:
    if client.collection_exists(name):
        return
    client.create_collection(
        name,
        vectors_config={
            "dense": models.VectorParams(
                size=client.get_embedding_size(EMBEDDING_MODEL),
                distance=models.Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)
        },
    )


def retrieve_hybrid(q: str, user_id: str, doc_type: str | None = None, limit: int = 5):
    if not user_id:
        raise ValueError("user_id is required")   # never fall back to "no filter"

    must = [models.FieldCondition(key="allowed", match=models.MatchAny(any=[user_id, "public"]))]
    if doc_type:
        must.append(models.FieldCondition(key="doc_type", match=models.MatchValue(value=doc_type)))
    query_filter = models.Filter(must=must)
    return client.query_points(
        HYBRID_COLLECTION_NAME,
        prefetch=[
            models.Prefetch(query=models.Document(text=q, model=EMBEDDING_MODEL),
                            using="dense", filter=query_filter, limit=20),
            models.Prefetch(query=models.Document(text=q, model=BM25_MODEL),
                            using="bm25", filter=query_filter, limit=20),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=limit,
    ).points