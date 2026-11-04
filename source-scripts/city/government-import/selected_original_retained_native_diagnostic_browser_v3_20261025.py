"""V3 unapproved native-support preview: source-bound BASIC fallback protections; all V2 evidence gates retained."""
import argparse
import copy
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','native-context']:parser.add_argument('--'+k,required=True)
    parser.add_argument('--uid',action='append',required=True)
    parser.add_argument('--retain-native',action='append',required=True)
    parser.add_argument('--support',action='append',default=[])
    parser.add_argument('--protect-basic-against',action='append',default=[])
    parser.add_argument('--owned',action='store_true')
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json'
    refs,pins=[Path(__file__)],{}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(a.runtime,'selection.json.gz');selected={r['uid']:r for r in selection['rows']}
    assert len(set(a.uid))==len(a.uid) and set(a.uid)<=selected.keys()
    assert len(set(a.retain_native))==len(a.retain_native) and not set(a.uid)&set(a.retain_native)
    archived={r['uid']:r for r in take(a.native_context,'native-input.json.gz')['rows']}
    assert set(a.retain_native)<=archived.keys()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert sha==selection['manifestSHA256'];refs.append(manifest)
    current={}
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url
        for entry in read(p)['models']:
            if entry['uid']in a.retain_native:current[entry['uid']]=(entry,p)
    assert set(current)==set(a.retain_native)
    for uid,(entry,p)in current.items():
        assert entry==archived[uid]['entry'];asset=(p.parent/entry['asset']).resolve()
        assert asset==ROOT/archived[uid]['path'] and digest(asset.read_bytes())==entry['sha256'];refs.extend([p,asset])
    supports=dict(v.split(',')for v in a.support)
    assert len(supports)==len(a.support) and set(supports)<=set(a.uid) and set(supports.values())<=set(a.retain_native)
    protections=[]
    for pair in a.protect_basic_against:
        uid,owner=pair.split(',');assert uid in a.uid and owner in a.retain_native
        entry=current[owner][0];assert uid in entry.get('suppressesBuildingUids',[])
        row=selected[uid]
        protections.append(dict(uid=uid,buildingCSUID=row['candidate']['entry']['buildingCSUID'],sourceSHA256=row['sourceSHA256'],suppressorUid=owner,suppressorSourceSHA256=entry['sha256']))
    assert len({(r['uid'],r['suppressorUid'])for r in protections})==len(protections)
    if not a.owned:
        assert not doc.exists()and not local.exists()
        resources=['building:'+u for u in sorted(set(a.uid)|set(a.retain_native))]
        claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
        save(leasepath,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(leasepath),sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(leasepath);assert reservations.owns(lease)and not doc.exists();doc.mkdir();entries=[]
    for uid in a.uid:
        r=selected[uid];tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==r['source']['building'];refs.append(tile)
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
        with connect()as db:
            db.execute('SET TRANSACTION READ ONLY');native=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(r['native']['cacheKey'],)).fetchone()
        assert native and native[1]==r['native']['resultSha']
        e=copy.deepcopy(r['candidate']['entry']);e.update(sourceTile=native[0],priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        if uid in supports:
            p=current[supports[uid]][0]
            e['supportDependencies']=[dict(uid=p['uid'],state='installed',buildingCSUID=p['buildingCSUID'],sha256=p['sha256'])]
        e['asset']='assets/'+r['sourceSHA256']+'.glb.gz';dest=local/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());entries.append(e)
    save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',diagnosticOnly=True,physicalAcceptance=False,publicationApproved=False,datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=len(entries))))
    save(local/'catalogue-index.json',dict(models=len(entries),catalogues=['catalogue.json']));save(local/'source-forms.json',[selected[u]['source']['building']for u in a.uid]);save(local/'validation-forms.json',{u:selected[u]['source']for u in a.uid})
    tool=HERE/'ronsdale_three_live_browser_v12_20261025.mjs';refs.append(tool)
    config=dict(basicFallbackProtections=protections,stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',terrain=[],browserUids=a.uid,fitBox=True,additionalRetainedUids=a.retain_native,retainedNativeOwnViews=True,retainedBuildingUids=[],jointUids=a.uid,nativeSupportUidsByModel={u:[p]for u,p in supports.items()},captureDirectionByModel={u:[-.7,.8,1]for u in a.uid})
    save(local/'preflight-config.json',dict(**config,doc=str(doc.relative_to(ROOT))+'/'))
    subprocess.run(['node',str(tool),'preflight',str((local/'preflight-config.json').relative_to(ROOT))],cwd=ROOT,check=True)
    commands=[]
    for width in [1280,390]:
        assert reservations.owns(lease)
        cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(**config,viewportWidths=[width],failureTestUids=a.uid if width==390 else [],doc=str((doc/str(width)).relative_to(ROOT))+'/'))
        with(doc/('browser-'+str(width)+'.log')).open('w')as log:
            proc=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
        report=doc/str(width)/'staged-browser.json'
        commands.append(dict(width=width,exitCode=proc.returncode,reportPresent=report.exists(),diagnosticPassed=proc.returncode==0 and report.exists()and read(report)['passed']))
        save(doc/('command-'+str(width)+'.json'),commands[-1])
    assert digest(manifest.read_bytes())==sha
    for uid,(entry,p)in current.items():assert next(e for e in read(p)['models']if e['uid']==uid)==entry
    refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
    result=dict(basicFallbackProtections=protections,uids=a.uid,retainedNativeUids=a.retain_native,proposedSupportByUid=supports,retainedPublicationFlags={u:e['publicationApproved']for u,(e,p)in current.items()},currentManifestSHA256=sha,commands=commands,allBrowserDiagnosticsPassed=all(r['diagnosticPassed']for r in commands),diagnosticOnly=True,visualAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,nativeMetadataChanges=0,qualification='Unapproved private preview of proposed original dependencies on exact unchanged installed native entries, including held publication flags and suppressions. Actual source/retained/fallback behaviour is observed, not assumed accepted. No identity, physical, native-hold, runtime or publication approval is granted.')
    module('retained_native_diagnostic_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-original-with-unchanged-retained-native-dependency-browser-diagnostic',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
