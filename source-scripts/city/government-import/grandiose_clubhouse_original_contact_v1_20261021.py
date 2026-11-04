"""Exact unchanged original-to-original surface comparison; diagnostic only."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-grandiose-clubhouse-original-contact-v1-20261021'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/246824:0','landsd/27898:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)];triangles=[]
 for batch,sha,count in [
 ('government-xl-grandiose-missing-podium-v1-20261021','205606ffc6076f33d504f33878067b7e2aa72d62baa9e22f712b1e80e8db99e5',3627),
 ('government-xl-tko-clubhouse-source-v1-20261021','0f061357cde3fd4e582f2544986eb4a5a8b52e9dd4d0f29cc66077135c71f4e5',1837)]:
  receiptPath=BASE/batch/'result.json';receipt=read(receiptPath);refs.append(receiptPath)
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  p=BASE/batch/'sources.json.gz';pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
  assert any(r['model']['asset']['sha256']==sha for r in read(p)['rows'])
  asset=HERE/'local/government-xl-thirty-spatial-original-closures-20261008/assets'/(sha+'.glb.gz')
  raw=asset.read_bytes();assert digest(raw)==sha;refs.append(asset)
  tri=decode_original_world_triangles(raw);assert len(tri)==count;triangles.append(tri)
 assert reservations.owns(lease)
 a,b=triangles;proof=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))))
 save(DOC/'contacts.json.gz',proof)
 counts={str(dim):sum(c['dimension']==dim for c in proof['contacts']) for dim in [0,1,2]}
 result=dict(uids=UIDS,faces=[len(a),len(b)],contactDimensions=counts,installationApproved=False,newlyInstalled=0,geometryChanges=0,qualification='Complete original-source finite surface contacts only; not current runtime, support, containment or installation approval.')
 save(DOC/'summary.json',result)
 refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
 module('original_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-clubhouse-podium-complete-surface-contact',refs,result)
 print(json.dumps(result),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
