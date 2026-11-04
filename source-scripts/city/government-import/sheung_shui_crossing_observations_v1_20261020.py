"""Image-backed source crossing interpretation; no runtime or installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-crossing-observations-v1-20261020';DOC=BASE/BATCH
VIEWS=BASE/'government-xl-sheung-shui-isolated-groups-v1-20261020';GROUPS=BASE/'government-xl-sheung-shui-whole-components-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [VIEWS,GROUPS]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 groups=read(GROUPS/'groups.json')['groups'];assert len(groups)==10;rows=[]
 for n,g in enumerate(groups,1):
  image=VIEWS/('group-'+str(n)+'-terrain.png');assert digest(image.read_bytes())==pins[str(image.relative_to(ROOT))]
  stair=n in [1,3,5,7,8]
  rows.append(dict(group=n,sourceFaceIds=g['sourceFaceIds'],flaggedSourceFaceIds=g['flaggedSourceFaceIds'],imageActuallyViewed=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),reviewer='Codex ROOT',observation=('External stair assembly with curved landings. Red crossing faces are at the low terminal edge beneath the lower flight.' if stair else 'Tall narrow planar/prismatic panel, with most of its height exposed and its bottom entering original terrain. Isolated rendering does not establish a load-bearing function.'),sourceRoleInterpretation=('stair-lower-edge'if stair else'vertical-panel-base'),currentTerrainAccepted=False,installationApproved=False))
 assert sum(len(r['flaggedSourceFaceIds'])for r in rows)==68
 save(DOC/'ROOT-OBSERVATIONS.json',dict(uid='landsd/56054:0',rows=rows,sourceOnly=True,aiEvidenceInterpretation=True,aiGeometryModelling=False,nextStep='Evaluate exact current/proposed runtime terrain crossings and resolve separate whole-source wing identity/foreign-overlap flag. Do not repeat these source role views or treat original-ground observations as runtime acceptance.'))
 refs.extend(ROOT/p for p in pins)
 module('sheung_observation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'sheung-shui-ten-source-crossing-groups-reviewed',refs,dict(uids=['landsd/56054:0'],reviewedGroups=10,accountedFlaggedFaces=68,stairGroups=5,verticalPanelGroups=5,currentTerrainAccepted=False,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
