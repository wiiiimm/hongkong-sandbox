"""Complete unchanged source foundation check on current captured drawn ground."""
from pathlib import Path
import uuid,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-apex227942-current-capture-v3-20261017';BATCH='government-xl-apex227942-current-foundation-v1-20261017';DOC=BASE/BATCH;UID='landsd/227942:0'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  rt=HERE/'local'/CAP.name/'runtime-geometry.json.gz';g=read(rt)['rows'][0];row=read(CAP/'selection.json.gz')['rows'][0];assert g['uid']==row['uid']==UID and g['sourceSHA256']==row['sourceSHA256']
  tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(tri)==row['native']['model']['triangles']
  b=row['source']['building'];f=module('yoho_foundation',HERE/'xl-final-script-pass.py').foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));passed=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0
  save(DOC/'foundation.json',dict(uid=UID,foundation=f,strictFoundationAccepted=passed,fullAcceptance=False,installationApproved=False));print(dict(passed=passed,foundation=f),flush=True)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert reservations.owns(lease)
  result=module('yoho_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex227942-complete-current-foundation-v1',[Path(__file__),CAP/'result.json',rt,HERE/'xl-final-script-pass.py',*[ROOT/p for p in pins]],dict(uids=[UID],strictFoundationAccepted=passed,fullAcceptance=False,newlyInstalled=0,nextStep='Complete identity, current neighbours and browser checks; retain actual failures for investigation.'))
  print(result['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
