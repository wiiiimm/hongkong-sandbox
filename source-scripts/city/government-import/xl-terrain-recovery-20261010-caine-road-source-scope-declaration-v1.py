"""Declare complete original Caine proof and unchanged historical negative evidence.

The existing disjoint-routing provenance contract classifies only exact unrelated
metadata pointers; original source/TIN/proposal/current drawn geometry stay numeric.
Root independently closes every transitive byte binding before any publication.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from original_disjoint_routing_metadata_scope_20261010 import boundaries,verify_boundaries
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-caine-road-source-scope-declaration-v1';ROLE=BASE/'government-xl-terrain-recovery-caine-road-current-complete-visual-role-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();typed=read(ROLE/'typed-role.json.gz');receipt=read(ROLE/'result.json');assert typed['currentTypedPhysicalAccepted'] and not typed['reasons'] and typed['completeOriginalFaces']==10947 and typed['completeOriginalComponents']==204 and typed['allCurrentRetainedNativeChecksPassed'] is True
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 dirs=sorted({d for pattern in ['*caine-road*','*unnamed-268032*'] for d in BASE.glob(pattern) if d.is_dir() and not any(x in d.name for x in ['typed-stage','installed','scope-declaration'])})
 paths={str(p.relative_to(ROOT)) for d in dirs for p in d.rglob('*') if p.is_file()}
 files={p for pattern in ['*caine_road*','*caine-road*','*unnamed-268032*'] for p in HERE.glob(pattern) if p.is_file() and not any(x in p.name for x in ['stage-install','live-install','scope-declaration'])}
 files.update(HERE/n for n in ['candidate_native_support_witness_v1_20261010.mjs','test_candidate_native_support_witness_v1_20261010.mjs','xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs','original_disjoint_routing_metadata_scope_20261010.py','test_original_disjoint_routing_metadata_scope_20261010.py']);files.add(Path(__file__));paths.update(str(p.relative_to(ROOT)) for p in files)
 prior=read(BASE/'xl-terrain-recovery-20261010-mei-yat-stage-live-closure-v1/closed-scope.json')
 aliases=list(prior['historicalManifestAliases']);leaf=set(prior['metadataLeafPaths']);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';raw=manifestpath.read_bytes();assert digest(raw)==typed['currentManifest']['sha256'];OUT.mkdir();archive=OUT/'acceptance-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)));leaf.add(str(archive.relative_to(ROOT)));manifest=read(archive)
 leaf.update('3d-viewer/'+u for u in manifest['officialModelCatalogues']);leaf.update('3d-viewer/'+e['url'] for e in manifest['terrainPatches']);pointers=[]
 for d in dirs:
  p=d/'current-source-terrain-preflight.json'
  if not p.is_file():continue
  pre=read(p)
  if 'completeCurrentTerrainRouting' not in pre:continue
  sha=pre['currentManifest']['sha256'];matches=[r for r in aliases if r['sha256']==sha];assert matches,'Exact historical manifest archive is required';original_manifest=read(ROOT/matches[0]['archive']['path']);assert digest((ROOT/matches[0]['archive']['path']).read_bytes())==sha
  for r in pre['completeCurrentTerrainRouting']:assert ref(ROOT/r['asset']['path'])==r['asset']
  declared=boundaries(pre,original_manifest);verify_boundaries(pre,original_manifest,declared);pointers.extend(dict(path=str(p.relative_to(ROOT)),documentSHA256=ref(p)['sha256'],boundary=b) for b in declared)
 save(OUT/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),metadataLeafJsonPointers=pointers,currentRoleNeon=receipt['jobId'],sourceGeometryChanges=0,terrainProposalChanged=True,stageAndLiveExcluded=True,qualification='Complete original and actual10947faces/204parts;202 genuinely rooted structural parts and two named source-bound mounted visual details supply no roots or bridges. All18 current forms and all10 retained native meshes checked;76-form expanded native scope independently reconstructed. All nine parent child meshes and grid byte-equal numerics; explicit foreign dyadic parent restoration proposal remains fully numerical. Original/TIN/root/streams/source/foundation/current/foreign/runtime and old failures fully recursive. Only existing reviewed global metadata and exact disjoint-routing acquisition pointers are nonrecursive. Root independent unchanged verifier required; no installed credit.'))
 print(dict(paths=len(paths),pointers=len(pointers),currentRoleNeon=receipt['jobId']),flush=True)
if __name__=='__main__':main()
