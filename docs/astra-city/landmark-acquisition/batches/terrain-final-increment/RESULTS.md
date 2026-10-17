# HKS-213 / HKS-214 · Final terrain increment

The final 273-model candidate inventory required 24 additional native terrain sheets for 118 flagged model parts. The pinned inventory hash and complete native member metadata are retained in the batch input.

**23 sheets were acquired and verified in this batch; the remaining sheet is acquired and verified in `terrain-source-refresh`. Together all 24 required sheets are available.** This batch transferred 66,256,133 bytes, including the newly fetched directory for the changed source. No monolithic source archive, photograph, whole-HK DTM, terrain application or geometric correction was performed.

`15-NW-3B` had been repacked under a new official ETag. Its terrain member CRC and decoded/compressed sizes were unchanged, but ZIP header offsets moved. The pinned metadata guard rejected the stale offsets. This batch retains that source-revision hold rather than rewriting its input. The separately pinned `terrain-source-refresh` batch records current HEAD provenance, full-directory proof and the successful native files. Its 8,096,209 bytes bring this final increment to 74,352,342 response bytes in total.

The 23 retained sheets pass complete-directory, CRC/length, source cache SHA-256, native binary, derived glTF and native 1× HKPD checks. `terrain-verification.json` intentionally still records the unacquired old-revision sheet; the follow-up report supplies its verified replacement. Ten acquisition regressions pass, including partial multi-sheet completion and missing-sheet verifier failures. Existing original/model checkpoint reports were not rewritten.

Executor: Codex acquisition agent. No maps were used, and no modelling, placement approval or publication was performed. The final preflight inventory should discover all 24 manifests across both batches.
