"""Record coordinator-inspected original-source views; no identity/support waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-component-visual-observations-v1-20261019';DOC=BASE/BATCH;VIEWS=BASE/'government-xl-lai-chi-kok-component-views-v1-20261019';CHECKS=BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [VIEWS,CHECKS]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 shapes={'198623':'Long rectangular raised structure with parallel upper edges, along platform boundary.','192968':'Rectangular raised structure at the curved platform end.','218874':'Rectangular raised structure; recorded footprint extends beyond one short end.','206341':'Rounded raised structure; recorded rounded footprint extends beyond source outline.','207349':'Rounded raised structure; recorded rounded footprint extends beyond source outline.','206337':'Long narrow raised edge structure; source and recorded footprint extents differ.','207352':'Small rectangular block overlapping the stepped platform boundary.'}
 rows=[]
 for v in read(VIEWS/'render.json')['views']:
  uid=v['uid'];key=uid.split('/')[1].split(':')[0];identity=read(CHECKS/(uid.split('/')[1]+'-identity.json'));route=identity['exactCurrentComponentRoute'];rows.append(dict(uid=uid,image=v['image'],actuallyViewedByCoordinator=True,observation=shapes[key],officialRouteQualified=route['qualified'],official=route['official'],rawIdentityPassed=identity['passed'],rawIdentityReasons=identity['reasons'],identityAccepted=False,supportAccepted=False))
 assert len(rows)==7
 summary=dict(rows=rows,installationApproved=False,sourceGeometryChanges=0,qualification='All seven PNGs were inspected in this turn. Geometric shape observations only: outline correspondence does not resolve raw coverage failures, source support, embedded faces, terrain dependency, or runtime acceptance. Footprint overlay is drawn at diagnostic height and is not an observed vertical-position error.')
 save(DOC/'observations.json',summary)
 module('lai_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-reviewed-original-component-images',refs,dict(uids=[r['uid']for r in rows],summary=summary,installationApproved=False));print('Seven inspected images recorded; no installation approval.',flush=True)
if __name__=='__main__':main()
