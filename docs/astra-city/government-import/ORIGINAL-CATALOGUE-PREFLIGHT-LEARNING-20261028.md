# Original catalogue preflight

A source-form match and successful source geometry capture do not prove the production catalogue can load. The Elegant Garden full-scene preview exposed 13 entries without required `sourceTile`, causing the entire catalogue to be rejected before any new model loaded. These were metadata omissions, not corrupt meshes.

Before browser work, run the actual `prepareModelCatalogue` validator and verify all original asset bytes/hashes. Resolve missing source sheets only through the pinned native-stage cache key and unchanged result hash. Verify UID, model ID and asset hash against that exact cached model. Reject conflicting existing sheets; do not guess from coordinates or names. Several models may share a cache key, so compare unique key sets rather than model counts.

Use `original_catalogue_source_sheets_v1_20261028.py` and `private_original_catalogue_preflight_v1_20261028.mjs`. This supplies provenance metadata only. It grants no identity, placement, geometry, optimisation or publication approval. Preserve failed preview receipts and original bytes. Capture and reverify the actual viewer dependency closure around the corrected browser run.
