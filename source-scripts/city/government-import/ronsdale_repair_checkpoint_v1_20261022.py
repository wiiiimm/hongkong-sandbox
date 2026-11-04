"""Persist verified Ronsdale source success and private terrain failure for resumption."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-ronsdale-repair-checkpoint-v1-20261022'
def main():
 refs=[Path(__file__)];jobs=[]
 for name in ['government-xl-ronsdale-podium-original-ground-v1-20261022','government-xl-ronsdale-adjacent-ground-v1-20261022','government-xl-ronsdale-terrain-scope-v2-20261022']:
  folder=BASE/name;r,pins=authenticate(folder)
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
  refs.extend([folder/'result.json',*[ROOT/path for path in pins]]);jobs.append(r['jobId'])
 failed=BASE/'government-xl-ronsdale-private-terrain-v1-20261022'
 diagnostic=read(failed/'overlap-diagnostic.json');assert diagnostic['coverageDifferenceM2']>400 and diagnostic['triangles']>25000
 refs.extend([failed/'overlap-diagnostic.json',failed/'failed-or-proposed-terrain.json',HERE/'ronsdale_private_terrain_v1_20261022.py',HERE/'ronsdale_terrain_scope_v1_20261022.py'])
 result=dict(uids=['landsd/233771:0','landsd/256702:0'],completedInputJobs=jobs,sourceGeometryChanges=0,installationApproved=False,terminalRejection=False,actionableState='held-for-scripted-terrain-repair',reason='Broad original terrain candidate lacks full rectangle coverage and has tile-seam overlap; also exceeds 25000-face terrain budget.',diagnostic=diagnostic,nextAction='Build a bounded original-terrain inset around the complete source projection, retaining current parent outside and resolving the original tile seam with the existing surface-preserving constructor. Then run full source support, affected-actor, runtime and browser checks.',originalPodiumGround=dict(completeFaces=2438,totalFaces=2438,buriedFaces=0),externalModellingAICalls=0)
 save(BASE/BATCH/'summary.json',result)
 module('ronsdale_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-source-terrain-repair-checkpoint',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
