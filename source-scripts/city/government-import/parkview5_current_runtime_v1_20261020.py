"""Rebind Parkview Block 5 original and installed podium to current runtime; no approval."""
from pathlib import Path
import copy,subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview5-current-runtime-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-star-parkview-support-v1-20261020';UIDS=['landsd/256113:0'];POD='landsd/254491:0'
assert not DOC.exists();receipt=read(CAP/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};selection=CAP/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestSHA=digest(manifestpath.read_bytes());pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointerpath);refs=[Path(__file__),CAP/'result.json',selection,manifestpath,pointerpath]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 review=c.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],POD)).fetchone();assert review and review[0]=='installed-verified'
 evidence=ROOT/review[2]['evidence'];assert digest(evidence.read_bytes())==review[2]['sha256'];refs.append(evidence)
rows=[copy.deepcopy(r)for r in read(selection)['rows']if r['uid']in UIDS+[POD]];assert len(rows)==2
found=[]
for url in manifest['officialModelCatalogues']:
 p=ROOT/'3d-viewer'/url
 for e in read(p)['models']:
  if e['uid']==POD:found.append((e,p))
assert len(found)==1;entry,catalogue=found[0];assert entry['sha256']==review[1];refs.append(catalogue)
for r in rows:
 if r['uid']==POD:
  for k in ['uid','sha256','buildingCSUID','objectId','worldBounds']:assert entry[k]==r['candidate']['entry'][k]
  r['candidate']['entry']=copy.deepcopy(entry);r['candidate']['path']=str((catalogue.parent/entry['asset']).relative_to(ROOT))
 source=ROOT/r['candidate']['path'];assert digest(source.read_bytes())==r['sourceSHA256'];refs.append(source);target=LOCAL/r['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());r['candidate']['path']=str(target.relative_to(ROOT));refs.append(target)
 tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];r['source']['tileSHA256']=digest(tile.read_bytes());refs.append(tile)
save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestSHA));save(DOC/'installed-podium-provenance.json',dict(uid=POD,reviewState=review[0],sourceSHA256=review[1],installedReview=review[2],snapshotId=pointer['snapshotId'],currentCatalogueFlags={k:entry.get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved']},flagsReconciled=False,installationApproved=False))
tool=HERE/'acceptance-metrics-multi-retained.mjs';cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
with (DOC/'metrics.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode));assert p.returncode==0
metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==2 and all(not r.get('error')for r in metrics['rows']);oldpath=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(oldpath.read_bytes())==pins[str(oldpath.relative_to(ROOT))];refs.append(oldpath);old={r['uid']:r for r in read(oldpath)['rows']};current=read(LOCAL/'runtime-geometry.json.gz')['rows'];bindings=[]
for r in current:
 o=old[r['uid']];ground=np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);before=np.asarray(o['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 world=np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];prior=np.asarray(o['position'],dtype='<f8').reshape(-1,3)[np.asarray(o['index']).reshape(-1,3)]
 bindings.append(dict(uid=r['uid'],completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),sameCompleteWorld=bool(np.array_equal(world,prior)),sameCompleteDrawnGround=bool(np.array_equal(ground,before)),completeFaces=len(world),completeGroundFaces=len(ground)))
assert digest(manifestpath.read_bytes())==manifestSHA and read(pointerpath)==pointer
for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
refs.extend([tool,LOCAL/'runtime-geometry.json.gz']);save(DOC/'current-binding.json',dict(rows=bindings,installationApproved=False,currentManifestSHA256=manifestSHA));print(bindings,flush=True)
module('parkview_current_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-block5-and-installed-podium-runtime',list(dict.fromkeys(refs)),dict(uids=UIDS+[POD],rows=bindings,installationApproved=False))
