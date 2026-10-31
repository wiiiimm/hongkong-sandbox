"""Prove six candidate labels refer to exact already installed originals."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from verified_installed_dependency_metadata_20261010 import proposal,verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-dependency-plan-v1-20261020';DOC=BASE/BATCH;INST=BASE/'government-xl-yoho-seven-original-installed-v1-20261020';CAT='3d-viewer/city/data/official-models/government-xl-yoho-seven-private-stage-v1-20261020/catalogue.json'
def main():
    assert not DOC.exists();receipt=read(INST/'result.json');manifestpath=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];cat=read(ROOT/CAT);uids={e['uid'] for e in cat['models']};assert uids==set(receipt['installedUids']);reviews={};refs=[Path(__file__),INST/'result.json',manifestpath,pointer,ROOT/CAT,HERE/'verified_installed_dependency_metadata_20261010.py'];forms={};assets={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
        for e in cat['models']:
            state=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,e['uid'])).fetchone();assert state==('installed-verified',e['sha256']);assert e['sha256']==receipt['sourceSHA256ByUid'][e['uid']];reviews[e['uid']]=state
    for tile in read(manifestpath)['tiles']:
        if len(forms)==7:break
        path=ROOT/'3d-viewer'/tile['url']
        for b in read(path)['buildings']:
            if b['uid'] in uids:forms[b['uid']]=b;refs.append(path)
    assert len(forms)==7
    for e in cat['models']:
        p=(ROOT/CAT).parent/e['asset'];raw=p.read_bytes();assert digest(raw)==e['sha256'] and len(raw)==e['bytes'];assets[e['uid']]=dict(sha256=digest(raw),bytes=len(raw));refs.append(p)
    plan=proposal({CAT:cat},reviews,forms,assets);assert len(plan['changes'])==6 and not plan['retainedRelations'];verify({CAT:cat},plan['catalogues'],reviews,forms,assets)
    packet=dict(before=cat,after=plan['catalogues'][CAT],cataloguePath=CAT,changes=plan['changes'],forms=list(forms.values()),snapshotId=snapshot,manifestSHA256=digest(manifestpath.read_bytes()),catalogueBeforeSHA256=digest((ROOT/CAT).read_bytes()),newlyInstalled=0)
    save(DOC/'proposal.json',packet);(DOC/'before-catalogue.json').write_bytes((ROOT/CAT).read_bytes());save(DOC/'proposed-catalogue.json',packet['after']);tool=HERE/'yoho_seven_dependency_replay_v1_20261020.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(tool)
    check=read(DOC/'loader-check.json');assert check['passed'] and check['geometryIdentical']
    for p,h in check['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    module('lai_chi_kok_metadata_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-verified-installed-dependency-labels',list(dict.fromkeys(refs)),dict(uids=sorted(uids),dependencyChanges=6,newlyInstalled=0,geometryChanges=0,metadataApplied=False,snapshotId=snapshot))
if __name__=='__main__':main()
