# cache.py: sqlite-backed, safe keys
import hashlib, json, sqlite3, time
from types import SimpleNamespace
from rag import answer
from corpus_version import corpus_version


def cache_key(q: str, user: str, version: int) -> str:
    norm = " ".join(q.lower().split())
    return hashlib.sha256(f"{user}:{version}:{norm}".encode()).hexdigest()


def get(k: str, ttl: int = 3600) -> dict | None:
    with sqlite3.connect("cache.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS c (k TEXT PRIMARY KEY, v TEXT, t REAL)")
        row = conn.execute("SELECT v, t FROM c WHERE k = ?", (k,)).fetchone()
    if row and time.time() - row[1] <= ttl:
        return json.loads(row[0])
    return None


def put(k: str, value: dict) -> None:
    with sqlite3.connect("cache.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS c (k TEXT PRIMARY KEY, v TEXT, t REAL)")
        conn.execute(
            "INSERT OR REPLACE INTO c VALUES (?, ?, ?)",
            (k, json.dumps(value), time.time()),
        )


def serialise(hits) -> list[dict]:
    return [{"score": h.score, "payload": h.payload} for h in hits]


def deserialise(items: list[dict]) -> list:
    return [SimpleNamespace(score=i["score"], payload=i["payload"]) for i in items]


def cached_answer(q: str, user: str):
    k = cache_key(q, user, corpus_version())
    if hit := get(k):
        return hit["ans"], deserialise(hit["hits"])
    ans, hits = answer(q, user_id=user)
    put(k, {"ans": ans, "hits": serialise(hits)})
    return ans, hits