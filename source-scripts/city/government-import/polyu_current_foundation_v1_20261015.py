"""Run existing foundation acceptance on all four saved PolyU representations."""
from pathlib import Path
import uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-current-foundation-v1-20261015';DOC=BASE/BATCH;UID='landsd/305582:0'
def main():
 assert not DOC.exists()
 bound=BASE/'government-xl-polyu-current-map-rebind-v1-20261015/result.json';receipt=read(bound)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']
 folder=BASE/'government-xl-polyu-whole-actor-current-ground-delta3-v1-20261014';wp=folder/'complete-saved-actor-worlds.json.gz';gp=folder/'complete-whole-actor-current-candidate-ground.json.gz'
 actor=next(r for r in read(wp)['rows']if r['uid']==UID);ground=np.asarray(read(gp)['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)
 lookup=HERE/'local/government-xl-polyu-current-loader-validation-v1-20261015/source-forms-lookup.json';b=read(lookup)[UID]['building'];poly=Polygon(b['rings'][0],b['rings'][1:]);f=module('polyu_existing_foundation',HERE/'xl-final-script-pass.py')
 claim=reservations.claim('polyu-foundation-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];rows=[]
 try:
  DOC.mkdir()
  for mode,w in actor['worlds'].items():
   tri=np.asarray(w['completeWorldTriangles'],float).reshape(-1,3,3);assert len(tri)==10536
   foundation=f.foundation_context(tri,ground,poly)
   accepted=foundation['completeTerrainTriangles']==len(tri)and foundation['fullyBuriedUpwardTriangles']==0 and foundation['fullyBuriedAreaFraction']<=0.001
   row=dict(uid=UID,mode=mode,worldSHA256=digest(tri.tobytes()),supportSHA256=digest(ground.tobytes()),foundation=foundation,foundationAccepted=accepted);rows.append(row);save(DOC/(mode+'.json'),row);assert reservations.heartbeat(lease)['ok'];print(mode,'accepted',accepted,'buried',foundation['fullyBuriedTriangles'],flush=True)
  for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']
  save(DOC/'summary.json',dict(rows=rows,allFoundationChecksPassed=all(r['foundationAccepted']for r in rows),fullAcceptance=False))
  paths=[ROOT/q['path']for q in receipt['evidenceRefs']]+[bound,wp,gp,lookup,Path(__file__),HERE/'xl-final-script-pass.py']
  module('polyu_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-foundation-four-representations-v1',paths,dict(uids=[UID],rows=rows,allFoundationChecksPassed=all(r['foundationAccepted']for r in rows),fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
