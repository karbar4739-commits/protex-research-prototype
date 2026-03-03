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

# ======================================================
# HELPERS
# ======================================================

def embed(text: str):
    return openai.embeddings.create(
        model=EMBED_MODEL,
        input=text
    ).data[0].embedding


def text_hash(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def flatten_profile(profile: Dict[str, Any], prefix: str = "p") -> Dict[str, Any]:
    flat = {}
    for k, v in profile.items():
        if isinstance(v, dict):
            nested = flatten_profile(v, prefix=f"{prefix}_{k}")
            flat.update(nested)
        else:
            flat[f"{prefix}_{k}"] = v
    return flat


def upsert_profile(case_id: str, profile: Dict[str, Any]):
    profile_id = f"{case_id}__profile"
    flat = flatten_profile(profile)

    profile_text = f"CASE_PROFILE for {case_id}: " + ", ".join(
        [f"{k}={v}" for k, v in flat.items()]
    )

    index.upsert(
        vectors=[{
            "id": profile_id,
            "values": embed(profile_text),
            "metadata": {
                "entity_type": "case_profile",
                "case_id": case_id,
                **flat
            }
        }],
        namespace=NS_PROFILES
    )

    print(f"✔ PROFILE INGESTED: {profile_id}")
    return profile_id


# ======================================================
# CHUNK INGESTION
# ======================================================

def upsert_chunk(
    case_id: str,
    profile_id: str,
    section: str,
    section_group: str,
    chunk_role: str,
    text: str,
    order: int,
):
    chunk_id = f"{case_id}__{section}__{order:02d}"

    index.upsert(
        vectors=[{
            "id": chunk_id,
            "values": embed(text),
            "metadata": {
                "entity_type": "case_chunk",
                "case_id": case_id,
                "profile_ref": profile_id,
                "section": section,
                "section_group": section_group,
                "chunk_role": chunk_role,
                "order": order,
                "hash": text_hash(text),
                "text": text,
            }
        }],
        namespace=NS_CASES
    )

    print(f"✔ CHUNK INGESTED: {chunk_id}")


# ======================================================
# EXECUTION ENTRY (TEMPLATE)
# ======================================================

if __name__ == "__main__":
    profile_id = upsert_profile(CASE_ID, CASE_PROFILE)

    example_text = """
    Example case description.
    Replace this with structured case data.
    """

    upsert_chunk(
        case_id=CASE_ID,
        profile_id=profile_id,
        section="case_description",
        section_group="narrative",
        chunk_role="case_summary",
        text=example_text.strip(),
        order=1,
    )

    print(f"\n=== INGEST COMPLETE — {CASE_ID} ===")