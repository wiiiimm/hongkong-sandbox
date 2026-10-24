# Main Block capture compatibility - 25 October 2026

Diagnostic only: original model `landsd/280350:0`, 13,121 faces, no installation or approval transfer.

The current authenticated capture omitted the older `originalGeometryOnly` field required by the terrain replacement producer. The compatibility producer reconstructs the canonical entry from the exact pinned native record and current source form, requires exact metadata equality apart from the local asset URL, verifies source bytes, and replays the production loader. All geometry and drawn-ground rows must equal the previous capture exactly; all production input hashes must match except the explicitly rebound selection file. An explicitly false original flag is rejected.

Neon receipt: `77f9c248ad19166902346c409c9f4028592fa44aee78dd847580fbfca6df69f5`.

Six adversarial unit tests pass, including altered placement, added transforms/approval, changed identity, triangle counts and asset digests.

The first compatibility attempt compared complete replay documents, which necessarily include different selection paths. Its geometry rows were identical. V2 explicitly binds both selection hashes and requires equality of every other input hash. Its failed local output remains preserved; no acceptance was granted.

The subsequent unchanged V4 terrain producer progressed beyond schema validation but rejected a parent triangle crossing the domain. That is a capture-script limitation, separately recorded in replacement-v2. The additive V5 producer uses existing V2 3D parent clipping and the established V11 template/unchanged-low-parent proof; all source-height, area, coverage, overlap, boundary and 25,000-face limits remain in force.
