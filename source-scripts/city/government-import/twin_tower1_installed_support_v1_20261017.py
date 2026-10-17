"""Recheck remaining Tower 1 against newly installed original podium and Tower 2."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-twin-tower1-installed-support-v1-20261017';DOC=BASE/BATCH;UID='landsd/223207:0'
OLD=BASE/'government-xl-extended-223207-20261005';COUNT=BASE/'government-xl-opus-original-installed-v1-20261017/full-xl-current-count.json';SHA='ba739fa1425007e305a489fe97738edf800795fbdcc38cc9e11705e6475253af'
def main():
 assert not DOC.exists();require_remaining(COUNT,UID,SHA);r=read(OLD/'result.json');p=OLD/'selection.json.gz'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))in r['evidenceRefs'];selection=read(p);row=next(r for r in selection['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA
 refs=[Path(__file__),COUNT,OLD/'result.json',p,asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'require_remaining_xl.py'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath);pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];refs.append(pointer);supports=[]
 for url in manifest['officialModelCatalogues']:
  q=ROOT/'3d-viewer'/url
  for e in read(q)['models']:
   assert e['uid']!=UID
   if e['uid']in ['landsd/222465:0','landsd/223206:0']:
    a=q.parent/e['asset'];assert digest(a.read_bytes())==e['sha256'];tri=decode_original_world_triangles(a.read_bytes());assert len(tri)==e['triangles'];supports.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],triangles=tri.tolist(),entry=e));refs.extend([q,a])
 assert {s['uid']for s in supports}=={'landsd/222465:0','landsd/223206:0'}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for s in supports:assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,s['uid'])).fetchone()==('installed-verified',s['sourceSHA256'])
 tile=ROOT/'3d-viewer'/row['source']['tile'];b=next(b for b in read(tile)['buildings']if b['uid']==UID);assert b==row['source']['building'];refs.append(tile);source=dict(uid=UID,sourceSHA256=SHA,triangles=decode_original_world_triangles(asset.read_bytes()).tolist());assert len(source['triangles'])==11796
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};claim=reservations.claim('twin-tower1-original-support-'+str(uuid.uuid4()),['building:'+u for u in [UID,'landsd/222465:0','landsd/223206:0']],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'input.json.gz',dict(source=source,supports=supports,snapshotId=snapshot,currentManifestSHA256=pins[str(manifestpath.relative_to(ROOT))],sourceGeometryChanges=0));tool=HERE/'twin_tower1_installed_support_v1_20261017.mjs'
  with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'interfaces.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
  data=read(DOC/'interfaces.json.gz');summary=[dict(supportUids=x['supportUids'],samples=x['proof']['samples'],strict=x['proof']['strictContacts'],walls=x['proof']['wallIntersections'],unresolved=len(x['proof']['unresolved']))for x in data['rows']]
  for p,h in {**pins,**data['inputHashes'],**data['closure']['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs.extend([tool,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs']);save(DOC/'summary.json',dict(rows=summary,sourceGeometryChanges=0,fullAcceptance=False,newlyInstalled=0,qualification='Fresh source-space canonical contact diagnostic against exact current installed support originals. Actual renderer/foundation/identity/runtime checks remain separate.'))
  result=module('twin_tower1_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-twin-tower1-installed-original-support-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=[UID],rows=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],rows=summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
