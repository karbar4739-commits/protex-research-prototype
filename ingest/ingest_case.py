from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import os
import hashlib
from typing import Dict, Any

# ======================================================
# ENV CONFIG
# ======================================================

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "protex")

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    raise RuntimeError("Missing API keys")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
openai = OpenAI(api_key=OPENAI_API_KEY)

EMBED_MODEL = "text-embedding-3-large"

NS_CASES = "cases"
NS_PROFILES = "profiles"

# ======================================================
# CASE CONFIG (RESEARCH TEMPLATE)
# ======================================================

CASE_ID = "PROTEX-XXX"

CASE_PROFILE = {
    "childhood": {
        "abuse_present": "unknown",
        "neglect_present": "unknown",
        "institutionalization": "unknown"
    },
    "modus_operandi": {
        "primary_control": "unknown",
        "weapon_used": "unknown",
        "planning_level": "unknown"
    },
    "victims": {
        "primary_gender": "unknown",
        "age_group": "unknown"
    },
    "temporal": {
        "offence_pattern": "unknown"
    }
}