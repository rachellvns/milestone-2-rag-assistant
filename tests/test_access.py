# tests/test_access.py
import re
from pathlib import Path
import pytest
from config import ALLOWED_BY_FILE
from store import retrieve_hybrid

DOCTOR_ONLY = "hypertension-guideline.md"
PUBLIC_DOC  = "asthma-overview.md"


def title_of(fname: str) -> str:
    text = Path("corpus", fname).read_text(errors="ignore")
    return re.search(r"^title:\s*(.+)$", text, re.M).group(1).strip()


def test_config_has_no_typos():
    for fname in ALLOWED_BY_FILE:
        assert Path("corpus", fname).exists(), f"{fname} not found in corpus/"


def test_patient_cannot_see_doctor_only_doc():
    hits = retrieve_hybrid(title_of(DOCTOR_ONLY), user_id="patient")
    assert hits, "retrieval returned nothing, so the test proves nothing"
    assert all(h.payload["source"] != DOCTOR_ONLY for h in hits)


def test_doctor_can_see_doctor_only_doc():
    hits = retrieve_hybrid(title_of(DOCTOR_ONLY), user_id="doctor")
    assert any(h.payload["source"] == DOCTOR_ONLY for h in hits)


def test_patient_can_see_public_doc():
    hits = retrieve_hybrid(title_of(PUBLIC_DOC), user_id="patient")
    assert any(h.payload["source"] == PUBLIC_DOC for h in hits)


def test_missing_role_fails_closed():
    with pytest.raises(ValueError):
        retrieve_hybrid("anything", user_id="")