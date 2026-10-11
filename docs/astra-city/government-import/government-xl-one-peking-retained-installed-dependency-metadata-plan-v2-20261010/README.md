Exact retained dependency metadata proposal (not applied)

All four exact current actors/supports are uniquely present in the current catalogues and have matching viewer UID/CSUID/objectID/type-to-original identifiers, byte hashes, complete original world/stream/root records and installed-verified Neon readbacks in snapshot ee1a41d61d2de0fe. Current manifest is 3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8.

Only263590→232907 and268032→101781 dependency state changes candidate→installed are proposed. Only263590's missing exact CSUID is added. All source bytes, original pose, all other catalogue fields and dependency edges remain unchanged.11 actual/adverse helper tests pass. Parent independently passed the same11 tests. Root must recheck all current provenance before serialized metadata publication; the proposal provides zero new geometry/physical/model credit.

The unfenced v1 producer stopped because Caine catalogue entries omit structureType. V2 verifies exact current viewer type and original01/T or02/P ModelID/CSUID conventions, without adding any type metadata. All failed producer facts remain preserved.

Historical actual-live fixture test remains unchanged at its original path, with a byte-identical archive named archived_retained_installed_dependency_pre_correction_tests_20261010.py. Future test discovery must use hermetic test_retained_installed_dependency_metadata_plan_v2_20261010.py; it verifies the frozen before-fixture SHA from the plan receipt. The historical test only applies before dependency correction and is not a post-correction gate.
