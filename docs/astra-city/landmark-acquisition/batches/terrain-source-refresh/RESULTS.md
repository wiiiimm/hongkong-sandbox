# HKS-213 / HKS-214 · Refreshed 15-NW-3B source

The official archive changed from ETag `"30b4b2f-6598a4674b837"` to `"30b4b9c-65a904a99c060"`. Native terrain CRC and byte sizes are unchanged; archive member offsets changed. `refresh-input.json` pins the current complete-directory hash, exact member offsets, HEAD provenance and the old/new ETags. The previous batch input remains untouched.

One sheet and its two native glTF/bin members were acquired and verified using 8,096,209 response bytes (one HEAD and two bounded ranges). The existing decoder staged geometry-only terrain with native 1× HKPD coordinates and unchanged binary geometry. Independent verification passed; resume transferred zero bytes and made no further requests. The source photograph was omitted, and no terrain was applied or published.

This checkpoint resolves the source-revision hold for 15-NW-3B in `terrain-final-increment`. Standard compact ZIP and staged terrain manifests are discoverable by preflight. Executor: Codex acquisition agent.
