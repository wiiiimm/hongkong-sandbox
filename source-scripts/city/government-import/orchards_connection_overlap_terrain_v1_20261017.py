"""Current original terrain checks with explicit Orchards connection identity only."""
import json,subprocess,sys,uuid
from pathlib import Path
from types import SimpleNamespace
from contextlib import contextmanager
import numpy as np
import government_georef_cell_identity as base_identity
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from orchards_named_connection_identity_v1_20261017 import interpret,UID
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CURRENT=BASE/'government-xl-three-current-originals-v1-20261017';REVIEW=BASE/'government-xl-orchards-named-connection-identity-v1-20261017';ATTR=BASE/'government-xl-orchards-lower-extension-attribution-v1-20261017';BATCH='government-xl-orchards-connection-overlap-terrain-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
ORIGINAL_VERIFY=base_identity.verify_files;ORIGINAL_POLICY=base_identity.POLICY;POLICY='orchards-byte-bound-original-lower-connection-identity-v1'
@contextmanager
def raw_identity_scope():
 previous=(base_identity.verify_files,base_identity.POLICY)
 base_identity.verify_files=ORIGINAL_VERIFY;base_identity.POLICY=ORIGINAL_POLICY
 try:yield
 finally:base_identity.verify_files,base_identity.POLICY=previous

def verify_files(row,context,local):
 with raw_identity_scope():raw=raw_verify(row,context,local)
 triangles=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());lo,hi=triangles.min((0,1)),triangles.max((0,1));final=module('orchards_current_forms',HERE/'xl-final-script-pass.py')
 forms=[f for f,_,_ in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])]
 value=interpret(raw,row,triangles,forms,read(ATTR/'attribution.json.gz'))
 assert value==read(REVIEW/'identity.json'),'Reviewed identity changed; fresh interpretation required'
 return value

def owned():
 assert reservations.owns(read(LOCAL/'reservation.json'))
 receipt=read(REVIEW/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'],e['path']
 selection=read(CURRENT/'selection.json.gz');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256'];row=next(r for r in selection['rows']if r['uid']==UID);context=next(r for r in read(CURRENT/'context.json.gz')['rows']if r['uid']==UID)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(UID,)).fetchone()is None
 row['currentReview']=None;inputs=LOCAL/'inputs';save(inputs/'check-selection.json.gz',dict(selection,rows=[row]));save(inputs/'context.json.gz',dict(rows=[context]))
 save(DOC/'explicit-identity-adapter.json',dict(policy=POLICY,reviewJobId=receipt['jobId'],reviewReceiptSHA256=digest((REVIEW/'result.json').read_bytes()),adapterSHA256=digest(Path(__file__).read_bytes()),interpretationSHA256=digest((HERE/'orchards_named_connection_identity_v1_20261017.py').read_bytes()),physicalGatesUnchanged=True,publication=False))
 # Test both direct and shimmed calls against the same current saved proof.
 direct=verify_files(row,context,LOCAL/'adapter-preflight')
 base_identity.verify_files=verify_files;base_identity.POLICY=POLICY
 try:
  repeated=base_identity.verify_files(row,context,LOCAL/'adapter-repeat');assert repeated==direct and base_identity.verify_files is verify_files
  worker=module('orchards_indexed_worker',HERE/'xl-cell-indexed-terrain-continuation.py')
  assert worker.verify_files is verify_files and worker.POLICY==POLICY
  original_module=worker.module
  def configured(name,filename):
   value=original_module(name,'xl-cell-retained-overlap-contact.py' if filename=='xl-cell-contact-resolution.py' else filename)
   if filename=='xl-cell-contact-resolution.py':
    value.RETAIN_NATIVE_URL='city/data/government-native-254621-0.json'
    value.RETAIN_NATIVE_MODEL_REGIONS_ONLY=False
   return value
  worker.module=configured
  worker.TERRAIN_PIPELINE_PATH=HERE/'xl-cell-retained-overlap-contact.py'
  worker.owned(SimpleNamespace(uid=UID,batch=BATCH,base=str(inputs.relative_to(ROOT))),DOC,LOCAL)
 finally:base_identity.verify_files=ORIGINAL_VERIFY;base_identity.POLICY=ORIGINAL_POLICY

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 retained='city/data/government-native-254621-0.json';manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert retained in {p['url'] for p in manifest['terrainPatches']}
 old=read(ROOT/'3d-viewer'/retained);parent=read(ROOT/'3d-viewer/city/data/terrain.json');second=module('orchards_scope_second',HERE/'xl-second-pass.py');patches=module('orchards_scope_patches',HERE/'native_patch_resolution.py');bounds=patches._patch_bounds(old)
 row=next(r for r in read(CURRENT/'selection.json.gz')['rows']if r['uid']==UID);lo,hi=row['native']['model']['worldBounds'];bounds=[min(bounds[0],lo[0]-2),min(bounds[1],lo[2]-2),max(bounds[2],hi[0]+2),max(bounds[3],hi[2]+2)]
 cells=second.resolution.rectangle_for([[bounds[0],0,bounds[1]],[bounds[2],0,bounds[3]]],parent);bounds=second.resolution.extent(cells,parent);final=module('orchards_scope_forms',HERE/'xl-final-script-pass.py');uids={UID,*old['meta']['targetUids'],*[f['uid']for f,_,_ in final.load_forms(bounds)]}
 resources=[('building:'if u.startswith('landsd/')else'source-form:')+u for u in sorted(uids)]+['terrain-patch:'+UID,'terrain-surface:'+retained]
 claim=reservations.claim('orchards-connection-retained-terrain-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
