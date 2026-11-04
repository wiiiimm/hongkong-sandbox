"""Complete actual current canopy mesh vs every source/literal credited wall.

Current basic heights are procedural/estimated and stay unchanged. No provider
NULL height, footprint overlap or identity relationship grants collision credit.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-villa-canopy-complete-actual-foreign-wall-context-v1-20261010';DOC=BASE/BATCH
PHYS=BASE/'government-xl-villa-five-original-coupled-physical-v3-20261010';WALL=BASE/'government-xl-villa-five-original-and-rendered-finite-wall-contexts-v3-20261010';FOREIGN=BASE/'government-xl-villa-five-current-complete-foreign-wall-scope-v1-20261010';UID='landsd/325786:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();selection=read(PHYS/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256']
 foreign=read(FOREIGN/'diagnostic.json.gz');required=[r for r in foreign['completeActualForeignBasicForms'] if r['requiresCompleteActualForeignMesh']];assert [r['uid'] for r in required]==[UID] and not foreign['foreignNativeBoundsTouchingWalls'] and not foreign['allExactSourceAuthoredMutualWallIntersectionsRetained']
 neighbours=read(PHYS/'neighbour-inputs.json.gz');form=required[0]['completeActualCurrentForm'];tiles=[]
 for p,h in neighbours['inputHashes'].items():
  path=ROOT/p;assert ref(path)['sha256']==h
  matches=[b for b in read(path)['buildings'] if b['uid']==UID]
  if matches:assert matches==[form];tiles.append(p)
 assert len(tiles)==1
 inputs=dict(manifestSHA256=selection['manifestSHA256'],currentInputHashes=neighbours['inputHashes'],rows=[dict(tile=tiles[0],building=form)])
 save(DOC/'actual-canopy-input.json',inputs);exporter=HERE/'xl-terrain-recovery-20261010-garden-podium-foreign-basic-meshes-v1.mjs';output=DOC/'actual-canopy-rendered-geometry.json'
 subprocess.check_call(['node',str(exporter),str(DOC/'actual-canopy-input.json'),str(output)],cwd=ROOT)
 exported=read(output);assert len(exported['rows'])==1 and exported['rows'][0]['uid']==UID and exported['rows'][0]['currentBuilding']==form and exported['currentManifestSHA256']==selection['manifestSHA256']
 for p,h in exported['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 f=exported['rows'][0];mesh=np.asarray(f['position'],float).reshape(-1,3)[np.asarray(f['index']).reshape(-1,3)];assert np.isfinite(mesh).all()
 runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath)['rows'];walls=read(WALL/'diagnostic.json.gz')['rows'];proofs=[];assets=[]
 for row in selection['rows']:
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];assets.append(asset)
  tri=decode_original_world_triangles(raw);r=next(x for x in runtime if x['uid']==row['uid']);actual=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
  wall=next(x for x in walls if x['uid']==row['uid'])
  for mode,a in [('completeOriginal',tri),('actualRendered',actual)]:
   c=wall[mode];assert not c['unresolvedWallConditions'] and not c['buriedUpwardFaces'];ids=c['affectedFaces']
   contacts=exact_component_contacts(a,ids,mesh,list(range(len(mesh)))) if ids else dict(contacts=[],trianglePairsTested=0,allPairsExamined=True,geometryChanges=0,physicalSupportAccepted=False)
   proofs.append(dict(uid=row['uid'],representation=mode,allCreditedWallFaces=ids,completeWallActorFaces=len(a),completeWallActorWorldSHA256=digest(a.tobytes()),completeActualForeignFaces=len(mesh),completeForeignWorldSHA256=digest(mesh.tobytes()),exactActualSurfaceContacts=contacts,strictAllWallSurfacesDisjoint=not contacts['contacts']))
 clear=all(p['strictAllWallSurfacesDisjoint'] for p in proofs)
 save(DOC/'diagnostic.json.gz',dict(manifestSHA256=selection['manifestSHA256'],foreignUID=UID,currentActualBasicForm=form,completeActualForeignFaces=len(mesh),completeActualForeignWorldSHA256=digest(mesh.tobytes()),sourceAndLiteralAllWallTrials=proofs,allActualCurrentForeignCanopyWallSurfacesStrictlyDisjoint=clear,estimatedHeightsRemainEstimated=True,propertyOwnershipClaimed=False,sourceGeometryChanges=0,fullAcceptance=False,publication=False))
 assert ref(manifest)['sha256']==selection['manifestSHA256']
 refs=[Path(__file__),manifest,PHYS/'result.json',PHYS/'selection.json.gz',PHYS/'neighbour-inputs.json.gz',WALL/'result.json',WALL/'diagnostic.json.gz',FOREIGN/'result.json',FOREIGN/'diagnostic.json.gz',runtimepath,DOC/'actual-canopy-input.json',output,exporter,HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',*assets]+[ROOT/p for p in exported['inputHashes']]
 s=importlib.util.spec_from_file_location('villa_canopy_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-current-actual-basic-canopy-all-source-and-literal-grade-wall-collision-diagnostic-v1',sorted(set(refs)),dict(uids=[r['uid'] for r in selection['rows']]+[UID],allActualCurrentForeignCanopyWallSurfacesStrictlyDisjoint=clear,completeActualForeignFaces=len(mesh),exactSurfaceIntersections=sum(len(r['exactActualSurfaceContacts']['contacts']) for r in proofs),sourceGeometryChanges=0,fullAcceptance=False,publication=False,humanDecisionRequired=False))
 print(dict(actualForeignFaces=len(mesh),strictForeignClear=clear,contacts=sum(len(r['exactActualSurfaceContacts']['contacts']) for r in proofs)),flush=True)
if __name__=='__main__':main()
