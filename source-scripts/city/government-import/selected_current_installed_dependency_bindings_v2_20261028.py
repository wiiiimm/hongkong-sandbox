"""Prove current exact installed support dependencies without editing old catalogues."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--scope',required=True);a=ap.parse_args();BATCH=a.batch
 assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.scope])
 doc=BASE/BATCH;assert not doc.exists();scope=BASE/a.scope;_,pins=authenticate(scope);sp=scope/'scope.json';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))];uids=read(sp)['touchingNativeUids'];mp=ROOT/'3d-viewer/city/data/manifest.json';pp=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pp)['snapshotId'];refs=[Path(__file__),scope/'result.json',sp,mp,pp];models={};catalogues={}
 for url in read(mp)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p)
  for m in read(p)['models']:assert m['uid']not in models;models[m['uid']]=m;catalogues[m['uid']]=p
 forms_path=scope/'form-obligations.json.gz';assert digest(forms_path.read_bytes())==pins[str(forms_path.relative_to(ROOT))];refs.append(forms_path)
 forms={f['uid']:f for f in read(forms_path)};tiles={t['id']:t for t in read(mp)['tiles']}
 bindings=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid in uids:
   for dep in models[uid].get('supportDependencies',[]):
    assert isinstance(dep,dict)
    if dep['state'] in ['fallback','surveyed-footprint-fallback'] and not dep.get('csuid'):
     assert dep['uid'] not in models
     form=forms[dep['uid']];assert form.get('buildingCSUID') and not form.get('modelGeometry')
     tile=ROOT/'3d-viewer'/tiles[form['tile']]['url'];key=str(tile.relative_to(ROOT));sha=digest(tile.read_bytes());assert sha==pins[key]
     assert [b for b in read(tile)['buildings'] if b['uid']==dep['uid']]==[form];refs.append(tile)
     owner=models[uid];state=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone();assert state==('installed-verified',owner['sha256'])
     asset=catalogues[uid].parent/owner['asset'];assert digest(asset.read_bytes())==owner['sha256'];refs.append(asset)
     bindings.append(dict(kind='exact-current-surveyed-fallback',owner=uid,ownerSHA256=owner['sha256'],ownerReviewState=state[0],snapshotId=snapshot,rawDependency=dep,uid=dep['uid'],csuid=form['buildingCSUID'],sourceForm=form,sourceTile=dict(path=key,sha256=sha),physicalSupportCredit=False))
     continue
    if dep['state']!='candidate' and not(dep['state']=='installed' and not dep.get('csuid')):continue
    support=models[dep['uid']];assert dep['state']!='candidate' or dep.get('sha256');assert not dep.get('sha256') or dep['sha256']==support['sha256'];assert not dep.get('csuid')or dep['csuid']==support['buildingCSUID']
    state=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,support['uid'])).fetchone();assert state==('installed-verified',support['sha256']),(uid,dep,state)
    asset=catalogues[support['uid']].parent/support['asset'];assert digest(asset.read_bytes())==support['sha256'];refs.append(asset)
    bindings.append(dict(owner=uid,ownerSHA256=models[uid]['sha256'],rawDependency=dep,uid=support['uid'],csuid=support['buildingCSUID'],sourceSHA256=support['sha256'],snapshotId=snapshot,reviewState=state[0]))
 result=dict(uids=read(sp)['uids'],requiredNativeUids=uids,currentManifest=dict(path=str(mp.relative_to(ROOT)),sha256=digest(mp.read_bytes())),snapshotId=snapshot,bindings=bindings,installationApproved=False,publication=False,newlyInstalled=0,qualification='Exact current installed-ledger/source hashes only; no physical support or identity acceptance transfer; original dependency metadata retained.')
 save(doc/'bindings.json',result);refs.append(doc/'bindings.json');module('olympic_dependency_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-installed-dependency-context',refs,result);print(dict(bindings=len(bindings)),flush=True)
if __name__=='__main__':main()
