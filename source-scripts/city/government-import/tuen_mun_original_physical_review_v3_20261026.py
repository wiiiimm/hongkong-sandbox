"""Closed twelve-source hospital physical/visual review; preserve every raw failure."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from tuen_mun_original_identity_contract_v1_20261026 import SOURCES
from candidate_availability_graph_v1_20261026 import validate

BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-after-pok-oi-tuen-mun-';DATE='-20261026'
EXPECTED_WALLS={'landsd/336667:0','landsd/193881:0','landsd/336668:0','landsd/336669:0','landsd/336672:0','landsd/198266:0','landsd/6629:0'}
EXPECTED_CONTACTS={'landsd/336669:0','landsd/336670:0','landsd/336671:0','landsd/199375:0'}
EXPECTED_NATIVE={'landsd/190440:0','landsd/191896:0','landsd/222781:0'}

def main():
    batch=PREFIX+'closed-physical-source-review-v3'+DATE;out=BASE/batch;assert not out.exists()
    refs=[Path(__file__),HERE/'tuen_mun_original_identity_contract_v1_20261026.py'];pins={};receipts={}
    def folder(name):return name if name.startswith('government-xl-')else PREFIX+name+DATE
    def take(name,file):
        n=folder(name)
        if n not in pins:receipts[n],pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
        p=BASE/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def bound_path(name,p):
        n=folder(name)
        if n not in pins:receipts[n],pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    hashes={u:r['sourceSHA256']for u,r in SOURCES.items()};manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());refs.append(manifest)
    identity=take('closed-compound-identity-review-v1','ROOT-COMPOUND-IDENTITY-REVIEW.json')
    assert identity['identityAccepted']and identity['sourceSHA256ByUid']==hashes and identity['currentManifestSHA256']==msha
    runtime='twelve-retained-replacement-runtime-v1';selection=take(runtime,'selection.json.gz');metrics=take(runtime,'metrics.json')
    assert selection['manifestSHA256']==msha and {r['uid']:r['sourceSHA256']for r in selection['rows']}==hashes
    attr=take('twelve-runtime-evidence-v1','attributes.json.gz');assert attr['startEndAllInputsVerified'];attrs={r['uid']:r for r in attr['rows']}
    metric={r['uid']:r for r in metrics['rows']};assert set(metric)==set(hashes)
    policy=module('hospital_existing_policy',HERE/'acceptance-policy.py');raw_reasons={};foundations={};wall_proofs={}
    for uid,source in SOURCES.items():
        r=next(r for r in selection['rows']if r['uid']==uid);asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==hashes[uid];refs.append(asset)
        proof=identity['identityProofByUid'][uid]
        reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=hashes[uid],identityProof=proof),metric[uid],metrics['profiles']['mobile'])
        expected=[]
        if uid in EXPECTED_WALLS:expected.append('terrain-intersects-source-over-0.5m')
        if uid in EXPECTED_CONTACTS:expected.append('ground-contact-unresolved')
        assert set(reasons)==set(expected),(uid,reasons,expected);raw_reasons[uid]=reasons
        n='retained-foundation-'+uid.split('/')[1].replace(':','-')+'-v1';foundation=take(n,'summary.json')
        assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
        assert {v['mode']for v in foundation['rows']}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
        assert all(v['uid']==uid and v['triangles']==v['completeTerrainTriangles']==source['triangles']and v['fullyBuriedTriangles']==v['fullyBuriedUpwardTriangles']==0 for v in foundation['rows']);foundations[uid]=ref(BASE/folder(n)/'summary.json')
        n='twelve-retained-clearance-v1'+DATE+'-'+uid.split('/')[1].replace(':','-')+'-low-faces'
        # Clearance driver appends source suffixes after its dated batch.
        low=take(PREFIX+n,'summary.json');assert low['sourceSHA256']==hashes[uid]and len(low['rows'])==4
        assert all(v['completeSourceFaces']==source['triangles']for v in low['rows'])
        if uid in EXPECTED_WALLS:
            assert all(v['exactAffectedFaces']and v['allAffectedWallLike']for v in low['rows'])
            caps=take(PREFIX+n.replace('-low-faces','-cap-paths'),'summary.json')
            assert caps['allFourCompleteGroundClearCapPaths']and caps['sourceSHA256']==hashes[uid]
            wall_proofs[uid]=dict(lowFaces=ref(BASE/(PREFIX+n)/'summary.json'),clearCaps=ref(BASE/(PREFIX+n.replace('-low-faces','-cap-paths'))/'summary.json'))
        else:assert all(not v['exactAffectedFaces']for v in low['rows'])
    graphpath=BASE/'government-xl-tuen-mun-proposed-availability-graph-v2-20261026.json';graphdata=read(graphpath);refs.append(graphpath)
    graph,order=validate(list(hashes),[u+','+v for u,peers in graphdata['dependencies'].items()for v in peers])
    mixed=take('mixed-fallback-coverage-v1','summary.json')
    assert mixed['sourceSHA256ByUid']==hashes and mixed['currentManifestSHA256']==msha and mixed['proposedDependencies']==graph
    assert mixed['allFourWorldMixedCoveragePassed']and len(mixed['rows'])==48 and set(mixed['requiredCoInstallationUids'])==set(hashes)
    assert all(r['passedExistingCoverageGate']and r['guaranteedMixedCoverageFraction']>=.95 for r in mixed['rows'])
    assert not graph['landsd/280350:0']and 'landsd/336670:0'in graph['landsd/336667:0']
    support_proofs={}
    def check_paths(uid,name,file_pattern,expected_count,peers,kind='rows'):
        summary=take(name,'summary.json')
        if 'sourceSHA256ByUid'in summary:assert all(hashes[u]==h for u,h in summary['sourceSHA256ByUid'].items())
        else:assert summary['sourceSHA256']==hashes[uid]
        assert set(peers)<=set(graph[uid]);seen=set()
        for mode in ['original','literal','leftF32','balancedF32']:
            file_mode=({'leftF32':'explicitLeftF32','balancedF32':'explicitBalancedF32'}.get(mode,mode) if kind=='paths' else mode)
            data=take(name,file_pattern.format(mode=file_mode));paths=data[kind];assert len(paths)==expected_count
            for r in paths:
                if kind=='paths':
                    v=r['verifiedPath'];assert v['withinEndpointHeight']and v['maximumResidualM']<=.001
                    c=v['contact'];assert c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2
                    seen.add('landsd/280350:0')
                else:
                    assert r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['maximumResidualM']<=.001
                    c=r['terminal']['contact'];assert c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['peerUid']in peers;seen.add(c['peerUid'])
            # Rebind every historical indexed world array used by the proof.
            n=folder(name);needed={uid,*peers};found=set()
            for p,h in pins[n].items():
                if not p.endswith('/attributes.json.gz'):continue
                path=ROOT/p;assert digest(path.read_bytes())==h;refs.append(path)
                for a in read(path)['rows']:
                    u=a['uid']
                    if u not in needed:continue
                    assert a['sourceSHA256']==attrs[u]['sourceSHA256']==hashes[u]
                    assert a['completeOriginalIndex']==attrs[u]['completeOriginalIndex']
                    for field in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert a[field]==attrs[u][field]
                    found.add(u)
            assert needed<=found,'Historical support proof lacks exact current-array equivalence'
        assert seen<=set(peers)
        support_proofs[uid]=dict(batch=folder(name),unresolvedWitnesses=expected_count,actualCompanionRoots=sorted(seen),allFourWorldPathsWithinExistingEndpointHeight=True,rawDirectSupportFailuresRetained=True)
    check_paths('landsd/336669:0','block-b-low-self-joins-v2','{mode}-paths.json.gz',138,{'landsd/280350:0','landsd/336672:0'})
    check_paths('landsd/336670:0','block-d-direct-podium-paths-v1','{mode}.json.gz',3,{'landsd/280350:0'})
    check_paths('landsd/336671:0','government-xl-after-ferry-tuen-mun-336671-companion-attachment-v1-20261026','{mode}.json.gz',24,{'landsd/280350:0','landsd/336667:0'})
    check_paths('landsd/199375:0','atrium-podium-paths-v1','{mode}.json.gz',7,{'landsd/280350:0'},kind='paths')
    # Complete peer-height envelopes remain raw diagnostics, separate from actual earth.
    compound=take('current-companion-foundations-v1','summary.json')
    assert len(compound['rows'])==24
    expected_pairs={('landsd/336669:0','landsd/280350:0'),('landsd/336669:0','landsd/336672:0'),('landsd/336670:0','landsd/280350:0'),('landsd/336671:0','landsd/280350:0'),('landsd/336671:0','landsd/336667:0'),('landsd/199375:0','landsd/280350:0')}
    assert {(r['uid'],r['supportUid'])for r in compound['rows']}==expected_pairs
    assert {(r['uid'],r['supportUid'],r['mode'])for r in compound['rows']}=={(u,v,m)for u,v in expected_pairs for m in ['original','literal','leftF32','balancedF32']}
    for r in compound['rows']:
        assert r['sourceSHA256']==hashes[r['uid']]and r['supportSourceSHA256']==hashes[r['supportUid']]
        f=r['foundation'];assert f['triangles']==f['completeTerrainTriangles']==SOURCES[r['uid']]['triangles']
        if (r['uid'],r['supportUid'])!=('landsd/336671:0','landsd/336667:0'):
            assert f['fullyBuriedUpwardTriangles']==0 and f['fullyBuriedAreaFraction']<=.001
        else:assert f['fullyBuriedTriangles']==51 and f['fullyBuriedUpwardTriangles']==4
    envelope=take('block-a-peer-envelope-context-v2','summary.json')
    assert envelope['sourceSHA256ByUid']=={u:hashes[u]for u in ['landsd/336671:0','landsd/280350:0','landsd/336667:0']}
    assert len(envelope['rows'])==4
    for r in envelope['rows']:
        assert r['allPeerEnvelopeBuriedFacesClearOfEarth']and r['peerEnvelopeUpwardFaces']==[4389,4390,6466,6467]
        detail=take('block-a-peer-envelope-context-v2',r['mode']+'-facets.json.gz')
        assert detail['completeSourceFaces']==6497 and len(detail['rows'])==53
        upward=[f for f in detail['rows']if f['upward']]
        assert len(upward)==4 and sum(f['areaM2']for f in upward)<4.85
        assert all(min(f['earthGapsM'])>46 and 50.66<min(f['heightRangeM'])<=max(f['heightRangeM'])<50.68 and max(f['peerEnvelopeGapsM'])< -7 for f in upward)
    context_png=BASE/folder('block-a-peer-envelope-context-v2')/'complete-source-peer-envelope-context.png'
    bound_path_name=folder('block-a-peer-envelope-context-v2')
    assert digest(context_png.read_bytes())==pins[bound_path_name][str(context_png.relative_to(ROOT))];refs.append(context_png)
    scope=take('retained-replacement-scope-v1','scope.json');native=take('retained-replacement-neighbours-v1','summary.json')
    assert scope['currentNativeActors']==6970 and scope['intersectingForms']==native['forms']==247
    assert set(scope['touchingNativeUids'])==set(native['requiredNativeUids'])==set(native['nativeResolved'])==EXPECTED_NATIVE
    assert all(r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['nativeRows'])
    assert {r['uid']for r in native['basicFlags']}=={'landsd/336669:0','landsd/336670:0','landsd/336671:0'}
    assert all(r['reasons']==['increased-neighbour-ground-gap']for r in native['basicFlags'])
    patch=take('podium-exact-retained-replacement-v3','summary.json');assert patch['status']=='private-terrain-validator-passed'and len(patch['replacedNativeTerrain'])==1
    budget=take('podium-exact-retained-replacement-v3','retained-inset-work-budget.json');assert budget['allDeclaredUnchangedFacesExact']and budget['allParentFacesAccounted']and budget['newWorkFaces']<=25000
    browsername='retained-terrain-private-browser-v5';take(browsername,'command-1280.json');browser=receipts[folder(browsername)]
    assert browser['allBrowserDiagnosticsPassed']and browser['proposedCandidateAvailabilityByUid']==graph and not browser['downloadFailureTestsSkipped']
    assert set(browser['retainedNativeUids'])==EXPECTED_NATIVE
    for width in [1280,390]:
        report=take(browsername,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        views=[r for r in report['views']if r.get('file')];assert len(views)==24 and {(r['uid'],r['time'])for r in views}=={(u,t)for u in hashes for t in ['15:00','22:00']}
        assert len(report['retainedNativeOwnViews'])==6
        if width==390:
            failed=[r for r in report['views']if r.get('phase')=='failed-download'];assert len(failed)==12 and {r['uid']for r in failed}==set(hashes)and all(r['fallbackRetained']for r in failed)
    sheets=take('retained-browser-contact-sheets-v1','summary.json');assert sheets['sourceImageCount']==60 and sheets['contactSheetCount']==16
    for r in sheets['images']+sheets['sheets']:
        path=ROOT/r['path'];assert digest(path.read_bytes())==r['sha256'];refs.append(path)
    forms=take('retained-replacement-scope-v1','form-obligations.json.gz');resources=[('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain:city/data/terrain.json','terrain:city/data/government-native-191896-0.json']
    result=dict(uids=list(hashes),sourceSHA256ByUid=hashes,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,
                currentManifest=ref(manifest),currentNativeActors=6970,requiredOriginalAssembly=hashes,requiredCoInstallationUids=sorted(hashes),supportByUid=graph,dependencyFirstOrder=order,
                rawPolicyReasonsByUid=raw_reasons,completeCompanionFoundationDiagnostics=compound,blockAPeerEnvelopeContext=envelope,blockAPeerEnvelopePlotActuallyInspected=ref(context_png),peerEnvelopeInterpretation='Complete original Block A and peer source context inspected. Four horizontal upward facets at50.669m total less than4.85m2, more than46m above actual earth, occur under higher neighbouring original source surfaces. This is original vertical layering at the shared building interface, not terrain burial. All53 envelope-classified facets are above actual earth in all4 worlds; the entire compound diagnostic is retained. Exact original attachment paths and current earth foundations remain separately required. No fabricated architectural identity or engineering root requirement.',completeFourWorldFoundations=foundations,exactOriginalWallCapProfiles=wall_proofs,sourceAttachmentProfiles=support_proofs,
                rawCoImportedBasicWarnings=native['basicFlags'],coImportedBasicResolutions={r['uid']:dict(sourceSHA256=hashes[r['uid']],completeOriginalPhysicalChecksPassed=True)for r in native['basicFlags']},
                retainedNativeUids=sorted(EXPECTED_NATIVE),terrainReplacement=patch['candidate'],terrainEdits=True,leaseResources=sorted(set(resources)),
                contactSheetsActuallyInspected=sheets['sheets'],sourceExportsInspectedViaContactSheets=sheets['images'],visualObservation='All60 authenticated actual day/night exports inspected via16 pixel-preserving contact sheets. Original government materials are unlit at night. Early mobile failure/retry views retain coarse companions and partly occlude193881; final joint checks show all12 original sources active. No framing, shader, collision, sampler or fallback failure. No new windows applied to government originals.',
                sourceGeometryChanges=0,sourcePoseChanges=0,nativeMetadataChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,scriptExternalAICalls=0,installationApproved=False,publication=False,
                supersededProposedAvailability=identity['requiredSourceAvailability'],availabilityQualification='The earlier pure-original closure proposal was diagnostic only. The new mandatory DAG retains exact physical roots and Main cell coverage; conservative original/BASIC intersections prove every remaining mixed companion state above the unchanged95percent footprint gate in all four worlds. This requires all12 exact original assets in the co-installation cohort; no missing-source or publication credit.',
                qualification='Closed exact source/ground/companion interpretation only. Complete source caps resolve authenticated lower-wall grade intersections; all four full foundations have zero buried facets. B138/D3/A24/Atrium7 exact source paths satisfy unchanged endpoint/incidence limits and require their typed original roots. Raw automatic failures remain archived. Three co-imported BASIC proxies are replaced only by independently qualified exact originals. All247region forms/3retainedactors and both actual browser widths are bound. Guarded publication/live/global-original/BASIC/readback checks remain required.')
    assert digest(manifest.read_bytes())==msha;save(out/'ROOT-PHYSICAL-REVIEW.json',result)
    refs.extend([HERE/'acceptance-policy.py',HERE/'candidate_availability_graph_v1_20261026.py'])
    module('closed_hospital_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'closed-exact-original-hospital-physical-and-visual-source-review',list(dict.fromkeys(refs)),result)
    print(dict(physicalReviewed=True,visualReviewed=True,models=12,installationApproved=False),flush=True)


if __name__=='__main__':main()
