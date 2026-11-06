"""Lease-fenced strict island original ports, with staged/live browser evidence.

Existing direct-import numeric, identity, dependency and publication guards remain.
Only separately validated terrain plans may be published. No invented supports,
original building geometry edits or variant approval.
"""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import subprocess
import sys
import threading
import uuid

from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module, policy
from run import connect, jobs, reservations, dict_row, Jsonb
sys.path.insert(0, str(HERE.parent/'model-review-ledger'))
import ledger


def call(args):
    subprocess.run([str(x) for x in args], cwd=ROOT, check=True)


def verify_inputs(pins):
    for path, digest in pins.items():
        assert sha(ROOT/path) == digest, path


def browser_verified(path, uids):
    direct = module('islands_original_browser_contract', HERE/'integrate.py')
    return direct.browser_verified(path, set(uids))


def solid_verified(report, models):
    """Require exact original identity and solid actors in every required view."""
    expected={m['uid']:m for m in models}
    assert report.get('passed') is True and report.get('errors')==[]
    views=[v for v in report['views'] if 'time' in v]
    assert len(views)==4*len(expected)
    assert {(v['uid'],v['width'],v['time'])for v in views}=={(uid,w,t)for uid in expected for w in (1280,390)for t in ('15:00','22:00')}
    assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==set(expected)
    for v in views:
        model=expected[v['uid']]
        assert v['sourceSHA256']==model['sha256'] and v['originalTriangles']==model['triangles']
        assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and v['selectionClosed']
        assert v['pick']==v['collision']==v['uid'] and not v['overflow']
        assert v['fallbackFaces']==0 and v['meshVisibility'] and all(v['meshVisibility'])
        assert v['wireframeFlags'] and not any(v['wireframeFlags'])
        assert v['materialOpacities'] and all(o==1 for o in v['materialOpacities'])
    return True


def worker(batch, phase, attempt=1):
    doc = ROOT/'docs/astra-city/government-import'/batch
    if attempt!=1:doc=doc/f'attempt-{attempt}'
    stage = HERE/'accepted'/batch
    local = HERE/'local'/batch
    receipt_path = local/(f'{phase}-reservation.json'if attempt==1 else f'{phase}-{attempt}-reservation.json')
    receipt = read(receipt_path)
    assert reservations.owns(receipt)
    proof = read(doc/'stage.json')
    verify_inputs(proof['inputHashes'])
    selected = read(doc/'selection.json.gz')
    assert selected['manifestSHA256'] == sha(ROOT/'3d-viewer/city/data/manifest.json')
    assert sha(stage/'catalogue.json') == proof['catalogueSHA256']
    assert sha(stage/'plan.json') == proof['planSHA256']
    uids = proof['uids']
    assert set(uids) == {r['uid'] for r in selected['rows']}
    for row in selected['rows']:
        if not row.get('identityProof'):continue
        from government_georef_cell_identity import verify_files
        identity_record=read(ROOT/proof['identityEvidencePath'])
        previous=next(r for r in identity_record['rows']if r['uid']==row['uid'])
        entry=row['candidate']['entry']
        replay=verify_files({**row,'sourceSHA256':entry['sha256'],'modelId':entry['modelId'],'triangles':entry['triangles']},
                            previous['context'],local/'identity-replay'/row['uid'].replace('/','-').replace(':','-'))
        assert replay['passed'] and replay['proof']==row['identityProof']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        states = dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC', (uids,)))
    assert not any(s in ('held','source-unavailable','identity-unresolved','installed-verified') for s in states.values())
    config = stage/'browser-config.json'
    visibility_uids=read(config).get('visibilitySupplementUids',['landsd/191632:0','landsd/81779:0','landsd/81809:0'])
    if phase == 'browser-visible':
        obscured=visibility_uids
        assert set(obscured)<=set(uids)
        reports=[]
        for width in(1280,390):
            c=read(config);c.update(viewportWidths=[width],browserUids=obscured,failureTestUids=obscured,
                captureDirectionByModel={uid:[.1,4,.1]for uid in obscured},doc=rel(doc/f'visibility-{width}')+'/')
            cp=local/f'visibility-config-{width}.json';save(cp,c)
            call(['node',HERE/'original_private_catalogue_preflight_v1_20261103.mjs',rel(stage/'catalogue.json')])
            call(['node',HERE/'ronsdale_three_live_browser_v15_20261026.mjs','staged',rel(cp)])
            r=read(doc/f'visibility-{width}/staged-browser.json');assert r['passed']and not r['errors']
            for v in r['views']:
                if 'time'in v:v['file']=f'visibility-{width}/'+v['file']
            reports.append(r)
        merged={**reports[0],'views':[v for r in reports for v in r['views']],'errors':[],'passed':True}
        solid_verified(merged,[m for m in read(stage/'catalogue.json')['models']if m['uid']in obscured])
        save(doc/'visibility-staged-browser.json',merged)
        print(json.dumps({'visibilitySupplementComplete':len(obscured),'installed':0}),flush=True)
        return
    if phase == 'browser-solid':
        if (doc/'staged-complete.json').exists():
            staged=read(doc/'staged-complete.json')
            assert staged['freshMetricsSHA256']==sha(doc/'fresh-metrics.json')
        else:
            args=['node',HERE/'acceptance-metrics.mjs','--selection',rel(doc/'selection.json.gz'),'--candidates',rel(stage),'--out',rel(doc/'fresh-metrics.json')]
            if proof.get('terrainCandidates'):args+=['--terrain-candidates',proof['terrainCandidates']]
            call(args);metrics=read(doc/'fresh-metrics.json');by_source={r['uid']:r for r in selected['rows']}
            assert {r['uid']for r in metrics['rows']}==set(uids)
            for metric in metrics['rows']:
                row=by_source[metric['uid']]
                assert not policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['candidate']['entry']['sha256'],
                    'identityProof':row.get('identityProof')},metric,metrics['profiles']['mobile'])
        verify_inputs(read(doc/'fresh-metrics.json')['inputHashes'])
        call(['node',HERE/'original_private_catalogue_preflight_v1_20261103.mjs',rel(stage/'catalogue.json')])
        reports=[]
        for width in (1280,390):
            c=read(config);c.update(viewportWidths=[width],doc=rel(doc/f'solid-{width}')+'/')
            cp=local/f'solid-browser-config-{width}.json';save(cp,c)
            call(['node',HERE/'ronsdale_three_live_browser_v15_20261026.mjs','preflight',rel(cp)])
            call(['node',HERE/'ronsdale_three_live_browser_v15_20261026.mjs','staged',rel(cp)])
            r=read(doc/f'solid-{width}/staged-browser.json')
            assert r['passed'] and not r['errors']
            for v in r['views']:
                if 'time' not in v:continue
                assert v['solidAppearance'] and v['selectionClosed'] and v['fallbackFaces']==0
                assert v['materialOpacities'] and all(o==1 for o in v['materialOpacities'])
                v['file']=f'solid-{width}/'+v['file']
            reports.append(r)
        merged={**reports[0],'views':[v for r in reports for v in r['views']],'errors':[],'passed':True,
                'harnessSHA256':sha(HERE/'ronsdale_three_live_browser_v15_20261026.mjs')}
        solid_verified(merged,read(stage/'catalogue.json')['models'])
        save(doc/'solid-staged-browser.json',merged);browser_verified(doc/'solid-staged-browser.json',uids)
        save(doc/'solid-staged-complete.json',{'uids':uids,'freshMetricsSHA256':sha(doc/'fresh-metrics.json'),
             'stagedBrowserSHA256':sha(doc/'solid-staged-browser.json'),'publication':False,'sourceGeometryChanges':0})
        print(json.dumps({'solidStagedBrowserComplete':len(uids),'installed':0}),flush=True)
        return
    if phase == 'browser':
        metrics = doc/'fresh-metrics.json'
        call(['node', HERE/'acceptance-metrics.mjs', '--selection', rel(doc/'selection.json.gz'), '--candidates', rel(stage), '--out', rel(metrics)])
        result = read(metrics)
        source = {r['uid']: r for r in selected['rows']}
        assert {r['uid'] for r in result['rows']} == set(uids)
        for row in result['rows']:
            assert not policy.reasons({'state':'runtime-validated-awaiting-acceptance', 'sourceSHA256':source[row['uid']]['candidate']['entry']['sha256']}, row, result['profiles']['mobile']), row['uid']
        call(['node', HERE/'original_private_catalogue_preflight_v1_20261103.mjs', rel(stage/'catalogue.json')])
        call(['node', HERE/'resolution-browser.mjs', 'staged', rel(config)])
        browser_verified(doc/'staged-browser.json', uids)
        save(doc/'staged-complete.json', {'uids':uids,'freshMetricsSHA256':sha(metrics), 'stagedBrowserSHA256':sha(doc/'staged-browser.json'), 'publication':False, 'sourceGeometryChanges':0})
        print(json.dumps({'stagedBrowserComplete':len(uids),'installed':0}), flush=True)
        return
    staged = read(doc/'solid-staged-complete.json')
    assert staged['uids'] == uids and staged['freshMetricsSHA256'] == sha(doc/'fresh-metrics.json')
    assert staged['stagedBrowserSHA256'] == sha(doc/'solid-staged-browser.json')
    browser_verified(doc/'solid-staged-browser.json', uids)
    solid_verified(read(doc/'solid-staged-browser.json'),read(stage/'catalogue.json')['models'])
    verify_inputs(read(doc/'fresh-metrics.json')['inputHashes'])
    inspection = read(doc/'staged-inspection.json')
    assert inspection['actuallyViewed'] and inspection['renderingAccepted']
    assert inspection['stagedBrowserSHA256'] == staged['stagedBrowserSHA256']
    for image in inspection['images']:
        assert sha(ROOT/image['path']) == image['sha256']
    supplements=[]
    if visibility_uids:
        supplement=read(doc/'visibility-staged-browser.json')
        solid_verified(supplement,[m for m in read(stage/'catalogue.json')['models']if m['uid']in set(visibility_uids)])
        assert inspection['visibilitySupplementSHA256']==sha(doc/'visibility-staged-browser.json');supplements.append(supplement)
    expected_images={rel(doc/v['file'])for report in[read(doc/'solid-staged-browser.json'),*supplements]for v in report['views']if'time'in v}
    assert {r['path']for r in inspection['images']}==expected_images
    catalogue = read(stage/'catalogue.json')
    for model in catalogue['models']:
        assert sha(stage/model['asset']) == model['sha256']
        assert not model.get('supportDependencies') and not model.get('retainedBasicSupportDependencies')
        model.update(placementReviewed=True, sourceIdentityReviewed=True, identityReviewApproved=True, publicationApproved=True,
            placementReview='Strict original-government-import-v1; exact original source/identity and unchanged original building geometry; validated current/proposed terrain, fresh complete direct contact metrics and staged/live desktop/mobile loading/picking/collision/failure-retry. No AI geometry modelling.')
    approved = local/('approved'if attempt==1 else f'approved-{attempt}')
    assert not approved.exists()
    save(approved/'catalogue.json', catalogue)
    for model in catalogue['models']:
        target = approved/model['asset'];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((stage/model['asset']).read_bytes())
    plan = read(stage/'plan.json')
    plan['areas'][0]['catalogue'] = rel(approved/'catalogue.json')
    save(approved/'plan.json',plan)
    # All old catalogues/assets/terrain and BASIC tiles are independently bound.
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    before = manifest_path.read_bytes();manifest=read(manifest_path)
    old_inputs={}
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;old_inputs[rel(p)]=sha(p)
        for m in read(p)['models']:
            a=p.parent/m['asset'];assert sha(a)==m['sha256'];old_inputs[rel(a)]=sha(a)
    for entry in manifest['tiles']+manifest.get('terrainPatches',[]):
        p=ROOT/'3d-viewer'/entry['url'];old_inputs[rel(p)]=sha(p)
    p=ROOT/'3d-viewer/city/data/terrain.json';old_inputs[rel(p)]=sha(p)
    save(local/'manifest-before.json',manifest)
    save(doc/'retained-inputs.json',old_inputs)
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
    for model in catalogue['models']:
        prior=parts.get(model['uid'],{})
        parts[model['uid']]={'uid':model['uid'],'name':model.get('label'),'landmarkIds':prior.get('landmarkIds',[]),
            'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},
            'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-import','knownHold':False}
    decision={'batch':batch,'transactionBatch':batch+'-'+str(uuid.uuid4()),'policy':policy.POLICY,
              'uids':uids,'stagedBrowserSHA256':sha(doc/'solid-staged-browser.json'),'freshMetricsSHA256':sha(doc/'fresh-metrics.json'),
              'inspectionSHA256':sha(doc/'staged-inspection.json'),'oldManifestSHA256':sha(manifest_path),'sourceGeometryChanges':0,
              'terrainChanges':len(plan.get('topLevelTerrainPatches',[])),'aiCalls':0}
    save(doc/'decision.json',decision)
    ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,decision]).encode()).hexdigest()[:16]
    inv=pointer_path.parent/f'source-review-inventory-{snapshot}.json'
    assert not inv.exists()
    save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered})
    ledger.seed(inv,inherit=pointer['snapshotId'])
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(doc/'decision.json')}
    note='Strict original-government source port; unchanged original building geometry; validated current/proposed terrain, direct contact/runtime/source identity and all staged/live desktop/mobile checks. No architectural reconstruction or AI geometry modelling.'
    ledger.record_many(snapshot,receipt_path,[(uid,'approved-for-integration',doc/'decision.json',note,commit) for uid in uids],effort=effort,request_id=batch+'-approve-'+snapshot)
    publication=[sys.executable,HERE/'islands_guarded_publish.py',rel(approved/'plan.json'),'--receipt',receipt_path,'--phase',batch+(f'-attempt-{attempt}'if attempt!=1 else'')]
    call(publication)
    verify_inputs(old_inputs)
    call(publication+['--apply'])
    try:
        reports=[]
        for width in (1280,390):
            c=read(config);c.update(viewportWidths=[width],doc=rel(doc/f'live-solid-{width}')+'/')
            if visibility_uids:c['captureDirectionByModel']={uid:[.1,4,.1]for uid in visibility_uids}
            cp=local/f'live-solid-browser-config-{width}.json';save(cp,c)
            call(['node',HERE/'ronsdale_three_live_browser_v15_20261026.mjs','live',rel(cp)])
            r=read(doc/f'live-solid-{width}/live-browser.json');assert r['passed'] and not r['errors']
            for v in r['views']:
                if 'time' in v:v['file']=f'live-solid-{width}/'+v['file']
            reports.append(r)
        save(doc/'live-browser.json',{**reports[0],'views':[v for r in reports for v in r['views']],'errors':[],'passed':True})
        browser_verified(doc/'live-browser.json',uids)
        solid_verified(read(doc/'live-browser.json'),catalogue['models'])
        verify_inputs(old_inputs)
    except BaseException:
        manifest_path.write_bytes(before)
        raise
    installed={**decision,'snapshotId':snapshot,'installed':len(uids),'liveBrowserSHA256':sha(doc/'live-browser.json'),
               'manifestSHA256':sha(manifest_path),'retainedInputsVerified':len(old_inputs),'productionPublished':False,
               'terrainChanges':len(plan.get('topLevelTerrainPatches',[]))}
    save(doc/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,receipt_path,[(uid,'installed-verified',doc/'installed-acceptance.json',note,commit) for uid in uids],effort=effort,request_id=batch+'-installed-'+snapshot)
    assert read(pointer_path)==pointer
    save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inv),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,HERE.parent/'building-progress/export.py','--refresh'])
    call(['node',ROOT/'3d-viewer/scripts/build_progress.mjs'])
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        actual=dict(db.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,uids)))
    assert actual=={uid:'installed-verified' for uid in uids}
    save(doc/'integration.json',{**installed,'neonVerified':True})
    print(json.dumps({'installed':len(uids),'snapshot':snapshot,'neonVerified':True}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=('browser','browser-solid','browser-visible','install'))
    parser.add_argument('--batch',required=True)
    parser.add_argument('--owned',action='store_true')
    parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args();assert args.batch.startswith('government-islands-') and '/' not in args.batch
    assert 1<=args.attempt<=9
    local=HERE/'local'/args.batch
    doc=ROOT/'docs/astra-city/government-import'/args.batch
    if args.attempt!=1:doc=doc/f'attempt-{args.attempt}'
    if not args.owned:
        stage_proof=read(doc/'stage.json');uids=stage_proof['uids']
        lp=local/(f'{args.phase}-reservation.json'if args.attempt==1 else f'{args.phase}-{args.attempt}-reservation.json');assert not lp.exists()
        resources=sorted(set(['building:'+uid for uid in uids]+['server:127.0.0.1:4176']+stage_proof.get('additionalLeaseResources',[])))
        claim=reservations.claim('codex-islands-direct-'+str(uuid.uuid4()),resources,batch=args.batch,ttl=3600)
        assert claim['ok'],'Existing owner; no takeover'
        save(lp,json.loads(json.dumps(claim['reservation'],default=str)))
        call([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',lp,'--ttl','3600','--',sys.executable,__file__,args.phase,'--batch',args.batch,'--attempt',str(args.attempt),'--owned'])
        return
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    class Server(http.server.ThreadingHTTPServer):
        def handle_error(self,request,client_address):
            if isinstance(sys.exception(),(BrokenPipeError,ConnectionResetError)):return
            super().handle_error(request,client_address)
    server=Server(('127.0.0.1',4176),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:worker(args.batch,args.phase,args.attempt)
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
