from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ["ANTHROPIC_API_KEY"]
BASE_URL = os.environ["ANTHROPIC_BASE_URL"]
MODEL = "claude-sonnet-4-6"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "corpus"

DOC_TYPE_BY_FILE = {
    "type2-diabetes-overview.md": "condition_overview",
    "asthma-overview.md": "condition_overview",
    "ckd-overview.md": "condition_overview",
    "hypertension-guideline.md": "treatment_guideline",
    "migraine-guideline.md": "treatment_guideline",
    "depression-anxiety-screening-guideline.md": "treatment_guideline",
    "knee-replacement-patient-education.md": "patient_education",
    "cardiovascular-nutrition.md": "patient_education",
    "adult-vaccination-patient-education.md": "patient_education",
    "antibiotic-resistance-summary.md": "clinical_summary",
}

ALLOWED_BY_FILE = {
    "hypertension-guideline.md": ["doctor"],
    "depression-anxiety-screening-guideline.md": ["doctor"],
    "antibiotic-resistance-summary": ["doctor"]
}