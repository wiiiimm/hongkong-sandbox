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
 bindings=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid in uids:
   for dep in models[uid].get('supportDependencies',[]):
    assert isinstance(dep,dict)
    if dep['state']!='candidate' and not(dep['state']=='installed' and not dep.get('csuid')):continue
    support=models[dep['uid']];assert dep['state']!='candidate' or dep.get('sha256');assert not dep.get('sha256') or dep['sha256']==support['sha256'];assert not dep.get('csuid')or dep['csuid']==support['buildingCSUID']
    state=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,support['uid'])).fetchone();assert state==('installed-verified',support['sha256']),(uid,dep,state)
    asset=catalogues[support['uid']].parent/support['asset'];assert digest(asset.read_bytes())==support['sha256'];refs.append(asset)
    bindings.append(dict(owner=uid,ownerSHA256=models[uid]['sha256'],rawDependency=dep,uid=support['uid'],csuid=support['buildingCSUID'],sourceSHA256=support['sha256'],snapshotId=snapshot,reviewState=state[0]))
 result=dict(uids=read(sp)['uids'],requiredNativeUids=uids,currentManifest=dict(path=str(mp.relative_to(ROOT)),sha256=digest(mp.read_bytes())),snapshotId=snapshot,bindings=bindings,installationApproved=False,publication=False,newlyInstalled=0,qualification='Exact current installed-ledger/source hashes only; no physical support or identity acceptance transfer; original dependency metadata retained.')
 save(doc/'bindings.json',result);refs.append(doc/'bindings.json');module('olympic_dependency_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-installed-dependency-context',refs,result);print(dict(bindings=len(bindings)),flush=True)
if __name__=='__main__':main()
