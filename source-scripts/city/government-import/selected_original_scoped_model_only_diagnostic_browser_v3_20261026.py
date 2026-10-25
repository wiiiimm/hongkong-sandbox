"""Private source subset preview preserving each selected source complete current scope.

Runs the unchanged complete publisher dry run before browser work. No --apply,
source approval, retained-source reapproval or installation credit is supported.
"""
import argparse, copy, json, os, subprocess, sys, uuid, math
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','scope']:
        ap.add_argument('--'+k,required=True)
    ap.add_argument('--support',action='append',default=[],help='Proposed sourceUid,supportUid availability dependency; no physical approval')
    ap.add_argument('--frame-all-sources-for',action='append',default=[],help='Capture-only enclosing bounds for this source; no ownership or geometry inference')
    ap.add_argument('--view-direction',action='append',default=[],help='sourceUid,x,y,z: camera only')
    ap.add_argument('--uid',action='append',help='Explicit source subset; full per-source form/native obligations remain mandatory')
    ap.add_argument('--owned',action='store_true')
    a=ap.parse_args(); assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import'; doc=base/a.batch; local=HERE/'local'/a.batch
    refs=[Path(__file__)]; pins={}; receipts={}
    def take(batch,name):
        if batch not in receipts:
            receipts[batch], bound=authenticate(base/batch);refs.append(base/batch/'result.json')
            for p,h in bound.items():
                assert p not in pins or pins[p]==h
                pins[p]=h
        path=base/batch/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(a.runtime,'selection.json.gz'); scope=take(a.scope,'summary.json')
    assert set(scope['uids'])=={r['uid']for r in selection['rows']}
    if a.uid:
        assert len(a.uid)==len(set(a.uid)) and set(a.uid)<=set(scope['uids'])
        selection={**selection,'rows':[r for r in selection['rows'] if r['uid'] in a.uid]}
        scope={**scope,'uids':sorted(a.uid),'rows':[r for r in scope['rows'] if r['uid'] in a.uid]}
        assert {r['uid'] for r in scope['rows']}=={r['uid'] for r in selection['rows']}==set(a.uid)
    assert all(not r['nearbyNativeActors']for r in scope['rows']), 'Interacting native sources require their own full diagnostics'
    supports=dict(pair.split(',')for pair in a.support)
    assert len(supports)==len(a.support)and set(supports)<={r['uid']for r in selection['rows']}and set(supports.values())<={r['uid']for r in selection['rows']}
    for uid in supports:
        seen=set();at=uid
        while at in supports:
            assert at not in seen;seen.add(at);at=supports[at]
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    sha=digest(manifest.read_bytes());assert sha==selection['manifestSHA256']==scope['currentManifestSHA256']==pins[str(manifest.relative_to(ROOT))]
    # All actual assets/forms/implementation files bound by the current-source
    # input proofs must still match, not merely their receipt files.
    for p,h in pins.items(): assert digest((ROOT/p).read_bytes())==h,p
    sourceuids=sorted(scope['uids']); resources=set(sourceuids)
    assert len(set(a.frame_all_sources_for))==len(a.frame_all_sources_for)and set(a.frame_all_sources_for)<=set(sourceuids)
    directions={}
    for item in a.view_direction:
        uid,*values=item.split(',');values=[float(v)for v in values]
        assert uid in sourceuids and uid not in directions and len(values)==3 and all(math.isfinite(v)for v in values)and values[1]>0
        directions[uid]=values
    allbounds=[r['candidate']['entry']['worldBounds']for r in selection['rows']]
    bounds=[[min(b[0][i]for b in allbounds)for i in range(3)],[max(b[1][i]for b in allbounds)for i in range(3)]]
    contexts={u:bounds for u in a.frame_all_sources_for}

    for row in scope['rows']:
        for f in take(a.scope,row['uid'].split('/')[1]+'-forms.json.gz'): resources.add(f['building']['uid'])
    leasepath=local/'reservation.json'
    if not a.owned:
        assert not doc.exists() and not local.exists()
        claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),['building:'+u for u in sorted(resources)],batch=a.batch,ttl=3600)
        assert claim['ok'],claim;lease=claim['reservation'];save(leasepath,json.loads(json.dumps(lease,default=str)))
        try:
            subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(leasepath),sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease): assert reservations.release(lease)['ok']
        return
    lease=read(leasepath);assert reservations.owns(lease) and not doc.exists();doc.mkdir();entries=[]
    for r in selection['rows']:
        uid=r['uid'];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==r['source']['building']
        with connect()as db:
            db.execute('SET TRANSACTION READ ONLY')
            native=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(r['native']['cacheKey'],)).fetchone()
        assert native and native[1]==r['native']['resultSha']
        entry=copy.deepcopy(r['candidate']['entry']);assert not entry.get('supportDependencies')
        entry.update(sourceTile=native[0],priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        if uid in supports:
            support=next(q for q in selection['rows']if q['uid']==supports[uid])
            entry['supportDependencies']=[dict(uid=support['uid'],state='installed',buildingCSUID=support['source']['building']['buildingCSUID'],sha256=support['sourceSHA256'])]
        entry['asset']='assets/'+r['sourceSHA256']+'.glb.gz';dest=local/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());entries.append(entry);refs.extend([asset,tile])
    catalogue=dict(schemaVersion=1,kind='staged-official-model-catalogue',diagnosticOnly=True,physicalAcceptance=False,publicationApproved=False,datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=len(entries)))
    save(local/'catalogue.json',catalogue);save(local/'catalogue-index.json',dict(models=len(entries),catalogues=['catalogue.json']))
    save(local/'source-forms.json',[r['source']['building']for r in selection['rows']]);save(local/'validation-forms.json',{r['uid']:r['source']for r in selection['rows']})
    terrain=[]
    plan=dict(areas=[dict(area='Private original diagnostic',catalogue=str((local/'catalogue.json').relative_to(ROOT)),destination='city/data/official-models/'+a.batch+'/catalogue.json')],topLevelTerrainPatches=terrain)
    save(local/'publisher-dry-run-plan.json',plan)
    publisher=module('scoped_model_diagnostic_canonical_publisher',ROOT/'source-scripts/city/island-detail-integration/publish.py')
    publisher.DOC=doc/'publisher-dry-run'; before_argv=sys.argv[:]
    try:
        sys.argv=[str(ROOT/'source-scripts/city/island-detail-integration/publish.py'),str((local/'publisher-dry-run-plan.json').relative_to(ROOT))]
        publisher.main()
    finally: sys.argv=before_argv
    dry=read(publisher.DOC/'publication-plan.json');assert dry['published']is False
    assert digest(manifest.read_bytes())==sha
    tool=HERE/'ronsdale_three_live_browser_v13_20261025.mjs';refs.extend([tool,ROOT/'source-scripts/city/island-detail-integration/publish.py'])
    config=dict(viewerURL='http://127.0.0.1:4177/city.html',stage=str(local.relative_to(ROOT))+'/',catalogueURL=plan['areas'][0]['destination'],terrain=terrain,browserUids=sourceuids,fitBox=True,additionalRetainedUids=[],retainedNativeOwnViews=True,retainedBuildingUids=[],jointUids=sourceuids,nativeSupportUidsByModel={u:[p]for u,p in supports.items()},captureBoundsByModel=contexts,captureDirectionByModel={u:directions.get(u,[-.7,.9,1])for u in sourceuids})
    save(local/'preflight-config.json',dict(**config,doc=str(doc.relative_to(ROOT))+'/'))
    subprocess.run(['node',str(tool),'preflight',str((local/'preflight-config.json').relative_to(ROOT))],cwd=ROOT,check=True)
    commands=[]
    for width in [1280,390]:
        assert reservations.owns(lease);cfg=local/('browser-config-'+str(width)+'.json')
        save(cfg,dict(**config,viewportWidths=[width],failureTestUids=sourceuids if width==390 else [],doc=str((doc/str(width)).relative_to(ROOT))+'/'))
        with(doc/('browser-'+str(width)+'.log')).open('w')as log:
            proc=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
        report=doc/str(width)/'staged-browser.json';commands.append(dict(width=width,exitCode=proc.returncode,reportPresent=report.exists(),diagnosticPassed=proc.returncode==0 and report.exists()and read(report)['passed']))
        save(doc/('command-'+str(width)+'.json'),commands[-1])
    for p,h in pins.items(): assert digest((ROOT/p).read_bytes())==h,p
    assert digest(manifest.read_bytes())==sha and reservations.owns(lease)
    refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
    result=dict(uids=sourceuids,leasedFormUids=sorted(resources),currentManifestSHA256=sha,proposedSupportByUid=supports,captureOnlyContextBounds=contexts,captureOnlyDirections=directions,canonicalPublisherDryRunPassed=True,commands=commands,allBrowserDiagnosticsPassed=all(r['diagnosticPassed']for r in commands),diagnosticOnly=True,physicalAcceptance=False,visualAcceptance=False,identityAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,terrainEdits=False,qualification='Exact immutable original source preview, including any explicitly proposed candidate availability edges. Full current source/form scope is leased and has no nearby installed native candidates. Canonical publisher identity/dependency/retained-basic guards run unchanged in dry-run only before the browser. Every source approval field is false. This supplies observations for later identity/contact-role review, not physical support, visual, identity or publication approval.')
    save(doc/'summary.json',result)
    module('scoped_model_diagnostic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-unapproved-model-only-complete-source-scope-browser-diagnostic',refs,result)

if __name__=='__main__': main()
