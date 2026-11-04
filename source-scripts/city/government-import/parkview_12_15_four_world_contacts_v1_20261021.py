"""Source-only diagnostic of exact Parkview originals; no placement approval."""
from pathlib import Path
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-12-15-four-world-contacts-v1-20261021';DOC=BASE/BATCH
CAP=BASE/'government-xl-parkview-12-15-shared-runtime-v1-20261021';ATTR=BASE/'government-xl-parkview-12-15-actual-render-attributes-v1-20261021'
UIDS=['landsd/255440:0','landsd/255648:0'];POD='landsd/254491:0'
def owned():
 assert reservations.owns(read(LOCAL/'reservation.json'))
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,ATTR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def consumed(p):
  rel=str(p.relative_to(ROOT));assert rel in pins and digest(p.read_bytes())==pins[rel],rel;refs.append(p)
 consumed(CAP/'selection.json.gz');consumed(ATTR/'attributes.json.gz')
 selection=[r for r in read(CAP/'selection.json.gz')['rows']if r['uid']in UIDS+[POD]];assert len(selection)==3
 worlds={'original':{}}
 for r in selection:
  p=ROOT/r['candidate']['path'];consumed(p);worlds['original'][r['uid']]=decode_original_world_triangles(p.read_bytes())
 capture=read(ATTR/'attributes.json.gz')
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in capture['rows']if r['uid']in UIDS+[POD]}
 def geom(t):return dict(position=t.reshape(-1).tolist(),index=list(range(t.size//3)))
 rows=[dict(uid=u,mode=m,source=geom(w[u]),support=geom(w[POD]),sourceWorldSHA256=digest(np.asarray(w[u],dtype='<f8').tobytes()),supportWorldSHA256=digest(np.asarray(w[POD],dtype='<f8').tobytes()))for m,w in worlds.items()for u in UIDS]
 save(DOC/'input.json.gz',dict(rows=rows));tool=HERE/'parkview-three-four-world-contacts-v1-20261020.mjs'
 subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'contacts.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'contacts.json.gz');summary=[{k:v for k,v in r.items()if k not in ['mapped','rawInterface']}for r in report['rows']]
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'exact_packed_world_geometry_20261009.py'])
 module('parkview_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-only-four-world-support-samples',list(dict.fromkeys(refs)),dict(uids=UIDS+[POD],rows=summary,scope='Exact historical source bytes and captured world representations only; current placement/terrain not approved.',installationApproved=False))
import sys, uuid, json
from run import reservations
LOCAL=HERE/'local'/BATCH
UID='landsd/33396:0'
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/255440:0','building:landsd/254491:0','building:landsd/255648:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

