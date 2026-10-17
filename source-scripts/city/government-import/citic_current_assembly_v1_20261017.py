"""Current source identity, canonical support and complete compound foundation diagnostic."""
from pathlib import Path
import copy,subprocess,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-current-assembly-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CURRENT=BASE/'government-xl-citic-current-pair-v1-20261017';OLD=BASE/'government-xl-four-towers-original-supports-20261006';PODIUM='landsd/232579:0';TOWER='landsd/278303:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CURRENT,OLD,BASE/'government-xl-citic-current-finite-v1-20261017']:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=consume(CURRENT/'selection.json.gz')['rows'];geo=consume(HERE/'local'/CURRENT.name/'runtime-geometry.json.gz')['rows'];old={r['uid']:r for r in consume(OLD/'support-inputs.json')['sources']};sources=[]
 for r in rows:
  x=copy.deepcopy(old[r['uid']]);assert x['sourceSHA256']==r['sourceSHA256'];x.update(source=r['source'],candidate=r['candidate']);sources.append(x)
 claim=reservations.claim('citic-original-assembly-'+str(uuid.uuid4()),['building:'+u for u in [PODIUM,TOWER]],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'support-inputs.json',dict(pairs=[dict(uid=TOWER,supportUid=PODIUM)],sources=sources));tool=HERE/'original-support-closure-interfaces.mjs'
  with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
  check=read(DOC/'support-checks.json.gz');assert len(check['rows'])==1;refs.append(tool)
  for p,h in check['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  final=module('citic_current_assembly_context',HERE/'xl-final-script-pass.py');tri={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in geo};grounds={g['uid']:np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)for g in geo};out=[]
  for r in sources:
   uid=r['uid'];t=tri[uid];ground=grounds[uid]if uid==PODIUM else np.concatenate([grounds[uid],tri[PODIUM]]);b=r['source']['building'];foundation=final.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));lo,hi=t.min((0,1)),t.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(uid=uid,sourceSHA256=r['sourceSHA256'],identity=final.identity_context(r,t,forms),neighbourTileHashes={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms});save(DOC/(uid.replace('/','-').replace(':','-')+'-context.json'),context)
   identity=verify_files(r,context,LOCAL/uid.replace('/','-').replace(':','-'));save(DOC/(uid.replace('/','-').replace(':','-')+'-identity.json'),identity)
   out.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],foundation=foundation,strictFoundationAccepted=foundation['completeTerrainTriangles']==foundation['triangles']and not foundation['fullyBuriedUpwardTriangles']and foundation['fullyBuriedAreaFraction']==0,identityPassed=identity['passed'],identityReasons=identity['reasons']))
   refs.extend(ROOT/'3d-viewer'/tile for _,_,tile in forms);assert reservations.heartbeat(lease)['ok'];print({k:v for k,v in out[-1].items()if k!='foundation'},flush=True)
  save(DOC/'summary.json',dict(rows=out,interface=check['rows'][0]['interface'],fullAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0));refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',*[p for p in LOCAL.rglob('*')if p.is_file()]])
  result=module('citic_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-citic-identity-interface-compound-foundation-v1',list(dict.fromkeys(refs)),dict(uids=[PODIUM,TOWER],rows=out,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
