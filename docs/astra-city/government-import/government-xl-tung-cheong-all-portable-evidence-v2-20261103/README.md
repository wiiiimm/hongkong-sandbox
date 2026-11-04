# Exact original-model evidence transport

`restore-map.json` binds the completed private diagnostic receipts to exact original payloads. It reuses the prior V1 archive by SHA and stores only supplemental payloads here. This is archival transport, not model simplification, runtime compression variants or approval.

For a missing declared path: verify archiveSHA256, gzip-decompress, verify originalSHA256 and originalBytes, then restore that path. Refuse an existing file with different bytes. Never write any unlisted or public/runtime path. Source receipts remain authoritative for the scope and acceptance limitations of each diagnostic. `capture-referenced-payloads.py` documents archive construction and verifies every round trip; do not rerun completed model processing.

Large frozen evidence JSON files are deliberately stored as exact byte archives. The raw local files were left untouched; all original source, production module, terrain and image hashes remain unchanged. Newer current-route metadata and small evidence files are committed directly alongside these archives.
