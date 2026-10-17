"""Apply existing strict support and full compound-foundation gates to Villa."""
from pathlib import Path
import subprocess,uuid,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-current-strict-support-v1-20261015';DOC=BASE/NAME;SOURCE=BASE/'government-xl-villa-five-current-physical-v4-20261015';PODIUM='landsd/89917:0'
def main():
 assert not DOC.exists();receipt=read(SOURCE/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 rows=read(SOURCE/'selection.json.gz')['rows'];uids=[r['uid']for r in rows];claim=reservations.claim('villa-support-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=NAME,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'support-inputs.json',dict(sources=rows,pairs=[dict(uid=u,supportUid=PODIUM)for u in uids if u!=PODIUM]));tool=HERE/'original-support-closure-interfaces.mjs';subprocess.check_call(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT)
  checks=read(DOC/'support-checks.json.gz');runtime=read(HERE/'local'/SOURCE.name/'runtime-geometry.json.gz');f=module('villa_compound_foundation_current',HERE/'xl-final-script-pass.py');originals={r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes())for r in rows};foundations=[]
  for row in rows:
   if row['uid']==PODIUM:continue
   actual=next(r for r in runtime['rows']if r['uid']==row['uid']);ground=np.asarray(actual['drawnGroundGeometry']).reshape(-1,3,3);support=np.concatenate([ground,originals[PODIUM]]);b=row['source']['building'];proof=f.foundation_context(originals[row['uid']],support,Polygon(b['rings'][0],b['rings'][1:]));strict=proof['completeTerrainTriangles']==len(originals[row['uid']])and not proof['fullyBuriedUpwardTriangles']and proof['fullyBuriedAreaFraction']==0;foundations.append(dict(uid=row['uid'],foundation=proof,strictFoundationAccepted=strict));print(row['uid'],'compoundFoundation',strict,flush=True)
  summary=dict(uids=uids,interfaces=[dict(uid=r['uid'],passed=r['interface']['passed'],samples=r['interface']['samples'],strictContacts=r['interface']['strictContacts'],wallIntersections=r['interface']['wallIntersections'],unresolved=len(r['interface']['unresolved']))for r in checks['rows']],foundations=foundations,fullAcceptance=False)
  save(DOC/'summary.json',summary)
  for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
  paths=[ROOT/q['path']for q in receipt['evidenceRefs']]+[SOURCE/'result.json',Path(__file__),tool,HERE/'xl-final-script-pass.py']+[ROOT/p for p in checks['inputHashes']]
  module('villa_strict_support_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'existing-strict-original-support-and-compound-foundation',paths,summary)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
