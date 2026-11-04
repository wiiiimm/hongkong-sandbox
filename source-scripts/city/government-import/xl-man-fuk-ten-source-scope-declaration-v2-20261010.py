"""Declare complete original Man Fuk proof and unchanged historical negative evidence.

The existing disjoint-routing provenance contract classifies only exact unrelated
metadata pointers; original source/TIN/proposal/current drawn geometry stay numeric.
Root independently closes every transitive byte binding before any publication.
"""
from pathlib import Path
import ast
from run import ROOT,HERE,read,save,digest,connect
from original_disjoint_routing_metadata_scope_20261010 import boundaries,verify_boundaries
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-man-fuk-ten-source-scope-declaration-v2-20261010';ROLE=BASE/'government-xl-man-fuk-ten-current-complete-typed-role-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();typed=read(ROLE/'typed-role.json.gz');receipt=read(ROLE/'result.json');assert typed['currentTypedPhysicalAccepted'] and not typed['reasons'] and typed['completeOriginalFaces']==29125 and typed['completeOriginalComponents']==131 and typed['allCurrentThirdPartyAndOtherProposedOriginalCrossingWallCollisionsStrictClear'] is True
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 dirs=sorted({d for pattern in ['*man-fuk*','*man-ming*','*man-hei*'] for d in BASE.glob(pattern) if d.is_dir() and not any(x in d.name for x in ['typed-stage','installed','scope-declaration','complete-typed-stage'])})
 paths={str(p.relative_to(ROOT)) for d in dirs for p in d.rglob('*') if p.is_file()}
 files={p for pattern in ['*man_fuk*','*man-fuk*','*man_ming*','*man-ming*','*man_hei*','*man-hei*'] for p in HERE.glob(pattern) if p.is_file() and not any(x in p.name for x in ['stage-install','live-install','scope-declaration','complete-typed-stage'])}
 files.update(HERE/n for n in ['xl-complete-multi-source-finite-column-refinement-v1-20261010.py','xl-complete-multi-source-finite-wall-contexts-v1-20261010.py','original_upward_facets_conservative_terrain_ceiling_20261010.py','test_original_upward_facets_conservative_terrain_ceiling_20261010.py','original_ordinary_ground_root_graph_20261009.py','original_strict_clear_cap_wall_paths_20261009.py','xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs','candidate_native_support_witness_v1_20261010.mjs','test_candidate_native_support_witness_v1_20261010.mjs','xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs','original_disjoint_routing_metadata_scope_20261010.py','test_original_disjoint_routing_metadata_scope_20261010.py']);files.add(Path(__file__));paths.update(str(p.relative_to(ROOT)) for p in files)
 prior=read(BASE/'xl-terrain-recovery-20261010-mei-yat-stage-live-closure-v1/closed-scope.json')
 aliases=list(prior['historicalManifestAliases']);leaf=set(prior['metadataLeafPaths']);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';raw=manifestpath.read_bytes();assert digest(raw)==typed['currentManifest']['sha256'];OUT.mkdir()
 original_script=HERE/'xl-man-fuk-current-bound-envelope-promotion-v2-20261010.py'
 tree=ast.parse(original_script.read_text());texts=[node.args[0].value for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='write_text' and len(node.args)==1 and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str)];assert len(texts)==1
 original_readme=BASE/'government-xl-man-fuk-current-bound-envelope-promotion-v2-20261010/README.md'
 historical_receipt=read(original_readme.parent/'result.json');binding=next(r for r in historical_receipt['evidenceRefs'] if r['path']==str(original_readme.relative_to(ROOT)))
 recovered=texts[0].encode();assert digest(recovered)==binding['sha256']
 recovered_path=OUT/'exact-original-frozen-identity-readme.txt';recovered_path.write_bytes(recovered);paths.add(str(recovered_path.relative_to(ROOT)));paths.add(str(original_script.relative_to(ROOT)))
 frozen_aliases=[dict(path=binding['path'],sha256=binding['sha256'],archivePath=str(recovered_path.relative_to(ROOT)))]
 save(OUT/'historical-readme-recovery.json',dict(originalFrozenRef=binding,recoveredExactBytes=ref(recovered_path),verbatimProducer=ref(original_script),metadataOnly=True,numericalEvidenceChanged=False));paths.add(str((OUT/'historical-readme-recovery.json').relative_to(ROOT)))
 archive=OUT/'acceptance-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)));leaf.add(str(archive.relative_to(ROOT)));manifest=read(archive)
 leaf.update('3d-viewer/'+u for u in manifest['officialModelCatalogues']);leaf.update('3d-viewer/'+e['url'] for e in manifest['terrainPatches']);pointers=[]
 for d in dirs:
  p=d/'current-source-terrain-preflight.json'
  if not p.is_file():continue
  pre=read(p)
  if 'completeCurrentTerrainRouting' not in pre:continue
  sha=pre['currentManifest']['sha256'];matches=[r for r in aliases if r['sha256']==sha];assert matches,'Exact historical manifest archive is required';original_manifest=read(ROOT/matches[0]['archive']['path']);assert digest((ROOT/matches[0]['archive']['path']).read_bytes())==sha
  for r in pre['completeCurrentTerrainRouting']:assert ref(ROOT/r['asset']['path'])==r['asset']
  declared=boundaries(pre,original_manifest);verify_boundaries(pre,original_manifest,declared);pointers.extend(dict(path=str(p.relative_to(ROOT)),documentSHA256=ref(p)['sha256'],boundary=b) for b in declared)
 save(OUT/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],historicalManifestAliases=aliases,aliases=frozen_aliases,metadataLeafPaths=sorted(leaf),metadataLeafJsonPointers=pointers,currentRoleNeon=receipt['jobId'],sourceGeometryChanges=0,terrainProposalChanged=True,stageAndLiveExcluded=True,qualification='All ten unchanged Man Fuk originals:29125 source and literal rendered faces,131 exact-contact rooted parts,five independently verified actual footings,all105 steep exposed grade-wall paths,all70 current forms and complete retained ManOi mesh,59 foreign basic forms and every installed native bound. Exact finite column domains and raw failed proposals preserved. Terrain-only current-parent restoration and Float32 seam infill; zero government building geometry changes. Only previously reviewed global metadata and precisely bound disjoint-routing acquisition pointers are nonrecursive. Root unchanged verifier required; browser/live still required; zero installed credit.'))
 print(dict(paths=len(paths),pointers=len(pointers),currentRoleNeon=receipt['jobId']),flush=True)
if __name__=='__main__':main()
