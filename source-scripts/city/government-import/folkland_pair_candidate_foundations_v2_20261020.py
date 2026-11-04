"""Complete Folkland original/renderer foundations on private replacement terrain."""
from pathlib import Path
import json,subprocess,sys,uuid,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-pair-candidate-foundations-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-folkland-pair-runtime-capture-v1-20261020';SRC=BASE/'government-xl-coverage-assembly-closure-20261007-264677-0';GROUND=BASE/'government-xl-next-twenty-original-ground-v3-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,GROUND,BASE/'government-xl-folkland-preserve-neighbours-v1-20261020']:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def consume(d,p):
  assert digest(p.read_bytes())==pins[d.name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=consume(CAP,SRC/'selection.json.gz');rows=selection['rows'];assert {r['uid']for r in rows}=={'landsd/264677:0','landsd/225387:0'}
 attr=consume(CAP,CAP/'attributes.json.gz');assert attr['startEndAllInputsVerified'];mp=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(mp.read_bytes());refs.append(mp);selection['manifestSHA256']=mh
 originals={}
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(p);originals[r['uid']]=decode_original_world_triangles(raw)
  tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
 save(DOC/'selection.json.gz',selection)
 candidate_doc=BASE/'government-xl-folkland-preserve-neighbours-v1-20261020'
 candidate_summary=consume(candidate_doc,candidate_doc/'summary.json');assert candidate_summary['terrainValidatorPassed'] and candidate_summary['terrainFaces']<=100000
 candidate_path=candidate_doc/'candidate-terrain.json';patch=consume(candidate_doc,candidate_path)
 parent_url='city/data/terrain/unnamed147996-private-v1.json';parentpath=ROOT/'3d-viewer'/parent_url;parent=read(parentpath);refs.append(parentpath)
 assert digest(parentpath.read_bytes())==patch['nativeMesh']['source']['folklandLocalReplacement']['priorParentSHA256']
 save(DOC/'terrain-candidates.json',[dict(path=str(candidate_path.relative_to(ROOT)),sha256=digest(candidate_path.read_bytes()),uids=sorted(originals),replaces=dict(url=parent_url,sha256=digest(parentpath.read_bytes()),retainedUids=parent['meta']['targetUids']))])
 tool=HERE/'acceptance-metrics-multi-retained.mjs';cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str((HERE/'local'/SRC.name).relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==2 and all(not r.get('error')for r in metrics['rows'])
 runtime={r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']}
 gp=HERE/'local'/GROUND.name/'264677:0-ground.json.gz';native=np.asarray(consume(GROUND,gp)['completeOriginalTerrain'])
 final=module('folkland_complete_foundations',HERE/'xl-final-script-pass.py');worlds={'original':originals}
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in attr['rows']}
 summary=[]
 for r in rows:
  uid=r['uid'];b=r['source']['building'];polygon=Polygon(b['rings'][0],b['rings'][1:]);ground=np.asarray(runtime[uid]['drawnGroundGeometry']).reshape(-1,3,3)
  for mode,world in worlds.items():
   tri=world[uid];assert len(tri)==r['triangles'];f=final.foundation_context(tri,ground,polygon);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(uid=uid,mode=mode,foundation=f,installationApproved=False));summary.append(dict(uid=uid,mode=mode,**{k:v for k,v in f.items()if k!='components'}));print(summary[-1],flush=True)
  f=final.foundation_context(originals[uid],native,polygon);save(DOC/(uid.split('/')[1]+'-native.json'),dict(uid=uid,foundation=f,originalSheetOnly=True,installationApproved=False));summary.append(dict(uid=uid,mode='original-native-sheet',**{k:v for k,v in f.items()if k!='components'}));print(summary[-1],flush=True)
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert digest(mp.read_bytes())==mh and reservations.owns(lease);refs.extend([tool,HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',LOCAL/'runtime-geometry.json.gz'])
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0))
 module('folkland_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-candidate-four-representation-and-original-ground-foundations',list(dict.fromkeys(refs)),dict(uids=sorted(originals),rows=summary,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/264677:0','building:landsd/225387:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)));DOC.mkdir()
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
