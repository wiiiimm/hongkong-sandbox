"""Close Festival Walk unchanged-source numeric proof and immutable recovery lineage."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from original_disjoint_routing_metadata_scope_20261010 import boundaries,verify_boundaries
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-source-closed-scope-v1';OUT=BASE/BATCH
ROLE=BASE/'government-xl-terrain-recovery-festival-pair-current-typed-visual-role-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();typed=read(ROLE/'typed-role.json.gz');receipt=read(ROLE/'result.json');assert typed['currentTypedPhysicalAccepted'] and not typed['reasons'] and typed['completeOriginalFaces']==35006 and typed['completeOriginalComponents']==279
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 # Each complete source checkpoint is immutable. Superseded causal failures are
 # retained; browser stage/live are separately closed after their actual results.
 dirs=[d for d in sorted(BASE.glob('*festival*')) if '20261010' in d.name and (d/'result.json').is_file() and not any(s in d.name for s in ['typed-stage','atomic-installed'])]
 paths={str(p.relative_to(ROOT)) for d in dirs for p in d.rglob('*') if p.is_file()}
 names=[p for p in HERE.glob('*festival*20261010*') if p.is_file()]+[p for p in HERE.glob('xl-terrain-recovery-20261010-festival*') if p.is_file()]
 names=[p for p in names if not any(s in p.name for s in ['two-stage-install','two-live-install','source-closed-scope'])]
 names.extend(HERE/n for n in ['exact_original_edge_finite_facade_distance_band_v2_20261010.py','test_exact_original_edge_finite_facade_distance_band_v2_20261010.py','candidate_native_support_witness_v1_20261010.mjs','test_candidate_native_support_witness_v1_20261010.mjs','xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs','original_disjoint_routing_metadata_scope_20261010.py'])
 paths.update(str(p.relative_to(ROOT)) for p in names);paths.add(str(Path(__file__).relative_to(ROOT)))
 prior=read(BASE/'xl-terrain-recovery-20261010-ching-hin-stage-live-closure-v1/closed-scope.json');aliases=list(prior['historicalManifestAliases']);leaf=set(prior['metadataLeafPaths']);current=ROOT/'3d-viewer/city/data/manifest.json';raw=current.read_bytes();assert digest(raw)==typed['currentManifest']['sha256'];OUT.mkdir();archive=OUT/'acceptance-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)));leaf.add(str(archive.relative_to(ROOT)));manifest=read(archive)
 leaf.update('3d-viewer/'+u for u in manifest['officialModelCatalogues']);leaf.update('3d-viewer/'+e['url'] for e in manifest['terrainPatches'])
 pointers=[]
 for d in dirs:
  p=d/'current-source-terrain-preflight.json'
  if not p.is_file():continue
  pre=read(p)
  if 'completeCurrentTerrainRouting' not in pre:continue
  assert pre['currentManifest']['sha256']==digest(raw)
  for r in pre['completeCurrentTerrainRouting']:assert ref(ROOT/r['asset']['path'])==r['asset'],'Full actual routing asset must be byte-bound'
  declared=boundaries(pre,manifest);verify_boundaries(pre,manifest,declared);pointers.extend(dict(path=str(p.relative_to(ROOT)),documentSHA256=ref(p)['sha256'],boundary=b) for b in declared)
 save(OUT/'closed-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),metadataLeafJsonPointers=pointers,currentRoleNeon=receipt['jobId'],sourceGeometryChanges=0,terrainProposalChanged=True,stageAndLiveExcluded=True,qualification='All35006 original and actual rendered faces retain complete finite ordinary clearance;279 components are fully partitioned,241 original positive-dimensional contacts and nine genuine unchanged-band ground roots support231 structural components,48 bounded original visual details contribute zero ground roots or bridges. All91 current forms and both provider/root/streams/native memberships/identities/foundations/runtime gates remain recursive numeric proof. Current disjoint routing assets/global catalogues are byte-bound metadata, with complete bounds replayed; only their unrelated archived acquisition provenance is nonrecursive. Original TIN,21 complete restored finite facets,25 finite hulls,15041-face actual proposal, current drawn ground and441 independent sampler/ray probes remain recursive numeric inputs. Historical failures/proposed runtime copies preserved. No installed credit.'))
 print(dict(paths=len(paths),pointers=len(pointers),currentRoleNeon=receipt['jobId']),flush=True)
if __name__=='__main__':main()
