"""Frozen stage/source deployment closure for root's serial installation review."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261009-market-six-stage-closure-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted/government-xl-terrain-recovery-market-six-typed-stage-v2-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();paths=[]
 for v in range(1,6):
  directory=ROOT/'docs/astra-city/government-import'/f'government-xl-terrain-recovery-market-six-typed-stage-v{v}-20261009'
  if directory.exists():paths.extend(p for p in directory.rglob('*') if p.is_file())
 paths.extend(p for p in STAGE.rglob('*') if p.is_file())
 for pattern in ['xl-terrain-recovery-20261009-market-six-stage-install-v*.py','xl-terrain-recovery-20261009-market-six-live-install-v*.py','xl-terrain-recovery-20261009-multi-native-*browser*.mjs']:
  paths.extend(HERE.glob(pattern))
 paths.append(Path(__file__))
 acceptance=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-typed-stage-v5-20261009/acceptance.json';a=read(acceptance);assert a['passed'] and a['newlyInstalled']==0
 for r in a['evidenceRefs']:assert ref(ROOT/r['path'])==r
 plan=read(STAGE/'plan.json');catalogue=read(STAGE/'catalogue.json');deployed=[]
 for area in plan['areas']:
  p=ROOT/area['catalogue'];deployed.append({**ref(p),'destination':'3d-viewer/'+area['destination']})
  for m in catalogue['models']:
   asset=p.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256'] and len(asset.read_bytes())==m['bytes']
   deployed.append({**ref(asset),'destination':str(Path('3d-viewer')/Path(area['destination']).parent/m['asset']),'uid':m['uid'],'originalTriangles':m['triangles']})
 for patch in plan['topLevelTerrainPatches']:
  p=ROOT/patch['source'];assert digest(p.read_bytes())==patch['sha256'];deployed.append({**ref(p),'destination':'3d-viewer/'+patch['destination']})
 save(DOC/'closure.json',{'closedStagePaths':[ref(p) for p in sorted(set(paths))],'stagedDeployableDependencies':deployed,'sourceProofClosure':ref(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-proof-closure-v2/closure.json'),'acceptedStage':ref(acceptance),'rootOnlyLiveInstaller':ref(HERE/'xl-terrain-recovery-20261009-market-six-live-install-v4.py'),'liveOutputExcluded':True,'sourceGeometryChanges':0,'publication':False,'newlyInstalled':0,'note':'Stage v1/v2 failure records and v3/v4 preliminary selected/solid passes remain immutable. Final stage v5 tests actual complete solid source/triangle/material/fallback state and complete desktop assembly framing; old territorial archival dependencies retain explicit unavailable-historical classification in source proof closure.'})
 print(json.dumps({'closedStageFiles':len(set(paths)),'deployableDependencies':len(deployed),'finalStagePassed':True}),flush=True)
if __name__=='__main__':main()
