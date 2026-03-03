# PROTEX Architecture

## Overview
PROTEX is a controlled hybrid retrieval architecture for structured case analysis in narrative domains.  
It is designed to reduce inferential drift and cross-case contamination in retrieval-augmented systems by enforcing epistemic constraints during retrieval and context assembly.

## Design Goals
- **Boundary enforcement:** prevent mixing content across unrelated cases unless explicitly requested.
- **Provenance preservation:** retrieved content must retain origin context (case_id, section, role).
- **Epistemic layer separation:** structured profile facts vs narrative chunks are treated differently.
- **Controlled failure modes:** prefer “unknown / insufficient evidence” over speculative synthesis.
- **Auditability:** decisions should be reconstructable from metadata.

## Data Model
### 1) Case Profile (Structured, Filterable)
Stored in namespace: `profiles`  
Purpose: stable, metadata-filterable features for grouping and eligibility checks.

Typical metadata:
- `case_id`
- flattened keys such as `p_childhood_abuse_present`, `p_modus_operandi_weapon_used`, etc.

### 2) Case Chunks (Narrative / Sectioned)
Stored in namespace: `cases`  
Purpose: narrative fragments aligned to a controlled structure.

Typical metadata:
- `case_id`
- `section` (e.g., `case_description`)
- `section_group` (e.g., `context`, `interaction`)
- `chunk_role` (e.g., `behaviour_sequence`, `mo_signature`)
- `order`, `hash`
- `text` (content payload)

## Retrieval Pipeline
### Step A — Query intake
Input: user query + mode (single/multi), plus optional debug flag.

### Step B — Case boundary detection
- If mode = **single**, an explicit `CASE_ID` is required.
- If `CASE_ID` is present, retrieval is filtered to `case_id in {...}`.

### Step C — Semantic retrieval (within constraints)
- Query is embedded with the chosen embedding model.
- Vector retrieval runs in namespace `cases` with filters applied (case_id + optional routing constraints).

### Step D — Context assembly
- Results are grouped by `case_id`.
- Low-score matches are discarded via thresholds.
- Top-N chunks per case are assembled in ranked order.
- Each chunk is emitted with header metadata for auditability.

## Confidence Model (Current)
PROTEX outputs a coarse confidence label:
- **high:** explicit case boundary was used and matches were found
- **inferred:** semantic matches found without explicit boundary
- **unknown:** no reliable matches found

This model is intentionally conservative and can be refined into a calibrated uncertainty estimator.

## Failure Modes Addressed
- **Cross-case contamination:** prevented via case_id filtering (especially in single mode).
- **Narrative bias amplification:** reduced by forcing provenance-tagged context assembly.
- **Overconfident synthesis:** mitigated by explicit `unknown` outputs when evidence is insufficient.
- **Section drift:** reduced by routing via stable keys (`chunk_role`, `section_group`).

## Non-Goals (for this public repo)
- Publishing real case data
- Production-grade deployment configuration
- Full private evaluation suite and datasets

## Future Work
- Evaluation harness (precision/contamination metrics; naive-RAG baseline comparison)
- Expanded group-query parsing (safe structured query parser)
- Calibrated confidence scoring and uncertainty signalling
- Routing policy learning (supervised/weakly-supervised routing to chunk roles)