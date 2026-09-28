# corpus_version.py
from pathlib import Path

_F = Path("corpus_version.txt")

def corpus_version() -> int:
    return int(_F.read_text()) if _F.exists() else 1

def bump_corpus_version() -> None:
    _F.write_text(str(corpus_version() + 1))