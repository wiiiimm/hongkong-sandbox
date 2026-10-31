"""Existing complete foundation guard with the unchanged native podium as support."""
from pathlib import Path
import importlib.util,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-esplanade-compound-foundation-v1-20261015';DOC=BASE/BATCH;PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';CAPTURE=BASE/'government-xl-esplanade-render-finite-v2-20261015';LOCAL=HERE/'local'/PHYSICAL.name

def main():
 assert not DOC.exists();receipt=read(CAPTURE/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 selection=read(PHYSICAL/'selection.json.gz')['rows'];captured=read(CAPTURE/'attributes.json.gz')['rows'];worlds={'original':{}};paths=[Path(__file__),CAPTURE/'result.json',CAPTURE/'attributes.json.gz',PHYSICAL/'selection.json.gz',LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']
 for r in selection:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];worlds['original'][r['uid']]=decode_original_world_triangles(p.read_bytes());paths.append(p)
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[key],float).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in captured}
 tower='landsd/268828:0';podium='landsd/309385:0';rt=next(r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']if r['uid']==tower);ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);b=next(r for r in selection if r['uid']==tower)['source']['building'];poly=Polygon(b['rings'][0],b['rings'][1:]);spec=importlib.util.spec_from_file_location('esplanade_existing_foundation',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
 claim=reservations.claim('esplanade-compound-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];rows=[]
 try:
  for mode,world in worlds.items():
   tri=world[tower];support=world[podium];assert len(tri)==23998 and len(support)==1476;compound=np.concatenate([ground,support]);foundation=f.foundation_context(tri,compound,poly);strict=foundation['completeTerrainTriangles']==len(tri)and not foundation['fullyBuriedUpwardTriangles']and foundation['fullyBuriedAreaFraction']==0;rows.append(dict(mode=mode,towerWorldSHA256=digest(tri.tobytes()),podiumWorldSHA256=digest(support.tobytes()),completeTerrainSHA256=digest(ground.tobytes()),compoundGroundSHA256=digest(compound.tobytes()),foundation=foundation,strictFoundationAccepted=strict));assert reservations.heartbeat(lease)['ok'];print(mode,'strictFoundationAccepted',strict,flush=True)
  save(DOC/'compound-foundation.json',dict(rows=rows,allFourPass=all(r['strictFoundationAccepted']for r in rows),installationApproved=False))
  for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
  spec=importlib.util.spec_from_file_location('esplanade_compound_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-original-compound-foundation-four-representations-v1',paths,dict(uids=[tower,podium],rows=rows,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
