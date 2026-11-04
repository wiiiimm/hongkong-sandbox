"""Stage one unchanged hospital original against complete strict physical evidence.

Both installed neighbouring terrain patches are preserved and checked. No live
publication or installation credit; the root-run publisher replays this receipt.
"""
import argparse, importlib.util, json, os, shutil, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from tuen_mun_current_bound_identity_20261010 import verify_files
from tuen_mun_named_original_hospital_identity_20261010 import POLICY
from dependency_preflight import from_catalogues

UIDS={'landsd/191896:0'}
RETAINED={'landsd/190440:0','landsd/222781:0'}
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-tuen-mun-special-original-two-retained-physical-20261010'
BASE=ROOT/'docs/astra-city/government-import/government-xl-tuen-mun-bound-current-owner-source-20261010'
BATCH='government-xl-tuen-mun-special-original-stage-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
BROWSER_CONFIG=DOC/'browser-config.json'
LEASE=HERE/'local'/BATCH/'install-reservation.json'

def ref(p):
    return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def recheck(local):
    physical=read(PHYSICAL/'result.json')
    assert physical['uids']==sorted(UIDS) and physical['scriptChecksPassed'] and not physical['reasons']
    assert physical['publication'] is False
    assert physical['newlyInstalled']==physical['modelGeometryChanges']==physical['scriptExternalAICalls']==0
    assert read(PHYSICAL/'neon-sync.json')==dict(jobId=physical['jobId'],resultVerified=True)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(physical['jobId'],)).fetchone()==('complete',physical)
    for item in physical['evidenceRefs']:assert ref(ROOT/item['path'])==item
    manifest_sha=read(BASE/'current-inputs.json.gz')['manifestSHA256']
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==manifest_sha
    rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}==UIDS
    contexts={c['uid']:c for c in read(BASE/'context.json.gz')['rows']}
    identities=[]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    for row in rows:
        identity=verify_files(row,contexts[row['uid']],local/row['uid'].split('/')[1].replace(':','-'))
        assert identity['policy']==POLICY and identity['passed'];identities.append(identity)
    assert json.loads(json.dumps(identities))==read(PHYSICAL/'owned-source-identity.json')['rows']
    metrics=read(PHYSICAL/'metrics.json');foundation=read(PHYSICAL/'foundation.json');validation=read(PHYSICAL/'validation.json')
    policy=module('hospital_numeric_policy',HERE/'acceptance-policy.py')
    from terrain_diagnostic_resolution import resolve_global_bottom_warning
    for row,identity in zip(rows,identities):
        uid=row['uid'];m=next(r for r in metrics['rows'] if r['uid']==uid);f=next(r for r in foundation['rows'] if r['uid']==uid)
        assert not policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':identity['proof']},m,metrics['profiles']['mobile'])
        assert f['strictFoundationAccepted'] and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==18759
        diagnostic=resolve_global_bottom_warning(next(v for v in validation['results'] if v['uid']==uid),m,f)
        assert not diagnostic['remaining']
    assert validation['checksPassed']==validation['loaderAccepted']==len(UIDS) and not validation['exceptions']
    native=read(PHYSICAL/'native-neighbour-checks.json');assert {r['uid'] for r in native['rows']}==RETAINED and all(r['passed'] for r in native['rows'])
    resolved=set(native['resolved']);assert not(set(native['blocked'])-resolved)
    neighbours=read(PHYSICAL/'neighbour-checks.json')['rows'];assert len(neighbours)==247
    assert not [r for r in neighbours if r['reasons'] and r['uid'] not in resolved]
    assert read(PHYSICAL/'final-terrain-budget.json')['passed']
    summary=dict(manifestSHA256=manifest_sha,completeOriginalFaces=18759,currentNeighbourFormsAccounted=247,independentPhysicalChecksPassed=True,unresolvedIndependentPhysicalReasons=[],physicalReceipt=ref(PHYSICAL/'result.json'),sourceGeometryChanges=0,physicalRoleExemptions=[])
    return rows,identities,summary

def owned():
    def owns():assert reservations.owns(read(LEASE))
    def call(cmd):
        subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
    owns();rows,identities,summary=recheck(HERE/'local'/BATCH/'identity-recheck')
    save(DOC/'identity-publication-recheck.json',identities);save(DOC/'complete-physical-publication-recheck.json',summary)
    entries=[]
    for row in rows:
        entry=dict(row['candidate']['entry']);assert not entry.get('suppressesBuildingUids') and not entry.get('supportDependencies')
        entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[],placementReview='Complete unchanged original Tuen Mun Hospital Special Block. Exact current provider and source-bound named hospital identity; all18759 original facets pass ordinary terrain clearance and whole foundation,62053 runtime samples and766 low-rim samples pass. All247 neighbouring forms and both existing190440/222781 original native actors pass unchanged. Both installed terrain surfaces preserved outside the authenticated original source terrain. No source geometry/root/elevation changes, no physical role exemption and zero AI geometry modelling.')
        asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset)
        assert ref(asset)['sha256']==entry['sha256'];entries.append(entry)
    catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json')
    catalogue.update(models=entries,counts={'packedModels':1},area='Tuen Mun Hospital unchanged original Special Block')
    save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']))
    forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];sourceforms=[r['building'] for r in forms if r['building']['uid'] in UIDS]
    assert {r['uid'] for r in sourceforms}==UIDS;save(STAGE/'source-forms.json',sourceforms)
    candidates=read(PHYSICAL/'terrain-candidates.json');assert len(candidates)==1;c=candidates[0]
    assert set(c['uids'])==UIDS and not c.get('replaces') and len(c['replacesMany'])==2
    assert ref(ROOT/c['path'])['sha256']==c['sha256']
    patch=STAGE/Path(c['path']).name;shutil.copyfile(ROOT/c['path'],patch);p=read(patch)
    assert p.get('nativeMesh') and not p.get('patches')
    assert p['meta']['parentTerrain']=='city/data/terrain.json' and p['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
    terrain=dict(source=ref(patch)['path'],sha256=ref(patch)['sha256'],destination='city/data/'+patch.name,resolution=p['cell'],area=catalogue['area']+' indexed original terrain')
    replacements=[];retained=set();manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    for replacement in c['replacesMany']:
        assert ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256']
        assert replacement['url'] in {r['url'] for r in manifest['terrainPatches']}
        assert set(replacement['retainedUids'])<=set(p['meta']['targetUids']);retained.update(replacement['retainedUids'])
        review=dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=terrain['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=p['meta']['targetUids'],fullMeshCheck=ref(PHYSICAL/'native-neighbour-checks.json'))
        reviewpath=DOC/('native-replacement-review-'+replacement['retainedUids'][0].split('/')[1].replace(':','-')+'.json')
        save(reviewpath,review);replacements.append({**replacement,'nativeReview':ref(reviewpath)})
    assert retained==RETAINED;terrain['replacesMany']=replacements
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[terrain]))
    dependencies=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json'])
    assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
    config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureBoundsByModel={e['uid']:e['worldBounds'] for e in entries},browserUids=sorted(UIDS),failureTestUids=sorted(UIDS),nativeSupportUidsByModel={u:sorted(RETAINED) for u in UIDS})
    save(BROWSER_CONFIG,config)
    evidence=[ref(q) for q in [Path(__file__),PHYSICAL/'result.json',DOC/'identity-publication-recheck.json',DOC/'complete-physical-publication-recheck.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',BROWSER_CONFIG,HERE/'tuen_mun_current_bound_identity_20261010.py',HERE/'tuen_mun_named_original_hospital_identity_20261010.py',HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs',HERE/'reviewed_multi_native_terrain_publication_20261009.py',HERE/'xl-terrain-recovery-20261009-publish-reviewed-multi-native.py']]+[r['nativeReview'] for r in replacements]
    decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},manifestSHA256=summary['manifestSHA256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence)
    save(DOC/'stage.json',decision)
    call([sys.executable,str(HERE/'xl-terrain-recovery-20261009-publish-reviewed-multi-native.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
    call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs'),'staged',ref(BROWSER_CONFIG)['path']])
    report=module('hospital_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS)
    expected={(u,w,t) for u in RETAINED for w in [1280,390] for t in ['15:00','22:00']}
    assert {(v['uid'],v['width'],v['time']) for v in report['retainedNativeOwnViews']}==expected
    assert all(v['active'] and v['visible'] and v['fullyFramed'] for v in report['retainedNativeOwnViews'])
    for item in evidence:assert ref(ROOT/item['path'])==item
    recheck(HERE/'local'/BATCH/'identity-final')
    decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True)
    save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=sorted(UIDS),publication=False,newlyInstalled=0)),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');args=parser.parse_args()
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned()
    assert not DOC.exists() and not STAGE.exists()
    forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows']
    resources={('building:' if r['building']['uid'].startswith('landsd/') else 'source-form:')+r['building']['uid'] for r in forms}|{'terrain-patch:'+u for u in UIDS}
    resources|={'terrain-surface:'+r['url'] for r in read(PHYSICAL/'terrain-candidates.json')[0]['replacesMany']}
    claim=reservations.claim('codex-tuen-mun-special-stage-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600)
    assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
