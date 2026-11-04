"""Full rendered mall/foreign BASIC surface contacts before and after; diagnostic."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-foreign-collision-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-manhattan-assembly-capture-v1-20261021'
UID='landsd/276331:0';FOREIGN='landsd/231708:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 receipt=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json'];pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cap=take(CAP/'attributes.json.gz');r=next(r for r in cap['rows']if r['uid']==UID)
 mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);refs.append(mp);mh=digest(mp.read_bytes());forms=[];hashes={}
 native=set()
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p);hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());native.update(e['uid']for e in read(p)['models'])
 assert UID not in native and FOREIGN not in native
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in [UID,FOREIGN]:forms.append(dict(building=b,tile=str(p.relative_to(ROOT))));hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());refs.append(p)
 assert len(forms)==2
 save(DOC/'input.json',dict(manifestSHA256=mh,currentInputHashes=hashes,rows=forms))
 tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json').relative_to(ROOT)),str((DOC/'basic.json').relative_to(ROOT))],cwd=ROOT,check=True)
 basic=read(DOC/'basic.json');world={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in basic['rows']};foreign=world[FOREIGN];summary=[]
 modes={'before-basic':world[UID]}
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:modes[mode]=np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]
 for mode,tri in modes.items():
  assert reservations.owns(lease);proof=exact_finite_contacts(tri,list(range(len(tri))),foreign,list(range(len(foreign))))
  save(DOC/(mode+'.json.gz'),proof);positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
  item=dict(mode=mode,mallFaces=len(tri),foreignFaces=len(foreign),positiveContactPairs=len(positive),mallContactFaces=sorted({c['sourceFaceA']for c in positive}),foreignContactFaces=sorted({c['sourceFaceB']for c in positive}));summary.append(item);print(json.dumps(item),flush=True)
 for report in [basic,cap]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert digest(mp.read_bytes())==mh
 refs.extend([tool,HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
 result=dict(uids=[UID,FOREIGN],rows=summary,installationApproved=False,qualification='Complete finite surface contacts, not volumetric containment or semantic ownership approval. Before BASIC and after unchanged original source retain all facets.');save(DOC/'summary.json',result)
 module('yoho_foreign_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-foreign-basic-before-after-surface-contacts',list(dict.fromkeys(refs)),result)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
