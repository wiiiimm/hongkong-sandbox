"""Fresh original identity and installed-support preflight; no publication or geometry edits."""
import importlib.util,json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from require_remaining_xl import require_remaining
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-aqua272788-current-identity-v1-20261017'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/272788:0';SUPPORT='landsd/193086:0'
PRIOR=BASE/'government-xl-current-ground-seven-original-supports-20261007'
def mod(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists()
 row=next(r for r in read(PRIOR/'support-inputs.json')['sources'] if r['uid']==UID)
 count=BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json'
 require_remaining(count,UID,row['sourceSHA256'])
 claim=reservations.claim('aqua272788-current-identity-'+str(uuid.uuid4()),['building:'+UID,'building:'+SUPPORT],batch=BATCH,ttl=1800);assert claim['ok'],claim
 lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId']
  installed={}
  for url in read(manifest)['officialModelCatalogues']:
   p=ROOT/'3d-viewer'/url
   for entry in read(p)['models']:
    assert entry['uid'] not in installed;installed[entry['uid']]=(p,entry)
  assert UID not in installed
  cat,entry=installed[SUPPORT];source=cat.parent/entry['asset'];assert digest(source.read_bytes())==entry['sha256']
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,SUPPORT)).fetchone()==('installed-verified',entry['sha256'])
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
  tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']==row['native']['model']['triangles']
  lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));final=mod('aqua272788_forms','xl-final-script-pass.py');forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form,_,tile=next(f for f in forms if f[0]['uid']==UID)
  row['source']=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
  context=dict(uid=UID,sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms})
  proof=verify_files(row,context,LOCAL/'identity')
  old=next(r for r in read(PRIOR/'support-checks.json.gz')['rows'] if r['uid']==UID and r['supportUid']==SUPPORT)
  assert old['sourceSHA256']==row['sourceSHA256'] and old['supportSHA256']==entry['sha256']
  save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity.json',proof)
  save(DOC/'support-preflight.json',dict(supportUid=SUPPORT,sourceSHA256=entry['sha256'],snapshotId=snapshot,reviewState='installed-verified',historicalInterface=old,currentContactRecheckRequired=True))
  assert digest(manifest.read_bytes())==mh and read(pointer)['snapshotId']==snapshot and reservations.owns(lease)
  paths=[Path(__file__),count,manifest,pointer,cat,source,ROOT/row['candidate']['path'],PRIOR/'support-inputs.json',PRIOR/'support-checks.json.gz']+[ROOT/'3d-viewer'/t for _,_,t in forms]+[p for p in (LOCAL/'identity').rglob('*') if p.is_file()]
  paths += [HERE/n for n in ['xl-final-script-pass.py','require_remaining_xl.py','exact_packed_world_geometry_20261009.py','exact_original_georef_cell_identity_20261009.py','routed_original_cell_identity.py','government_georef_cell_identity.py','exact_original_projection_coverage_20261009.py']]
  result=mod('aqua272788_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-original-identity-installed-support-preflight-v1',paths,dict(uids=[UID],sourceSHA256=row['sourceSHA256'],identityAccepted=proof['passed'],identityReasons=proof['reasons'],supportInstalledVerified=True,completeOriginalFaces=len(tri),currentNeighbourForms=len(forms),nextStep='Fresh whole-original physical and current support checks' if proof['passed'] else 'Review exact original identity evidence; preserve all raw reasons.'))
  print(json.dumps({k:result[k] for k in ['jobId','identityAccepted','identityReasons','supportInstalledVerified','completeOriginalFaces']}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
