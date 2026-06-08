# Decisions

## Evidence is read-only

`worldline.inspect_run_evidence` is a read-only inspect tool. It does not compile documents, update graph data, or write DB records.

## Use existing fixture shape

The frontend already carries EvidenceAnchor and SourceAsset metadata under `evidenceRefs`. The run ledger stores that shape compatibly instead of inventing a new schema.

## Source lookup is evidence-backed

Source reads are resolved through evidence records and their `sourceRef`, keeping SourceAsset access tied to EvidenceAnchor provenance.
