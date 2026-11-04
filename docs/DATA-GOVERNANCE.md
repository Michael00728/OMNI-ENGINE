# Data and Regulatory Knowledge Governance

## Source classes
- Statute
- Regulation
- Court decision
- Agency guidance
- Enforcement action
- Educational material
- Industry standard

Each record separately labels legal force as binding, non-binding, interpretive, not applicable, or unassessed. These labels are metadata and do not replace legal analysis.

## Source lifecycle
1. Identify the issuing authority and canonical source.
2. Retrieve the source over HTTPS and record retrieval time.
3. Preserve the original artifact and calculate a SHA-256 digest.
4. Extract text while retaining page, section, table, and paragraph locators.
5. Classify authority, jurisdiction, publication date, effective date, and status.
6. Review extraction and classification quality before indexing.
7. Detect updates and retain prior versions; never silently overwrite historical material.
8. Cite the exact version and passage used in downstream analysis.

A source URL or digest alone does not prove authenticity, legal applicability, or factual correctness. Keep original artifacts, extraction output, reviewer decisions, and derived findings linked by stable identifiers.

## Privacy rules
Do not ingest real consumer data into this foundation environment. Later ingestion must enforce consent and purpose limitation, minimize identifiers, mask or tokenize sensitive fields, encrypt protected data, restrict access by tenant and role, and apply documented retention and deletion controls.
