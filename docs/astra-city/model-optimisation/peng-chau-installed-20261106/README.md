# Peng Chau installed-model compression — HKS-229

Executor: Codex, 6 November 2026. Source commit `954b4c6eda356015ecbefbe22aec3075659657fb` on `feature/islands-model-enhancement-and-compression`.

**Current installed slice complete:** 22 enhanced Peng Chau models (21 newly installed original ports plus one existing original) have all four original/lossless, high, balanced and lightweight candidates: **88 complete / zero failed / 88 unreviewed / zero published**. Four exact previous variants were restored; 84 were generated locally. All variants passed independent decoder checks and exact Neon/file/receipt readback (176 artifact/receipt hashes). No AI geometry modelling or per-model AI calls.

This does **not** complete Peng Chau enhancement. The regional census contains 1,809 forms: 22 installed enhanced sources and 1,787 basic-only forms excluded from compression. There are 1,404 remaining selected original sources under investigation, including 300 private original-TIN candidates. User order remains Peng Chau enhancement/compression, then Cheung Chau; Tung Chung and the old XL campaign stay paused.

These meshes are already tiny: the 22 gzip originals total **37,083 bytes**. High and original/lossless candidates are all larger. One balanced candidate saves 17 bytes; three lightweight candidates save 441 bytes in total when retaining original bytes for larger candidates (**1.19%**). All outcomes remain indexed. Four tier labels do not guarantee four triangle counts or a runtime/FPS gain. Live serving still uses the original installed assets.

Frozen source snapshot SHA-256: `94d547acf1d5c257fcdc2692f39dcf0436975335263ad6812c64f2447d4e9610`. Final pinned Neon checkpoint `4e57b11bce3acd3217d615dd93fac8371a175cfb2672d9e1983d96c0e6c46e7f` was read back exactly. Original acquisition/installation review records and source geometry are unchanged by compression.

Portable committed bundle: `bundle/peng-chau-installed-20261106.tar.gz` (382,307 bytes), SHA-256 `8716285fb445b85cbe3599f7da8260015ac07a8cfec678cc184a690325cd98fa`. It contains all 110 unique original/candidate objects, 88 immutable processing receipts, source/variant indexes and recipes. Every archive member was read back byte-for-byte. Objects are named by compressed SHA-256 under `objects/`; use metadata source/variant hashes to resolve them. This is geometry/data, not a viewer/terrain package or a quality-approved runtime release.
