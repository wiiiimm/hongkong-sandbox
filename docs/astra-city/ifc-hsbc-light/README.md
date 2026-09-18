# IFC and HSBC light trial — HKS-227

Reuses five existing exact-ID native source models; no downloads, main-map replacement, source-height changes or new high-model acceptance. Both IFC towers and their two retained podium components form the IFC study. HSBC uses its existing Main Building component. This is not an exhaustive IFC shopping-centre/campus claim.

The existing deterministic one-metre vertex-clustering script generates the light variants and protects the upper20%of model elevation. Shared neutral comparison materials make the geometry differences visible. Small supports, facade elements and sharp edges can simplify; these light meshes remain comparison-only until a separate placement/architecture pass accepts them. No new photographic textures.

| Study | Components | Native gzip bytes | Light gzip bytes | Native triangles | Light triangles |
|---|---:|---:|---:|---:|---:|
| IFC |4|1,807,660|605,254|81,727|47,034|
| HSBC |1|4,678,280|738,903|177,857|57,078|

IFC payload is66.5%smaller; HSBC84.2%smaller. Maximum clustered vertex displacement: IFC1.118m, HSBC1.043m. These measurements describe the isolated trial, not visual equivalence or live-map performance.

Source manifests: `city/data/official-models/central/catalogue.json` and `landmark-pass/catalogue.json`. Model UIDs and source/light checksums are retained in the comparison manifest and `source-review.json`. IFC sources are dated21December2025; HSBC27August2026. Existing government source attribution applies. The original high models are unchanged.

Reproduce with `python source-scripts/city/whampoa-light-trial/generate.py`, which includes `source-scripts/city/ifc-hsbc-light/targets.json`. Requires the existing local building inventory and committed native assets. No AI calls are made during generation. Prior basic/light assets remain deterministic; UI-only metadata hashes may change. Run `node source-scripts/city/ifc-hsbc-light/verify.mjs` for all seven locations at1440/390px; screenshots and `verification.json` are recorded here. Physical mobile hardware is not tested.

`register.py --receipt PRIVATE_RECEIPT --commit SHA` records only these five light revisions, using the existing reservation-fenced Neon ledger. Geometry method islightweight; AI execution and reasoning arenot applicable to deterministic generation, matching the earlier light trial. Model reasoning used to author/review the script is not presented as measured per-model token use. Earlier revisions and the main installation snapshot remain intact. Runtime trial files are included in the feature PR, not separately published to production R2.
