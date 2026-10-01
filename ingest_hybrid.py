# ingest_hybrid.py: manifest + delete-then-upsert
import hashlib, json
from pathlib import Path
from qdrant_client import models
from chunker import chunk
from config import ALLOWED_BY_FILE, EMBEDDING_MODEL, DOC_TYPE_BY_FILE
from store import client, ensure_hybrid, HYBRID_COLLECTION_NAME, BM25_MODEL
from corpus_version import bump_corpus_version

MANIFEST = "manifest.json"


def load_json(p):
    return json.loads(Path(p).read_text()) if Path(p).exists() else {}


def save_json(p, data):
    Path(p).write_text(json.dumps(data, indent=2))


def stable_id(path: str, i: int) -> int:
    h = hashlib.md5(f"{path}:{i}".encode()).hexdigest()
    return int(h[:12], 16)


def upsert_file(p: Path) -> list[int]:
    text = p.read_text(errors="ignore")
    points = []
    for i, ch in enumerate(chunk(text)):
        points.append(models.PointStruct(
            id=stable_id(p.name, i),
            vector={
                "dense": models.Document(text=ch, model=EMBEDDING_MODEL),
                "bm25": models.Document(text=ch, model=BM25_MODEL),
            },
            payload={
                "source": p.name,
                "chunk": i,
                "text": ch,
                "doc_type": DOC_TYPE_BY_FILE.get(p.name, "unknown"),
                "allowed": ALLOWED_BY_FILE.get(p.name, ["public"]),
            },
        ))
    if points:
        client.upsert(collection_name=HYBRID_COLLECTION_NAME, points=points)
    return [pt.id for pt in points]


ensure_hybrid()

manifest = load_json(MANIFEST)   # {path: {hash, ids}}
changed = 0

for p in sorted(Path("corpus").glob("*.*")):
    allowed = ALLOWED_BY_FILE.get(p.name, ["public"])
    h = hashlib.sha256(p.read_bytes() + json.dumps(allowed).encode()).hexdigest()
    entry = manifest.get(str(p))
    if entry and entry["hash"] == h:
        continue
    if entry:
        client.delete(
            HYBRID_COLLECTION_NAME,
            points_selector=models.PointIdsList(points=entry["ids"]),
        )
    ids = upsert_file(p)
    manifest[str(p)] = {"hash": h, "ids": ids}
    changed += 1

for path in [k for k in manifest if not Path(k).exists()]:
    client.delete(
        HYBRID_COLLECTION_NAME,
        points_selector=models.PointIdsList(points=manifest[path]["ids"]),
    )
    del manifest[path]
    changed += 1

if changed:
    bump_corpus_version()
save_json(MANIFEST, manifest)
print(f"{changed} files re-indexed")