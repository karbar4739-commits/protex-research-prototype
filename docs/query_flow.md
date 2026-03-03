# Query Flow

## High-level flow

```text
User Query
   |
   v
Intent + Boundary Detection
   |-- if single-mode and no CASE_ID -> ERROR
   |
   v
(Optional) Routing Constraints
(chunk_role / section_group filters)
   |
   v
Embed Query
   |
   v
Vector Search (namespace = cases)
 + metadata filters (case_id, routing)
   |
   v
Thresholding + Grouping by case_id
   |
   v
Context Assembly (top chunks per case)
   |
   v
Confidence Label + Response

## Notes
	•	The pipeline is designed to remain auditable: each output chunk retains provenance metadata.
	•	The architecture prefers conservative outputs (“unknown”) over speculative synthesis