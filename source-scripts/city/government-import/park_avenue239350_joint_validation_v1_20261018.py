"""Private three-source terrain candidate; joint installed actors remain unapproved."""
from pathlib import Path
import json,sys,uuid,subprocess,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-park-avenue239350-joint-validation-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/239350:0','landsd/240161:0','landsd/227455:0']
INPUT=BASE/'government-xl-park-avenue239350-terrain-inputs-v1-20261018'
MAIN=BASE/'government-xl-park-avenue239350-current-identity-runtime-v3-20261018'
COMP=BASE/'government-xl-park-avenue239350-companion-identity-runtime-v1-20261018'
REVIEW=BASE/'government-xl-park-avenue239350-identity-review-v1-20261018'
JOINT=BASE/'government-xl-park-avenue239350-joint-scope-v1-20261018'
PRIOR=BASE/'government-xl-olympian-two-current-retained-terrain-v1-20261018'
def owned():
 import shutil
 import numpy as np
 from shapely.geometry import Polygon
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 prior=BASE/'government-xl-park-avenue239350-joint-terrain-v3-20261018';receipt=read(prior/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert read(prior/'final-terrain-budget.json')['passed']
 old=HERE/'local'/prior.name
 for name in ['assets','catalogue.json','catalogue-index.json','source-forms.json']:
  source=old/name;target=LOCAL/name
  if source.is_dir():shutil.copytree(source,target)
  else:shutil.copy2(source,target)
 for name in ['selection.json.gz','final-terrain-budget.json','retained-native-proof.json','source-local-parent-preservation.json']:
  save(DOC/name,read(prior/name))
 candidates=read(prior/'terrain-candidates.json');assert len(candidates)==1
 for row in candidates:
  replacements=row.pop('replacesMany');assert len(replacements)==1
  row['replaces']=replacements[0]
  assert digest((ROOT/row['path']).read_bytes())==row['sha256']
 save(DOC/'terrain-candidates.json',candidates)
 terrain=read(prior/'terrain.json');terrain['patch']=candidates[0];save(DOC/'terrain.json',terrain)
 inputs=read(prior/'neighbour-inputs.json.gz');inputs['patches']=candidates
 inputs['requiredNativeUids']=read(BASE/'government-xl-park-avenue239350-native-scope-v1-20261018/scope.json')['touchingNativeUids'];save(DOC/'neighbour-inputs.json.gz',inputs)
 def rel(p):return str(p.relative_to(ROOT))
 def call(args,allowed=(0,)):
  rc=subprocess.run(args,cwd=ROOT).returncode
  assert rc in allowed,(args,rc)
  assert reservations.owns(lease)
 error=None
 try:
  call(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
  call(['node',str(HERE.parent/'building-batch/validate_candidates_multi_retained.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
  call(['node',str(HERE/'check-neighbours-multi-retained.mjs'),rel(DOC)+'/'])
  call(['node',str(HERE/'check-native-neighbours-multi-retained-scoped-v3.mjs'),rel(DOC)+'/'])
  final=module('park_resume_foundation',HERE/'xl-final-script-pass.py');runtime={r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']};foundations=[]
  for row in read(DOC/'selection.json.gz')['rows']:
   g=runtime[row['uid']];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);form=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(form['rings'][0],form['rings'][1:]))
   foundations.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0))
  save(DOC/'foundation.json',dict(rows=foundations,modelGeometryChanges=0))
 except AssertionError as exc:
  error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),publication=False))
 refs=[Path(__file__),prior/'result.json',*[ROOT/p for p in pins]]
 refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json')
 refs.extend(HERE/n for n in ['acceptance-metrics-multi-retained.mjs','check-neighbours-multi-retained.mjs','check-native-neighbours-multi-retained-scoped-v3.mjs','terrain-replacements.mjs','xl-final-script-pass.py'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease)
 summary=dict(uids=UIDS,guardFailure=error,fullAcceptance=False,newlyInstalled=0,publication=False,modelGeometryChanges=0)
 out=module('park_resume_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-single-parent-private-validation-v1',list(set(refs)),summary)
 print(dict(jobId=out['jobId'],**summary),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope=read(INPUT/'scope.json');final=module('pair_scope_forms',HERE/'xl-final-script-pass.py');uids={b['uid']for b,_,_ in final.load_forms(scope['fullParentBounds'])}|set(UIDS)
 keys={('building:'if u.startswith('landsd/')else'source-form:')+u for u in uids}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['url']for r in scope['retainedParents']}
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
