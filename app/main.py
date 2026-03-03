from fastapi import FastAPI
from pydantic import BaseModel
from pinecone import Pinecone
from openai import OpenAI
from collections import defaultdict
import os
import re
from typing import Literal, List, Dict, Any

# ======================================================
# CONFIG
# ======================================================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "protex")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
openai = OpenAI(api_key=OPENAI_API_KEY)

EMBED_MODEL = "text-embedding-3-large"

NS_CASES = "cases"
NS_PROFILES = "profiles"

SINGLE_THRESHOLD = 0.10
MULTI_THRESHOLD = 0.20

app = FastAPI()

# ======================================================
# REQUEST MODEL
# ======================================================

class QueryRequest(BaseModel):
    query: str
    analysis_mode: Literal["single", "multi"] = "single"
    top_k: int = 30
    debug: bool = False

# ======================================================
# HELPERS
# ======================================================

CASE_REGEX = re.compile(r"PROTEX\s*[-–]?\s*([A-Z0-9]{2,})", re.IGNORECASE)

def extract_case_ids(text: str) -> List[str]:
    return [f"PROTEX-{m.upper()}" for m in CASE_REGEX.findall(text)]

def embed(text: str):
    return openai.embeddings.create(
        model=EMBED_MODEL,
        input=text
    ).data[0].embedding

def determine_confidence(
    used_case_id: bool,
    matches_found: bool
) -> str:
    if used_case_id and matches_found:
        return "high"
    if matches_found:
        return "inferred"
    return "unknown"

# ======================================================
# ROOT
# ======================================================

@app.get("/")
def root():
    return {
        "system": "PROTEX Research Prototype",
        "architecture": "Controlled Hybrid Retrieval",
        "status": "active"
    }

# ======================================================
# QUERY ENDPOINT
# ======================================================

@app.post("/query")
def query_protex(data: QueryRequest):

    requested_cases = extract_case_ids(data.query)

    if data.analysis_mode == "single" and not requested_cases:
        return {
            "status": "error",
            "reason": "Single mode requires explicit CASE_ID (e.g. PROTEX-012)."
        }

    threshold = SINGLE_THRESHOLD if data.analysis_mode == "single" else MULTI_THRESHOLD

    vector = embed(data.query.strip())

    pinecone_filter = {}
    if requested_cases:
        pinecone_filter["case_id"] = {"$in": requested_cases}

    results = index.query(
        vector=vector,
        top_k=data.top_k,
        include_metadata=True,
        filter=pinecone_filter if pinecone_filter else None,
        namespace=NS_CASES
    )

    grouped: Dict[str, List[dict]] = defaultdict(list)

    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        score = match.get("score", 0.0)

        if score < threshold:
            continue

        cid = meta.get("case_id", "UNKNOWN")
        grouped[cid].append({
            "section": meta.get("section"),
            "chunk_role": meta.get("chunk_role"),
            "content": meta.get("text"),
            "score": score
        })

    confidence = determine_confidence(
        used_case_id=bool(requested_cases),
        matches_found=bool(grouped)
    )

    if not grouped:
        return {
            "status": "ok",
            "confidence": "unknown",
            "kbContext": None
        }

    final_context = []

    for cid, chunks in grouped.items():
        chunks.sort(key=lambda x: -x["score"])
        for c in chunks[:8]:
            header = f"### CASE {cid} | {c['section']} | {c['chunk_role']} ###"
            final_context.append(f"{header}\n{c['content']}")

    return {
        "status": "ok",
        "confidence": confidence,
        "kbContext": "\n\n---\n\n".join(final_context)
    }