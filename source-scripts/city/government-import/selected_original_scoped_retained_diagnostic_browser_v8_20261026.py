"""Retain every V5 guard and expose the existing harness retained-camera direction."""
import argparse
import copy
import json
import math
import os
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from candidate_availability_graph_v1_20261026 import validate as validate_candidate_availability
from selected_full_native_replacement_binding_v2_20261026 import validate_envelope
from retained_native_nonregression_v1_20261023 import terrain_decision


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','native-context','scope']:parser.add_argument('--'+k,required=True)
    parser.add_argument('--uid',action='append',required=True)
    parser.add_argument('--retain-native',action='append',required=True)
    parser.add_argument('--support',action='append',default=[])
    parser.add_argument('--protect-basic-against',action='append',default=[])
    parser.add_argument('--viewer-url',default='http://127.0.0.1:4176/city.html')
    parser.add_argument('--capture-direction',type=float,nargs=3,default=[-.7,.8,1])
    parser.add_argument('--retained-capture-direction',type=float,nargs=3)
    parser.add_argument('--owned',action='store_true')
    parser.add_argument('--viewport-width',type=int,choices=[1280,390],action='append')
    parser.add_argument('--fit-joint-camera',action='store_true')
    parser.add_argument('--fit-joint-camera-mobile',action='store_true')
    parser.add_argument('--skip-download-failure',action='store_true',help='Final cohort observation only; previous failure evidence stays separate')
    for key in ['terrain-batch','terrain-scope','terrain-regression']:parser.add_argument('--'+key)
    parser.add_argument('--native-terrain-decisions',help='Exact authenticated terrain-only decisions retaining raw legacy support failures')
    parser.add_argument('--expanded-terrain-proposal',help='Authenticated separately validated expanded retained template; never inferred')
    parser.add_argument('--candidate-peer',action='append',default=[],help='Proposed sourceUid,peerUid availability edge; no physical approval')
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    assert all(math.isfinite(v)for v in a.capture_direction)and sum(v*v for v in a.capture_direction)>0
    if a.retained_capture_direction is not None:
        assert all(math.isfinite(v)for v in a.retained_capture_direction)and sum(v*v for v in a.retained_capture_direction)>0
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json'
    refs,pins=[Path(__file__),HERE/'candidate_availability_graph_v1_20261026.py',HERE/'selected_full_native_replacement_binding_v2_20261026.py',HERE/'retained_native_nonregression_v1_20261023.py'],{}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(a.runtime,'selection.json.gz');selected={r['uid']:r for r in selection['rows']}
    assert len(set(a.uid))==len(a.uid) and set(a.uid)<=selected.keys()
    assert len(set(a.retain_native))==len(a.retain_native) and not set(a.uid)&set(a.retain_native)
    archived={r['uid']:r for r in take(a.native_context,'native-input.json.gz')['rows']}
    assert set(a.retain_native)<=archived.keys()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert sha==selection['manifestSHA256'];refs.append(manifest)
    scope=take(a.scope,'summary.json');assert scope['currentManifestSHA256']==sha
    assert set(scope['uids'])==set(a.uid)
    forms={};form_pins={}
    for row in scope['rows']:
        for item in take(a.scope,row['uid'].split('/')[1]+'-forms.json.gz'):
            form=item['building'];uid=form['uid'];assert uid not in forms or forms[uid]==form;forms[uid]=form
            tile=ROOT/'3d-viewer'/item['tile'];key=str(tile.relative_to(ROOT))
            assert digest(tile.read_bytes())==item['tileSHA256']==scope['currentFormTileHashes'][key]
            assert next(f for f in read(tile)['buildings']if f['uid']==uid)==form
            refs.append(tile);form_pins[key]=item['tileSHA256']
    model_nearby={n['uid']for row in scope['rows']for n in row['nearbyNativeActors']}
    terrain_routes=[];terrain_resources=[];regression_flags=[]
    assert bool(a.terrain_batch)==bool(a.terrain_scope)==bool(a.terrain_regression)
    if a.terrain_batch:
        terrain_scope=take(a.terrain_scope,'scope.json')
        assert pins[a.terrain_scope][str(manifest.relative_to(ROOT))]==sha
        assert model_nearby|set(terrain_scope['touchingNativeUids'])==set(a.retain_native)
        for f in take(a.terrain_scope,'form-obligations.json.gz'):
            uid=f['uid'];assert uid not in forms or forms[uid]==f;forms[uid]=f
            tile=ROOT/'3d-viewer'/next(t['url']for t in read(manifest)['tiles']if t['id']==f['tile']);key=str(tile.relative_to(ROOT))
            assert digest(tile.read_bytes())==pins[a.terrain_scope][key]
            assert next(b for b in read(tile)['buildings']if b['uid']==uid)==f
            refs.append(tile);form_pins[key]=digest(tile.read_bytes())
        proposal=take(a.terrain_batch,'summary.json');candidate=proposal['candidate'];patchpath=ROOT/candidate['path']
        assert digest(patchpath.read_bytes())==candidate['sha256']==pins[a.terrain_batch][str(patchpath.relative_to(ROOT))];refs.append(patchpath)
        patch=read(patchpath);old=candidate['replaces'];oldpath=ROOT/'3d-viewer'/old['url']
        assert digest(oldpath.read_bytes())==old['sha256'];refs.append(oldpath)
        assert old['retainedUids']==read(oldpath)['meta']['targetUids']
        assert set(old['retainedUids'])<=set(a.retain_native) and set(old['retainedUids'])<=set(patch['meta']['targetUids'])
        if patch['coarseCells']!=read(oldpath)['coarseCells']:
            assert a.expanded_terrain_proposal,'Expanded retained envelope requires its separately validated proposal'
            expanded=take(a.expanded_terrain_proposal,'summary.json')
            assert expanded['status']=='private-terrain-validator-passed' and expanded['candidate']['path']==candidate['path'] and expanded['candidate']['sha256']==candidate['sha256']
            template_proof=take(a.expanded_terrain_proposal,'retained-template-proof.json')
            assert template_proof['templatePath']==str(oldpath.relative_to(ROOT)) and template_proof['templateSHA256']==old['sha256']
            validate_envelope(patch['coarseCells'],terrain_scope['regionalCoarseCells'],read(oldpath)['coarseCells'],template_proof)
        else:
            assert not a.expanded_terrain_proposal
            assert patch['coarseCells']==read(oldpath)['coarseCells']==terrain_scope['regionalCoarseCells']
        positive=[r for r in terrain_scope['terrainContacts']if r['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in r['packedContacts'])]
        assert len(positive)==1 and positive[0]['url']==old['url']
        regression=take(a.terrain_regression,'summary.json')
        assert regression['forms']==terrain_scope['intersectingForms'] and set(regression['requiredNativeUids'])==set(a.retain_native)
        if a.native_terrain_decisions:
            bundle=take(a.native_terrain_decisions,'summary.json')
            assert bundle['uids']==a.uid and bundle['currentManifestSHA256']==sha and bundle['nativeNeighbourBatch']==a.terrain_regression
            assert bundle['candidate']['path']==candidate['path'] and bundle['candidate']['sha256']==candidate['sha256']
            assert bundle['rawNativeRows']==regression['nativeRows'] and bundle['rawNativeResolved']==regression['nativeResolved']
            failed={r['uid']for r in regression['nativeRows']if not r['passed']}
            assert failed==set(bundle['rawNativeFailures'])==set(bundle['unchangedNativeContexts'])
            assert not bundle['existingNativeReaccepted'] and bundle['allTerrainChangeDecisionsPassed'] and bundle['sourceGeometryChanges']==bundle['nativeMetadataChanges']==0
            assert set(regression['nativeResolved'])=={r['uid']for r in regression['nativeRows']if r['passed']}
            installed_for_decisions={e['uid']:e for url in read(manifest)['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']}
            replayed=[]
            for row in regression['nativeRows']:
                if row['passed']:replayed.append(copy.deepcopy(row));continue
                item=bundle['unchangedNativeContexts'][row['uid']];context=take(item['batch'],'summary.json')
                assert pins[item['batch']][str(manifest.relative_to(ROOT))]==sha and pins[item['batch']][candidate['path']]==candidate['sha256']
                assert item['summary']==dict(path=str((base/item['batch']/'summary.json').relative_to(ROOT)),sha256=digest((base/item['batch']/'summary.json').read_bytes()))
                replayed.append(terrain_decision(row,context,installed_for_decisions))
            assert replayed==bundle['terrainDecisionRows'] and {r['uid']for r in replayed}==set(a.retain_native) and all(r['passed']for r in replayed)
        else:
            assert set(regression['requiredNativeUids'])==set(regression['nativeResolved']) and all(r['passed']for r in regression['nativeRows'])
        regression_flags=regression['basicFlags']
        assert {r['uid']for r in regression_flags}<=set(a.uid), 'Unresolved external BASIC regression cannot be attributed to this co-import group'
        terrain_routes=[dict(source=candidate['path'],sourceSHA256=candidate['sha256'],destination='city/data/'+a.batch+'-terrain.json',resolution=patch['cell'],area=positive[0]['coarseOverlapAreaM2'],replaces=old)]
        terrain_resources=['terrain:city/data/terrain.json','terrain:'+old['url']]
    else:
        assert not a.native_terrain_decisions
        assert model_nearby==set(a.retain_native)
    assert set(a.uid)|set(a.retain_native)<=set(forms)
    current={};all_current=set()
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url
        for entry in read(p)['models']:
            assert entry['uid']not in all_current;all_current.add(entry['uid'])
            if entry['uid']in a.retain_native:current[entry['uid']]=(entry,p)
    assert all(row['currentNativeActorsChecked']==len(all_current)for row in scope['rows'])
    assert set(current)==set(a.retain_native)
    for uid,(entry,p)in current.items():
        assert entry==archived[uid]['entry'];asset=(p.parent/entry['asset']).resolve()
        assert asset==ROOT/archived[uid]['path'] and digest(asset.read_bytes())==entry['sha256'];refs.extend([p,asset])
    supports=dict(v.split(',')for v in a.support)
    assert len(supports)==len(a.support) and set(supports)<=set(a.uid) and set(supports.values())<=set(a.retain_native)
    peers,peer_order=validate_candidate_availability(a.uid,a.candidate_peer)
    protections=[]
    for pair in a.protect_basic_against:
        uid,owner=pair.split(',');assert uid in a.uid and owner in a.retain_native
        entry=current[owner][0];assert uid in entry.get('suppressesBuildingUids',[])
        row=selected[uid]
        protections.append(dict(uid=uid,buildingCSUID=row['candidate']['entry']['buildingCSUID'],sourceSHA256=row['sourceSHA256'],suppressorUid=owner,suppressorSourceSHA256=entry['sha256']))
    assert len({(r['uid'],r['suppressorUid'])for r in protections})==len(protections)
    if not a.owned:
        assert not doc.exists()and not local.exists()
        resources=[('building:'if u.startswith('landsd/')else'source-form:')+u for u in sorted(forms)]+terrain_resources
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
        for peer in peers[uid]:
            other=selected[peer]
            e.setdefault('supportDependencies',[]).append(dict(uid=peer,state='installed',buildingCSUID=other['source']['building']['buildingCSUID'],sha256=other['sourceSHA256']))
        e['asset']='assets/'+r['sourceSHA256']+'.glb.gz';dest=local/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());entries.append(e)
    save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',diagnosticOnly=True,physicalAcceptance=False,publicationApproved=False,datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=len(entries))))
    save(local/'catalogue-index.json',dict(models=len(entries),catalogues=['catalogue.json']));save(local/'source-forms.json',[selected[u]['source']['building']for u in a.uid]);save(local/'validation-forms.json',{u:selected[u]['source']for u in a.uid})
    tool=HERE/'ronsdale_three_live_browser_v15_20261026.mjs';refs.append(tool)
    config=dict(fitJointCameraMobile=a.fit_joint_camera_mobile,fitJointCamera=a.fit_joint_camera,viewerURL=a.viewer_url,basicFallbackProtections=protections,stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',terrain=terrain_routes,browserUids=a.uid,fitBox=True,additionalRetainedUids=a.retain_native,retainedNativeOwnViews=True,retainedBuildingUids=[],jointUids=a.uid,nativeSupportUidsByModel={u:[p]for u,p in supports.items()},captureDirectionByModel={u:a.capture_direction for u in a.uid},retainedCaptureDirectionByModel={u:a.retained_capture_direction for u in a.retain_native}if a.retained_capture_direction is not None else {})
    save(local/'preflight-config.json',dict(**config,doc=str(doc.relative_to(ROOT))+'/'))
    subprocess.run(['node',str(tool),'preflight',str((local/'preflight-config.json').relative_to(ROOT))],cwd=ROOT,check=True)
    commands=[]
    assert not a.viewport_width or len(set(a.viewport_width))==len(a.viewport_width)
    for width in a.viewport_width or [1280,390]:
        assert reservations.owns(lease)
        cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(**config,viewportWidths=[width],failureTestUids=a.uid if width==390 and not a.skip_download_failure else [],doc=str((doc/str(width)).relative_to(ROOT))+'/'))
        with(doc/('browser-'+str(width)+'.log')).open('w')as log:
            proc=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
        report=doc/str(width)/'staged-browser.json'
        commands.append(dict(width=width,exitCode=proc.returncode,reportPresent=report.exists(),diagnosticPassed=proc.returncode==0 and report.exists()and read(report)['passed']))
        save(doc/('command-'+str(width)+'.json'),commands[-1])
    assert digest(manifest.read_bytes())==sha
    for uid,(entry,p)in current.items():
        assert next(e for e in read(p)['models']if e['uid']==uid)==entry
        assert digest((p.parent/entry['asset']).read_bytes())==entry['sha256']
    for key,h in form_pins.items():assert digest((ROOT/key).read_bytes())==h
    refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
    result=dict(retainedCaptureDirection=a.retained_capture_direction,privateTerrainRoutes=terrain_routes,unresolvedBasicRegressionFlags=regression_flags,terrainRegression=a.terrain_regression,downloadFailureTestsSkipped=a.skip_download_failure,fitJointCameraMobile=a.fit_joint_camera_mobile,proposedCandidateAvailabilityByUid=peers,proposedDependencyFirstOrder=peer_order,candidatePeerPhysicalApproval=False,viewportWidths=a.viewport_width or [1280,390],fitJointCamera=a.fit_joint_camera,modelScope=a.scope,leasedFormUids=sorted(forms),basicFallbackProtections=protections,uids=a.uid,retainedNativeUids=a.retain_native,proposedSupportByUid=supports,retainedPublicationFlags={u:e['publicationApproved']for u,(e,p)in current.items()},currentManifestSHA256=sha,commands=commands,allBrowserDiagnosticsPassed=all(r['diagnosticPassed']for r in commands),diagnosticOnly=True,visualAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,nativeTerrainDecisionBatch=a.native_terrain_decisions,rawRetainedNativeFailures=(bundle['rawNativeFailures']if a.native_terrain_decisions else []),nativeMetadataChanges=0,qualification='Unapproved private preview of proposed original dependencies on exact unchanged installed native entries, including held publication flags and suppressions. Actual source/retained/fallback behaviour is observed, not assumed accepted. No identity, physical, native-hold, runtime or publication approval is granted.')
    module('retained_native_diagnostic_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-original-with-unchanged-retained-native-dependency-browser-diagnostic',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
