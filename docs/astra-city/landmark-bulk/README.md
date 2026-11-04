# Retained-cache landmark bulk preparation — HKS-211

All registry entries accounted; staged preparation only. No landmark/region or publication approval.

All 213 registry entries were processed. 304 unique identified source parts; 25 staged candidates. Zero downloads and zero published replacements.

Entry status takes the most restrictive remaining component state; part counts preserve mixed progress. Already detailed means a reference exists, not architectural approval. Historical interiors retain unverified host identities. Name token normalisation never assigns coordinates, expands tower ranges or changes source heights. Same-name sites more than 1 km apart remain ambiguous. Cache absence describes retained staged inputs, not government availability. All 16 HKS-209 queue items and the prior Ngong Ping pagoda hold remain unapproved. Two separate infrastructure/landscape targets are reported outside the 213-entry denominator.

| State | Entries |
|---|---:|
| already-detailed | 17 |
| ambiguous | 3 |
| cache-absent | 59 |
| candidates-staged | 9 |
| known-placement-holds | 7 |
| no-identity | 115 |
| nonbuilding-scope | 3 |

## Reproduce / resume

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-bulk/process.py run
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/landmark-bulk/compact --out source-scripts/city/landmark-bulk/compact/validation.json
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-bulk/process.py report
```

Source matching, decoding, exact packing and resumable SQLite jobs reuse building-batch code. Native 1× geometry, source hashes and HKPD are retained. The script reserves 8 MiB of the 128 MiB output ceiling for reports. Resource/failed/deferred jobs remain explicit and are never accepted implicitly. Browser placement and source-component review precede any publication.
