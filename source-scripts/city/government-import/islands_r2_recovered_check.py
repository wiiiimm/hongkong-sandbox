"""Verify the approved 17 exact recovered originals and replay ordinary checks.

No source edits, terrain edits, acceptance transfer, R2 access or publication.
Historical source failures remain immutable; this is a new fenced check cohort.
"""
import argparse
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module
from run import reservations

BATCH='government-islands-cheung-r2-recovered-check-20261107-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
RECOVERY=ROOT/'docs/astra-city/government-import/government-islands-cheung-r2-recovery-20261107-v1'
ASSETS=HERE/'local'/RECOVERY.name/'recovered'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    if not a.owned:
        assert not DOC.exists() and not LOCAL.exists()
        plan=read(RECOVERY/'plan.json');report=read(ASSETS/'recovery-report.json')
        assert report['planSHA256']==sha(RECOVERY/'plan.json')=='7038555e77c0c43f8402d4260548e435ca1922272bea30655ae9a21f85d201ca'
        assert report['requested']==report['recovered']==len(plan['targets'])==17 and not report['missing']
        targets={r['uid']:r for r in plan['targets']};actual={r['uid']:r for r in report['rows']};assert set(targets)==set(actual)
        assert {r['archiveSHA256']for r in actual.values()}<={r['sha256']for r in plan['archives']}
        for uid,t in targets.items():
            source=ASSETS/(t['sourceSHA256']+'.glb.gz');assert source.stat().st_size==actual[uid]['bytes']==t['bytes']
            assert sha(source)==actual[uid]['sourceSHA256']==t['sourceSHA256'] and gzip.decompress(source.read_bytes())[:4]==b'glTF'
        assert {p.name for p in ASSETS.iterdir()}=={r['sourceSHA256']+'.glb.gz'for r in targets.values()}|{'recovery-report.json'}
        oldpath=ROOT/'docs/astra-city/government-import/government-islands-cheung-chau-resume-20261106-v2/selection.json.gz'
        old={r['uid']:r for r in read(oldpath)['rows']};manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=sha(manifest)
        installed={m['uid']for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};assert not installed.intersection(targets)
        rows=[];pins={rel(manifest):manifest_sha,rel(RECOVERY/'plan.json'):sha(RECOVERY/'plan.json'),rel(oldpath):sha(oldpath),rel(Path(__file__)):sha(Path(__file__))}
        for uid,t in targets.items():
            row=copy.deepcopy(old[uid]);assert row['sourceSHA256']==t['sourceSHA256']
            path=ROOT/'3d-viewer'/row['source']['tile'];forms={r['uid']:r for r in read(path)['buildings']}
            assert forms[uid]==row['source']['building'] and row['humanStatus']=='in-process' and not row['installedProof']
            row['source']['tileSHA256']=sha(path);pins[rel(path)]=sha(path);pins[rel(ASSETS/(t['sourceSHA256']+'.glb.gz'))]=t['sourceSHA256'];rows.append(row)
        assert sha(manifest)==manifest_sha
        claim=reservations.claim('codex-islands-r2-check-'+str(uuid.uuid4()),['building:'+uid for uid in targets],batch=BATCH,ttl=3600)
        assert claim['ok'],'Existing owner; no takeover'
        receipt=json.loads(json.dumps(claim['reservation'],default=str));save(LOCAL/'reservation.json',receipt)
        frozen={'batch':BATCH,'rows':rows,'manifestSHA256':manifest_sha,'inputHashes':pins,'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceGeometryChanges':0,'publication':False}
        save(LOCAL/'selection.json.gz',frozen);save(DOC/'selection.json.gz',frozen)
        save(RECOVERY/'recovery-report.json',report)
        save(RECOVERY/'independent-readback.json',{'verifiedSources':17,'verifiedBytes':sum(t['bytes']for t in targets.values()),'allHashesMatchPlan':True,'archiveReportsVerified':all(r['archiveVerified']for r in report['archives']),'workflowRun':42264710088,'readOnlyR2':True,'modelReviewWrites':0,'publication':False})
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',LOCAL/'reservation.json','--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        return
    frozen=read(LOCAL/'selection.json.gz')
    for path,h in frozen['inputHashes'].items():assert sha(ROOT/path)==h,path
    helper=module('islands_r2_existing_source_check',HERE/'xl-pass.py');helper.BATCH,helper.LOCAL,helper.DOC,helper.LIMIT=BATCH,LOCAL,DOC,len(frozen['rows'])
    packed=[]
    for row in frozen['rows']:
        h=row['sourceSHA256'];source=ASSETS/(h+'.glb.gz');assert sha(source)==h
        target=LOCAL/'recovered/assets'/(h+'.glb.gz');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        entry=helper.shape_prepare.entry(row['native'],row['source']['building']);assert entry['sha256']==h
        packed.append({'uid':row['uid'],'building':row['source']['building'],'candidate':{'path':rel(target),'entry':entry},'currentNative':None})
    save(LOCAL/'recovered/geometry-inputs.json',{'rows':packed,'errors':{},'sourceGeometryChanges':0})
    helper.check_owned()


if __name__=='__main__':main()
