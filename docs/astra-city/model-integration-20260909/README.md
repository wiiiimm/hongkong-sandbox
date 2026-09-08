## Current checkpoint — Whampoa and further residential components

This pass now has **205 new native source components installed and verified**, plus **31 existing native components reviewed** in Neon snapshot `f61930a5e4dfa572` (538 tracked source components). The Whampoa is a separate user request outside the frozen213-landmark baseline; both ship/hull sources are installed. These counts do not claim whole-landmark or regional completion.

The latest root integration adds18 components: ten Island Resort/Pacifica/Wplace models, six Capitol models and two Whampoa ship/hull models. Po Lin Hall of Great Hero now retains its native podium during streaming. Actual browser checks passed with unchanged1× source geometry: source IDs, terrain agreement, collision/picking, desktop/mobile night, walk/fly, failure fallback/Retry.264 viewer tests and28 guarded-publisher tests pass.

Capitol's narrower terrain extension preserves all29,751 existing Club Galaxy grid nodes and excludes the conflicting LOHAS ancillary structure. Two null-survey canopy base estimates follow the new terrain; surveyed elevations remain unchanged. Festival City and the LOHAS ancillary conflict remain held explicitly. The Whampoa native hull/decks/masts are recognisable; exact paint, glazing, lettering and decorative night lighting are a separately recorded appearance refinement, not delivered textures.

Current evidence: `current-checkpoint.json`, `residual-ten-live/after/verification.json`, `whampoa-capitol-live/after/verification.json`, `polin-live/after/verification.json`, and `../whampoa-special/close-view/report.json`. Four new exact-name tower sources were acquired; two passed the conservative packer and two Cullinan sources retain geometric identity review. Civic, Grand Promenade and further source review continue without waiting for user approval.

# HKS-214 modelling integration — 9 September

Five West Kowloon cultural source parts are installed in the feature viewer. Native source bytes are unchanged; generic procedural windows are disabled on the opaque cultural envelopes. The exact M+ source podium supports the raised tower. `cultural/publication.json` records the manifest/asset change; `cultural-live/report.json` contains20 successful real-route views, native picking and desktop/mobile layout checks. Source approval: `../cultural-model-review/visual-acceptance.json`.

Neon records these five as installed-verified. This does not mean production/R2 publication or complete landmark/campus acceptance. Remaining model candidates and terrain corrections are in progress under HKS-214, owned by the agent. Root integrates shared files; workers retain isolated evidence and expiring source reservations.

Two ancillary parts (landsd/186982:0 and226248:0) are also installed with source TIN-derived terrain patches. Source elevations remain unchanged; the patches restore positive roof clearance and preserve22 neighbouring source building envelopes without new flags. `roof/publication.json`, `roof-live/report.json`, and `roof-acceptance.json` record integration and limitations. These are a substation and a tiny Creative Media Centre ancillary part, not the main landmark building.

Road surfaces now refine only on terrain at1m resolution or finer, following the final sampler with the existing18cm road offset. Six focused road/terrain tests pass. The three-tile check retains Central's105336 road vertices and finds positive fine-terrain triangle-centre clearance in the two corrected hillside tiles. Road/UV buffer costs in those tiles are3.06MB and6.23MB; this is not physical-mobile thermal validation. Existing overlapping paths and wider neighbouring assemblies remain outside the subset.

The grounded batch installs23 parts after48 candidate framing captures and23 successful installed-route checks. Pedder landsd/69002:0 is explicitly held: native top54.080m versus footprint43.8m and the documented historic form need reconciliation. `grounded-root-review.json` overrides its earlier source-only approval. All other proposed tourist memberships remain unapproved independently of exact source-part integration.

The support batch installs59 parts after118 normal/isolated captures and59 successful installed-route checks. Tower bases contact actual native or surveyed fallback podium triangles, with explicit dependency records. `support/publication.json` and `support-live/after/verification.json` record the installed result. Both installed batches passed source picking/collision, native terrain agreement, mobile-budget/layout, Walk/Fly and failed-asset recovery checks. Measured desktop median/p95 were16.7ms in both; emulated-mobile p95 was16.8ms, not a physical-device result.

Current checkpoint: **187 new native source components installed and verified**, plus **12 previously installed components reviewed**. Neon records199 installed-verified source components in snapshot `11a25ce297101f9e`; its529 source components include recovered supports and133 existing assets with exact hashes. This does not mean187 complete landmarks.

Additional batches:7 terrain-supported parts;9 exact-TIN/recovered identities;18 foundations/Peak;53 tower/podium components;9 coherent Chungking/LP6/Branksome additions;2 HKDI/Belcher components. Publication reports and actual viewer evidence are in the corresponding subdirectories. The53-part evidence deliberately retains the initially failed report:51 completed source checks plus the final two-camera-picking rerun form `assemblies-verification.json`.

West Kowloon Station required an explicit source-confirmed water-mask correction:10,782 masked nodes repaired within its official footprint/collar, including the west wing. All other old grid nodes are protected by a hash-pinned allowlist.104 staged terrain rays and final installed station route passed. Native model coordinates are unchanged.

Native TIN rendering and walking now share exact Float32 source faces. The Branksome overlap allowance is restricted to original source facets, with exact source hashes and highest-surface ray agreement. Native interior collision uses the local roof, eliminating95 false depot contacts while preserving100 target contacts and5 real overlaps. Conservative aircraft spawn/avoidance envelopes remain intentionally broad.

Source-proven metadata migrations keep towers and native podiums loaded together; Hermitage's990 rim vertices all contact its podium, so incidental tower-to-tower references were removed to prevent cycles. One IFC's existing tower now retains its native podium. A stable per-window seed removes fragment-level night-light speckle on curved/smoothed native faces.

Validation:264 viewer unit tests and22 publisher tests pass. Neon source-version inheritance preserves decisions only for unchanged source identities. Desktop/emulated-mobile viewer samples, source identity, picking, local collision, terrain agreement, Walk/Fly and failed-load recovery are recorded per batch; emulation is not physical-phone validation.

Remaining candidate/identity/terrain reviews are agent-owned and continue in parallel. Pedder's source-height conflict and exact source absences are held explicitly. None of this checkpoint claims production deployment, photorealistic façades, or whole-landmark/component closure.
