# Miami Beach Towers 2 and 5: acceptance-ready original source stage

Agent: Codex identity investigation, 9 October 2026. This is a separate immutable staging checkpoint; no live publication or installation credit.

The complete unchanged original government assets for `landsd/202994:0` (Tower 2, 4,899 faces) and `landsd/203433:0` (Tower 5, 2,412 faces) pass the source-specific identity route, complete current native terrain/foundation, original ground contact, mobile runtime budgets, and all 18 physical neighbour rows (the two candidates plus 16 other actors). Physical receipt `d75a4c0ec6d0bf7641f963d41e4a761cc32eded1eab84b99dca37a76b0ec67bb`; explicit related-podium identity receipt `328fbc173f56b5cd0626a231e4e287708f3f5d9b510c8896b7cd4657903cd711`.

Original source SHA-256 values are `a91185beb3c7fb4451f889830fce52cc1d7a11b8ce3e29c0216b3e1be2152d3a` and `38d596b0bc390027b9dd68b379344df3459acc43ceac1df10c7fc78133904d50`. Original authored yaw, all nodes, all vertices and all faces are retained. AI was used to interpret evidence and write code; no AI geometry modelling, source edits or simplification occurred.

The independently identified original Miami podium is the sole explicitly related actor. Its current basic model `landsd/232089:0` remains loaded and visible. All other actors remain ordinary foreign actors, including shared-name and shared-permit buildings. The exact full-current-renderer diagnostic compares all 744 podium triangles against every original tower face using unpadded broad phase and rational narrow phase. It preserves all 252 Tower 2 and 249 Tower 5 line contacts, with no point-only or coplanar area contacts. These interfaces do not create any load-bearing or collision exemption. Full exact contact coordinates and original/current face IDs are in `basic-podium-exact-original-contacts.json.gz`.

The first legacy browser run passed all four desktop views and mobile Tower 2 failed-download fallback/retry, then failed whole-source camera framing after the mobile viewport settled. That failure and its exports remain in `browser-v1-failure/`. A separate scoped browser harness refits the actual complete loaded group after the viewport settles, keeps strict loader-range and full-framing assertions, and disables camera damping only inside the browser test. It changes neither runtime code nor any model. The replacement run in `browser-v2/` passes all eight desktop/mobile day/night views, both forced 503 fallback/retry cases, picking, collision, source visibility, full bounds, no horizontal overflow and drawn-ground/sampler parity (maximum 4 mm allowed). The basic podium remains visible in every view. All eight exported PNGs were independently opened by the identity agent. Current neighbours can obscure portions of the model in an ordinary city view; no neighbour was hidden to improve an export.

The reserved existing publisher dry run passed and left the live manifest unchanged. Stage review flags intentionally keep `publicationApproved=false`; root independently reviews the exports and contact evidence before creating its final serial installation copy. The handoff replay validates every upstream receipt reference SHA, exact original assets/current forms, fresh identity, browser assertions, and the unchanged current manifest `7de92c4dada1917ab6e37271d84f6134bd2517393f7156614d39530db35fbc03`. Any later manifest change requires a fresh current physical/publication binding.

Reproduce the diagnostic and browser check:

```sh
node source-scripts/city/government-import/xl-miami-two-basic-podium-contact-inputs-20261009.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-miami-two-basic-podium-exact-contacts-20261009.py
node source-scripts/city/government-import/xl-miami-two-staged-browser-20261009.mjs staged source-scripts/city/government-import/accepted/government-xl-miami-two-original-staged-20261009/browser-config-v2.json
```

These reproduction commands must write to a fresh stage after this checkpoint is frozen. The frozen records and source helpers are immutable. Parent owns guarded live installation, live browser acceptance and commits.
