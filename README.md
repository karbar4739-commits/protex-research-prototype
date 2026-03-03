# PROTEX  
**Controlled Hybrid Retrieval Architecture for Structured Case Analysis**

PROTEX is a research-oriented prototype implementing a controlled hybrid retrieval model designed for narrative-domain case analysis.

The system separates structured case profiles from narrative case chunks and enforces epistemic constraints during retrieval to reduce inferential drift and cross-case contamination in RAG pipelines.

---

## Research Motivation

Standard RAG pipelines treat all retrieved context as epistemically equivalent.  
In narrative and behavioural domains, this leads to:

- cross-case contamination  
- implicit inference inflation  
- uncontrolled abstraction  
- loss of provenance  

PROTEX introduces structural constraints to mitigate these failure modes.

---

## Core Design Principles

- Namespace separation (profiles vs narrative chunks)
- Deterministic metadata filtering before semantic retrieval
- Structured chunk roles
- Explicit confidence signalling
- Controlled failure modes

---

## System Components

- Case profile ingestion (structured, filterable metadata)
- Narrative chunk embedding and storage
- Intent-aware query routing
- Confidence model (high / inferred / unknown)

---

## Repository Scope

This repository contains:

- Research prototype implementation
- Ingestion templates (without real case data)
- Query engine example

This repository does NOT contain:

- Real case data
- Production deployment configuration
- Private implementation details

---

## Status

Active research prototype.  
Architecture and evaluation methodology under continuous development.
---

## Documentation
- Architecture: `docs/architecture.md`
- Query flow: `docs/query_flow.md`