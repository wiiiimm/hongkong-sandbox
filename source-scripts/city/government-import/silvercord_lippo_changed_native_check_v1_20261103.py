"""Run the unchanged installed native/fallback checker for the changed actor.

All retained parent actors remain in the canonical checker. Unchanged-context
proofs and raw failures stay separate; no source/support/publication approval.
"""
import sys,uuid,subprocess,copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-silvercord-lippo-changed-native-check-v1-20261103';LOCAL=HERE/'local'/BATCH
CONTEXT='government-xl-silvercord-lippo-all-native-terrain-context-v1-20261103'
FORMS='government-xl-silvercord-lippo-complete-floor-full-form-regression-v4-20261103'
CANDIDATE='government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
UIDS=['landsd/233997:0','landsd/231645:0']

def inputs():
 context,_=authenticate(BASE/CONTEXT);forms,_=authenticate(BASE/FORMS);proposal,_=authenticate(BASE/CANDIDATE)
 assert context['remainingFullMeshUids']==['landsd/239465:0'] and forms['forms']==5408 and forms['ordinaryFlagged']==0
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest_path.read_bytes())==context['currentManifestSHA256']==proposal['currentManifestSHA256'];manifest=read(manifest_path);models={};catalogues=[]
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogues.append(path)
  for m in read(path)['models']:assert m['uid']not in models;models[m['uid']]=m
 parent_path=ROOT/'3d-viewer'/proposal['replacedParent']['url'];assert digest(parent_path.read_bytes())==proposal['replacedParent']['sha256'];parent=read(parent_path)
 selected=set(parent['meta']['targetUids'])|set(context['remainingFullMeshUids']);todo=list(selected)
 while todo:
  for d in models[todo.pop()].get('supportDependencies',[]):
   uid=d['uid']if isinstance(d,dict)else d
   if uid in models and uid not in selected:selected.add(uid);todo.append(uid)
 return context,forms,proposal,manifest,models,selected,catalogues

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 context,forms,proposal,manifest,models,selected,catalogues=inputs();out=BASE/BATCH;refs=[Path(__file__),BASE/CONTEXT/'result.json',BASE/FORMS/'result.json',BASE/CANDIDATE/'result.json',*catalogues]
 all_rows={};checks={};patches=None;hashes=None
 for chunk in forms['finiteChunks']:
  folder=BASE/chunk['batch'];receipt,pins=authenticate(folder);assert receipt['jobId']==chunk['jobId']
  for name in ['neighbour-inputs.json.gz','neighbour-checks.json']:
   path=folder/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
  inp=read(folder/'neighbour-inputs.json.gz');raw=read(folder/'neighbour-checks.json')
  if patches is None:patches=inp['patches'];hashes=raw['inputHashes']
  else:assert inp['patches']==patches
  for path,sha in raw['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
  for r in inp['rows']:assert r['building']['uid']not in all_rows;all_rows[r['building']['uid']]=r
  for r in raw['rows']:assert r['uid']not in checks;checks[r['uid']]=r
 assert len(all_rows)==len(checks)==5408
 needed=set(selected)
 for uid in selected:
  needed.update(d['uid']if isinstance(d,dict)else d for d in models[uid].get('supportDependencies',[]))
 assert needed<=all_rows.keys(),'Exact current selected/support forms missing; extend actual checks, do not invent bindings'
 save(out/'neighbour-inputs.json.gz',dict(inputHashes={'3d-viewer/city/data/manifest.json':context['currentManifestSHA256']},candidateIds=UIDS,patches=patches,requiredNativeUids=sorted(set(context['remainingFullMeshUids'])),rows=list(all_rows.values())))
 save(out/'neighbour-checks.json',dict(rows=list(checks.values()),inputHashes=hashes,publication=False))
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);refs.append(pointer_path)
 review_uids=set(selected)
 for uid in selected:
  review_uids.update(d['uid']for d in models[uid].get('supportDependencies',[])if isinstance(d,dict)and d['uid']in models)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');rows=db.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(pointer['snapshotId'],sorted(review_uids))).fetchall()
 reviews={uid:(state,sha)for uid,state,sha in rows};assert set(reviews)==review_uids
 for uid in review_uids:assert reviews[uid]==('installed-verified',models[uid]['sha256'])
 bindings=[]
 for uid in selected:
  for dependency in models[uid].get('supportDependencies',[]):
   d=dependency;other=d['uid'];form=all_rows[other]['building']
   if d['state']=='candidate'or(d['state']=='installed'and not isinstance(d.get('csuid'),str)):
    support=models[other];bindings.append(dict(owner=uid,ownerSHA256=models[uid]['sha256'],rawDependency=d,reviewState='installed-verified',snapshotId=pointer['snapshotId'],uid=other,sourceSHA256=support['sha256'],csuid=support['buildingCSUID']))
   elif d['state']in ['fallback','surveyed-footprint-fallback']and not d.get('csuid'):
    tile=next(t for t in manifest['tiles']if t['id']==form['tile']);path=ROOT/'3d-viewer'/tile['url'];refs.append(path)
    bindings.append(dict(kind='exact-current-surveyed-fallback',owner=uid,ownerSHA256=models[uid]['sha256'],ownerReviewState='installed-verified',snapshotId=pointer['snapshotId'],rawDependency=d,uid=other,csuid=form['buildingCSUID'],sourceForm=form,sourceTile=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))))
 save(out/'installed-dependency-bindings.json',dict(currentManifest=dict(path='3d-viewer/city/data/manifest.json',sha256=context['currentManifestSHA256']),snapshotId=pointer['snapshotId'],bindings=bindings,originalMetadataChanged=False))
 tool=HERE/'check-native-neighbours-current-installed-v5-20261028.mjs';refs.append(tool)
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=7200)
 native=read(out/'native-neighbour-checks.json')
 for path,sha in native['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 by={r['uid']:r for r in native['rows']};assert set(context['remainingFullMeshUids'])<=by.keys()
 changed=[by[u]for u in context['remainingFullMeshUids']]
 result=dict(uids=UIDS,completeRequiredNativeScope=len(context['allRequiredNativeUids']),unchangedCompleteTerrainContexts=context['exactUnchangedNativeContexts'],changedNativeRows=changed,rawNativeRows=native['rows'],changedNativeFullMeshPassed=all(r['passed']for r in changed),originalCatalogueSupportMetadataUnchanged=True,existingNativeOrSupportReaccepted=False,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,next='Exact original native-podium/tower support migration, current source physical evidence, whole terrain admission and browser/publication remain mandatory. Raw unrelated legacy support negatives are retained, not reapproved.')
 save(out/'summary.json',result);assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==context['currentManifestSHA256']
 module('pair_changed_native_check_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-installed-native-full-indexed-mesh-terrain-and-existing-support-regression',list(dict.fromkeys(refs)),result)
 print(dict(changedNativeFullMeshPassed=result['changedNativeFullMeshPassed'],changedNativeRows=changed,installationApproved=False),flush=True)
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()and not(BASE/BATCH).exists();_,_,_,_,models,selected,_=inputs();keys={'building:'+u for u in set(UIDS)|selected}
  for uid in selected:
   for d in models[uid].get('supportDependencies',[]):
    other=d['uid']if isinstance(d,dict)else d;keys.add(('building:'if other.startswith('landsd/')else'source-form:')+other)
  claim=reservations.claim('pair-current-native-mesh-'+str(uuid.uuid4()),sorted(keys|{'immutable-source-proof:'+BATCH}),batch=BATCH,ttl=3600);assert claim['ok'];execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
