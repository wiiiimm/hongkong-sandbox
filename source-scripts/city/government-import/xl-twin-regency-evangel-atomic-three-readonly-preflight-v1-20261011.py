"""Unexecuted local read-only actual tuple/math/domain preflight for root review.
No DB query/write, ledger, actor acceptance, publication or geometry generation.
"""
from pathlib import Path
import json,time
from run import ROOT,HERE,read,save,digest
from publication_lock import locked_publication
import twin_evangel_atomic_three_separation_replay_v1_20261011 as guards
CURRENT='df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'
DOC=ROOT/'docs/astra-city/government-import/government-xl-twin-evangel-atomic-three-readonly-preflight-v1-20261011'
TWIN=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-twin-regency-pair-complete-current-role-v1'
EVANGEL=ROOT/'docs/astra-city/government-import/government-xl-evangel-college-91306-whole-current-role-acceptance-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 with locked_publication(ROOT):
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=ref(manifest);assert before['sha256']==CURRENT
  pins=[before,ref(Path(__file__)),ref(Path(guards.__file__)),ref(TWIN/'typed-role.json.gz'),ref(EVANGEL/'acceptance.json')]
  for folder in [TWIN,EVANGEL]:
   receipt=read(folder/'result.json');pins.append(ref(folder/'result.json'));pins+=receipt['evidenceRefs']
  pins=list({(p['path'],p['sha256']):p for p in pins}.values())
  for pin in pins:assert ref(ROOT/pin['path'])==pin
  print(json.dumps(dict(phase='all-original-input-pins-verified',references=len(pins))),flush=True)
  twin=guards.module('preflight_twin_stage',HERE/'xl-terrain-recovery-20261011-twin-regency-two-private-stage-v1.py')
  evangel=guards.module('preflight_evangel_stage',HERE/'xl-evangel-college-91306-unchanged-private-stage-v3-20261011.py')
  rows=read(twin.PHYSICAL/'selection.json.gz')['rows'];erow=read(evangel.DOCS['physical']/'selection.json.gz')['rows'][0]
  for stage in [twin,evangel]:
   pins += [ref(Path(stage.__file__)),ref(stage.STAGE/'plan.json'),ref(stage.STAGE/'catalogue.json'),ref(stage.STAGE/'browser-config.json'),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json')]
  separation=guards.separation(twin,evangel,rows,erow);print(json.dumps(dict(phase='complete-position-and-routing-domain-separation-pass')),flush=True)
  tr=read(TWIN/'typed-role.json.gz');er=read(EVANGEL/'acceptance.json');prepared=guards.prepare_math(tr,er)
  print(json.dumps(dict(phase='both-original-bound-pure-compositions-pass')),flush=True)
  replay=guards.replay_math(prepared)
  for pin in pins:assert ref(ROOT/pin['path'])==pin
  assert ref(manifest)==before
  save(DOC/'separation.json',separation)
  save(DOC/'result.json',dict(passed=True,currentManifest=before,preApplyPureReplays=2,allFourWholePositionWorldsAndBothEntireTerrainDomainsStrictlyDisjoint=True,originalTwinRoleCompositionSHA256=digest(json.dumps(prepared['twinExpected'],sort_keys=True,separators=(',',':')).encode()),originalEvangelRoleCompositionSHA256=digest(json.dumps(prepared['evangelExpected'],sort_keys=True,separators=(',',':')).encode()),replay=replay,publication=False,newlyInstalled=0,nativeReacceptance=False,sourceGeometryChanges=0,evidenceRefs=pins+[ref(DOC/'separation.json')]))
  print(json.dumps(dict(passed=True,publication=False,doc=str(DOC.relative_to(ROOT)))),flush=True)
if __name__=='__main__':main()
