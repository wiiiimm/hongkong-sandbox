from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-aerial-observations-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists()
refs=[Path(__file__)]
for name in ['government-xl-sheung-shui-overlap-imagery-v1-20261020','government-xl-sheung-shui-source-imagery-overlay-v1-20261020']:
 folder=BASE/name;r=read(folder/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  path=ROOT/e['path'];assert digest(path.read_bytes())==e['sha256'];refs.append(path)
observations={
 '74535:0':'Detailed outline follows the visible end-wing roof perimeter; the basic footprint crosses the same roof margins and extends onto an adjacent strip. Supports same-complex interpretation, not blanket basic suppression.',
 '88048:0':'Detailed outline and basic narrow footprint track the same visible linear side feature; detailed curved stair outlines occur at both ends. Image does not establish elevations or collision clearance.',
 '47284:0':'Detailed outline follows the building-side boundary and stair features beside the broad basic triangular footprint. The broad basic footprint is not wholly represented by the detailed source.',
 '47324:0':'Same building-edge and curved-stair correspondence beside the basic triangular footprint; retain independent basic coverage outside source.',
 '87203:0':'Long basic strip remains separate from the detailed perimeter except near protruding corners. No basis to remove the whole strip.'}
save(DOC/'observations.json',dict(uid='landsd/56054:0',reviewer='root',actuallyViewedImages=10,observations=observations,interpretationUsesAI=True,geometryChanges=0,imageryCaptureDateKnown=False,identityApproved=False,installationApproved=False,nextStep='Use exact source-root identity and reviewed aerial correspondence to resolve overlap roles; preserve basic-only coverage and validate final browser composition. Remaining source extent outside these five views still requires explicit coverage.'))
module('aerial_observations_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'sheung-shui-reviewed-official-aerial-observations',list(set(refs)),dict(uids=['landsd/56054:0'],actuallyViewedImages=10,identityApproved=False,installationApproved=False))
