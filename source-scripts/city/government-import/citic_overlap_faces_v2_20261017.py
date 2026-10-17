"""Account for every original podium face projecting into a foreign form; no approval."""
from pathlib import Path
import uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-citic-overlap-faces-v2-20261017'
DOC=BASE/BATCH
UID='landsd/232579:0'
def main():
 assert not DOC.exists()
 refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in ['government-xl-citic-current-pair-v1-20261017','government-xl-citic-current-assembly-v1-20261017']:
   p=BASE/name/'result.json';r=read(p)
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(p)
   for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))]
  refs.append(p);return read(p)
 geo=consume(HERE/'local/government-xl-citic-current-pair-v1-20261017/runtime-geometry.json.gz')
 g=next(x for x in geo['rows'] if x['uid']==UID)
 t=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 identity=consume(BASE/'government-xl-citic-current-assembly-v1-20261017/landsd-232579-0-identity.json')
 foreign=[x for x in identity['freshCurrentIdentity']['intersectingForms'] if not x['sameParent']]
 final=module('citic_overlap_context',HERE/'xl-final-script-pass.py')
 lo,hi=t.min((0,1)),t.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 claim=reservations.claim('citic-overlap-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();out=[]
  for f in foreign:
   matches=[(b,tile) for b,polygon,tile in forms if b['uid']==f['uid']];assert len(matches)==1
   b,tile=matches[0];p=ROOT/'3d-viewer'/tile
   assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p)
   poly=Polygon(b['rings'][0],b['rings'][1:]);faces=[]
   for i,face in enumerate(t):
    fp=Polygon(face[:,[0,2]])
    if fp.area==0:continue
    hit=fp.intersection(poly)
    if hit.area>0:
     faces.append(dict(faceIndex=i,vertices=face.tolist(),projectedOverlapM2=hit.area,sourceYMin=float(face[:,1].min()),sourceYMax=float(face[:,1].max())))
   out.append(dict(uid=f['uid'],name=b.get('name'),base=b['base'],top=b['base']+b['height'],faces=faces,faceCount=len(faces)))
  save(DOC/'faces.json.gz',dict(sourceUid=UID,completeSourceFaces=len(t),foreignForms=out,installationApproved=False))
  refs.append(HERE/'xl-final-script-pass.py')
  result=module('citic_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-citic-foreign-projection-face-account-v1',list(dict.fromkeys(refs)),dict(uids=[UID],foreignForms=[dict(uid=x['uid'],faceCount=x['faceCount']) for x in out],newlyInstalled=0,installationApproved=False))
  print(dict(jobId=result['jobId'],foreignForms=result['foreignForms']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
