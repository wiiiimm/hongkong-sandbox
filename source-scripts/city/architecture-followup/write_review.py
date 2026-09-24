"""Write compact review evidence for the bounded HKS-209 local pass."""
import hashlib,json,pathlib
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];D=R/'docs/astra-city/architecture-followup';B=H.parent/'architecture-batch'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
r=read(H/'bulk-report.json');v=read(H/'compact/validation.json');c=read(H/'compact/catalogue.json');a=read(B/'acceptance.json');p=read(B/'report.json');expected=set(a['held'])|{x['uid']for x in p['results']if x['outcome']=='no-standard-match-in-cache'};actual={x['uid']for x in r['rows']};assert len(actual)==16 and actual==expected
for path,digest in r['inputHashes'].items():assert sha(R/path)==digest,path
ready={x['uid']for x in r['rows']if x['outcome']=='ready'};assert ready=={x['uid']for x in c['models']}=={x['uid']for x in v['results']};assert v['exceptions']==0 and v['checksPassed']==3 and not v['concerns']
records=read(H/'input-records.json')['targets']
for m in c['models']:
 b=records[m['uid']];assert m['objectId']==b['object_id'] and m['buildingCSUID']==b['csuid'];assert m['recordedBaseHeight']==b['source_base'] and m['recordedTopHeight']==b['source_top'];asset=H/'compact'/m['asset'];assert asset.stat().st_size==m['bytes']and sha(asset)==m['sha256']
verification={'issue':'HKS-209','scopeUidsExactlyMatched':True,'accountedParts':16,'readyCandidates':sorted(ready),'allInputHashesCurrent':True,'nativeSourceIdentityAndSurveyHeightsRetained':True,'assetChecksumsAndSizesPassed':True,'loaderPassed':3,'loaderExceptions':0,'loaderTerrainConcerns':{},'compressedCandidateBytes':sum(m['bytes']for m in c['models']),'queueSha256':sha(H/'queue.json'),'catalogueSha256':sha(H/'compact/catalogue.json'),'qualification':'No GPU/browser architecture acceptance or live publication. Ready is a processing stage only.'};save(H/'verification.json',verification);save(D/'verification.json',verification);save(D/'candidate-validation.json',v);save(D/'staged-catalogue.json',c);save(D/'queue.json',read(H/'queue.json'))
notes={
'landsd/3089:0':'Fresh current-footprint match passes unchanged thresholds; shared loader/terrain checks pass.',
'landsd/3090:0':'Fresh current-footprint match passes unchanged thresholds; shared loader/terrain checks pass.',
'landsd/4314:0':'Miller Theater: refreshed exact source match and loader/terrain checks pass.',
'landsd/70574:0':'Nearby native building covers99.4% horizontally, but none of131rays reaches the estimated canopy band; insufficient canopy proof.',
'landsd/91009:0':'Related native roof covers88.7%;40/47rays hit, only31reach the estimated height band. Keep unmatched remainder/fallback.',
'landsd/114964:0':'Current retaining-edge burial remains. Prior high-cost0.25m grid is not accepted; retain source heights.',
'landsd/143421:0':'Exact GeoRef but zero actual footprint overlap;6.37m centroid gap. No coordinate shift or threshold relaxation.',
'landsd/223348:0':'Native upper component remains about7m above ground with no identified support; retain full-height fallback.',
'landsd/223783:0':'Adjacent native model covers only7.8% (one of11rays); downhill support remains unresolved.',
'landsd/242698:0':'No standalone exact member in the checked complete11-SW-8Ddirectory (2,428entries).',
'landsd/246271:0':'Main Peak model covers99.96%;19/22rays reach estimated band. Needs main-model placement and architectural confirmation.',
'landsd/246272:0':'Main Peak model covers100%;only6/28rays reach estimated band. Height/component correspondence remains unresolved.',
'landsd/248218:0':'Cached5m DTM trial worsens lowest-vertex burial to16.67–20.05m and introduces neighbour flags; rejected.',
'landsd/322573:0':'Cached5m/native-TIN trial improves median contact to−0.12m, but residual corner gaps and full-patch/browser review remain; held.',
'landsd/324948:0':'No exact source member in prior bounded complete-directory review; retain surveyed-height baseline.',
'landsd/330467:0':'Current retaining edge leaves3–4m gap; prior58,081vertex trial still~1m gap. Lower-cost edge solution remains pending.'}
text=f'''# HKS-209: cache-only bulk processing of all 16 flagged parts

All **16 requested source parts** are accounted for: **3 staged and validated candidates, 11 held, 2 missing from the reviewed retained sources**. No live building, terrain, source coordinates or shared inventory records were changed. All native geometry remains at 1× HKPD.

“Ready” means ready for the next browser review, not published or architecturally accepted. The three candidates total **{v['compressedBytes']:,} compressed bytes**. Shared loader, source-surface picking/collision and terrain checks pass for all three with zero exceptions and zero sampled terrain concerns. Actual browser review remains with the root task.

The three resolved match failures were stale cached footprint-selection matches: current source footprints match the original geometry at the existing ≥50% smaller-footprint overlap and ≤10 m centroid thresholds. The thresholds were not relaxed; source geometry was not shifted. Original source hashes and refreshed matching evidence are retained.

## Per-building disposition

| Source UID | Building / part | Processing state | Evidence and next action |
|---|---|---|---|
'''
for row in r['rows']:text+=f"| {row['uid']} | {row['name']} | {row['outcome']} | {notes[row['uid']]} |\n"
text+=f'''
## Cost and reusable tooling

The final bulk pass took **{r['scriptSeconds']:.3f} seconds**, inspected **{r['cachedManifestsInspected']} cached manifests**, and verified/read **{r['sourceFilesRead']} native payload files totalling {r['sourceBytesRead']:,} bytes**. That byte count excludes metadata reads and the separate terrain experiment. Network requests, downloaded bytes and AI calls inside the scripts were all **zero**.

The pass reuses the existing `cached_models.Processor`, original model decoder/packer, indexed-triangle evidence helper and read-only SQLite inventory. Individual failures become explicit retry entries rather than abandoning the remaining records. Candidate assets are checksum-addressed and reruns reuse identical output bytes.

The separate cached terrain experiment reuses the established 5 m DTM builder and native-TIN mosaic. **Both terrain outputs remain held.** Opus still needs broader neighbour and browser checks; Peak's DTM proposal increases burial and is unsuitable. The earlier high-cost Tai Kwun terrain candidate is also excluded. No source was moved to conceal a terrain problem.

## Reproduce

From the Astra worktree, using the existing local runtimes:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-followup/bulk_pass.py
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/architecture-followup/compact --out source-scripts/city/architecture-followup/compact/validation.json
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-followup/terrain_pass.py
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-followup/write_review.py
```

- `bulk-report.json`: per-UID source identity, exact geometry/support evidence and input hashes.
- `queue.json`: one next action for each of the 16 parts.
- `candidate-validation.json` and `verification.json`: source identity, checksum, loader and complete-scope checks.
- `terrain-report.json`: held Opus and rejected Peak terrain experiments with explicit limitations.
- Staged model assets remain in `source-scripts/city/architecture-followup/compact/`.

Cache/directory absence is limited to the listed source revisions; it does not establish dataset-wide unavailability. No fresh downloads were made. Further source acquisition, retaining-edge work or source-component correspondence review should be bounded follow-ups. HKS-209 remains In Progress; only the three validated candidates can proceed to visual review now.
'''
# Readable spacing in generated evidence; leave stable identifiers intact.
for old,new in {'covers99.4%':'covers 99.4%','of131rays':'of 131 rays','covers88.7%':'covers 88.7%','only31reach':'only 31 reach','high-cost0.25m':'high-cost 0.25 m',';6.37m':'; 6.37 m','about7m':'about 7 m','only7.8%':'only 7.8%','of11rays':'of 11 rays','complete11-SW-8Ddirectory':'complete 11-SW-8D directory','2,428entries':'2,428 entries','covers99.96%':'covers 99.96%',';19/22rays':'; 19/22 rays','covers100%':'covers 100%',';only6/28rays':'; only 6/28 rays','Cached5m':'Cached 5 m','Cached5m/native-TIN':'Cached 5 m/native-TIN','to16.67–20.05m':'to 16.67–20.05 m','to−0.12m':'to −0.12 m','leaves3–4m':'leaves 3–4 m','prior58,081vertex':'prior 58,081-vertex','still~1m':'still about 1 m'}.items():text=text.replace(old,new)
(D/'README.md').write_text(text);print(json.dumps(verification,indent=2))
