"""Qualify the exact three originals only after ROOT inspects all private exports."""
import argparse,copy,shutil,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
from hierarchical_unaffected_diagnostic_contract_v1_20261026 import verify_context
from podium323546_original_identity_and_role_review_v1_20261026 import SOURCES,PREFIX
BASE=ROOT/'docs/astra-city/government-import'
BATCH=PREFIX+'three-hierarchical-qualified-stage-v1-20261026';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
BROWSER=PREFIX+'three-hierarchical-private-browser-v1-20261026';PREVIOUS=HERE/'local'/BROWSER;SOURCE=DOC
ROLE=PREFIX+'three-original-identity-role-review-v1-20261026'
CONFIG=dict(prefix=PREFIX+'three-hierarchical',date='20261026',sources=SOURCES,browser=BROWSER,review=BATCH,physical=BATCH,previousCountReport='government-xl-beverly-d-finite-independent-original-original-installed-v2-20261026/full-xl-current-count.json',previousInstalled=382,expectedFixedXLDelta=1,currentNativeActors=6959,neighbourForms=6,placementReview='Bounded exact original anonymous podium assembly with complete unchanged hierarchical terrain/source-interface evidence',label='Three unchanged original podium components')
TERRAIN_OWNERS=['landsd/323546:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--accept-exports-actually-viewed-by-root',action='store_true',required=True);ap.parse_args()
    assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];pins={};receipts={}
    def take(name,file):
        if name not in receipts:
            receipts[name],bound=authenticate(BASE/name);refs.append(BASE/name/'result.json')
            for p,h in bound.items():assert p not in pins or pins[p]==h;pins[p]=h
        path=BASE/name/file;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    role=take(ROLE,'ROOT-IDENTITY-AND-ROLE-REVIEW.json');assert role['identityAccepted']and role['sourceSpecificPhysicalInterpretationAccepted']and role['completeNeighbourInterpretationAccepted']and role['sourceSHA256ByUid']==SOURCES
    browser=take(BROWSER,'summary.json');assert browser['allBrowserDiagnosticsPassed']and browser['canonicalPublisherDryRunPassed']and browser['retainedSourcesReapproved']is False
    manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert browser['currentManifestSHA256']==ref(manifest)['sha256']==role['currentManifest']['sha256'];refs.extend([manifest,pointer]);reports=[];images=[]
    for width in [1280,390]:
        reportpath=BASE/BROWSER/str(width)/'staged-browser.json';r=take(BROWSER,str(width)+'/staged-browser.json');assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2*len(SOURCES)
        assert {(v['uid'],v['time'])for v in views}=={(u,t)for u in SOURCES for t in ['15:00','22:00']}
        for v in views:
            assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
            path=reportpath.parent/v['file'];assert ref(path)['sha256']==pins[str(path.relative_to(ROOT))];refs.append(path);images.append(dict(**ref(path),uid=v['uid'],width=width,time=v['time']))
        assert r['retainedNativeOwnViews']==[]
        assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
        if width==390:
            failures=[v for v in r['views']if v.get('phase')=='failed-download'];assert {v['uid']for v in failures}==set(SOURCES)and all(v['fallbackRetained']for v in failures)
        reports.append(ref(reportpath))
    current_scope=take(PREFIX+'three-current-neighbours-v1-20261026','summary.json')
    proof=take(PREFIX+'whole-installed-change-scope-v2-20261026','summary.json');formscheck=take(PREFIX+'hierarchical-forms-v2-20261026','summary.json')
    cfgpath=PREVIOUS/'browser-config-390.json';assert ref(cfgpath)['sha256']==pins[str(cfgpath.relative_to(ROOT))];refs.append(cfgpath);cfg=read(cfgpath)
    assert cfg['viewerURL']=='http://127.0.0.1:4177/city.html'and cfg['additionalRetainedUids']==[] and len(cfg['terrain'])==1
    terrain=copy.deepcopy(cfg['terrain']);entry=terrain[0];replacement=entry['replaces'];oldpath=ROOT/'3d-viewer'/replacement['url'];source=ROOT/entry['source'];assert ref(source)['sha256']==entry['sha256'];refs.extend([source,oldpath])
    retention=verify_context(read(oldpath),read(source),TERRAIN_OWNERS,replacement,proof,formscheck,current_scope);assert retention==browser['hierarchicalRetention']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    catpath=PREVIOUS/'catalogue.json';assert ref(catpath)['sha256']==pins[str(catpath.relative_to(ROOT))];refs.append(catpath);cat=read(catpath);assert {m['uid']:m['sha256']for m in cat['models']}==SOURCES
    resources={'building:'+u for u in browser['leasedFormUids']}|{'terrain:'+replacement['url']}
    q=copy.deepcopy(role);q.update(privateStageQualified=True,originalSourceReviewAccepted=True,visualAcceptance=True,browserReports=reports,imagesActuallyViewed=images,leaseResources=sorted(resources),exactTerrainReplacement=replacement,hierarchicalRetention=retention,terrainNonEffectProof=ref(BASE/(PREFIX+'whole-installed-change-scope-v2-20261026')/'result.json'),retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],terrainEdits=True,retainedSourcesReapproved=False,qualification='Exact anonymous original source port. All12 private source day/night desktop/mobile full frames actually opened by ROOT. Podium deck/ramps and original cuboid roofs/façades are visible; lower cuboid faces are partly concealed by the adjoining original podium as in the source. Early podium mobile own views include BASIC companions during failure/retry sequencing; final joint checks have all three originals active. Original grey/day and dark/night materials retained. Whole-inventory exact terrain non-effect proof preserves21 old targets without granting fresh identity/placement/visual approval. Live verification/independent readback still required.',publication=False,installationApproved=False)
    save(DOC/'qualification.json',q);save(DOC/'ROOT-SOURCE-REVIEW.json',q);save(DOC/'ROOT-PHYSICAL-REVIEW.json',q);save(DOC/'install-config.json',CONFIG)
    cat.update(kind='official-model-catalogue',diagnosticOnly=False,physicalAcceptance=True,publicationApproved=True)
    for m in cat['models']:
        assert m['proceduralWindows']is False and not m.get('supportDependencies')and not m.get('suppressesBuildingUids')
        m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=CONFIG['placementReview'])
        p=PREVIOUS/m['asset'];assert ref(p)['sha256']==m['sha256'];refs.append(p);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']))
    sourceforms=PREVIOUS/'source-forms.json';assert ref(sourceforms)['sha256']==pins[str(sourceforms.relative_to(ROOT))];shutil.copyfile(sourceforms,STAGE/'source-forms.json');refs.append(sourceforms)
    dest=STAGE/'original-terrain.json';shutil.copyfile(source,dest);entry.update(source=str(dest.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',area=CONFIG['label'])
    assert set(read(dest)['meta']['targetUids'])==set(replacement['retainedUids'])|set(TERRAIN_OWNERS)
    save(DOC/'hierarchical-native-replacement-review.json',dict(status='approved-for-integration',method='exact-whole-source-terrain-non-effect',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=entry['sha256'],retainedUids=replacement['retainedUids'],sourceGeometryChanged=False,modelGeometryChanges=0,aiCalls=0,wholeInstalledActorProof=q['terrainNonEffectProof'],wholeSourceActorsAccounted=6959,registeredBasicSupportsAccounted=10,affectedNativeUids=[],affectedRegisteredBasicSupportUids=[],existingModelsReapproved=False,allOriginalChildrenAndOldGridExact=True))
    entry['hierarchicalNativeReview']=ref(DOC/'hierarchical-native-replacement-review.json')
    url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=CONFIG['label'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=terrain))
    cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
    deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
    for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    previous=BASE/CONFIG['previousCountReport'];delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==382 and delta['expectedFixedXLDelta']==1;save(DOC/'fixed-xl-delta.json',delta);refs.append(previous)
    pub=module('hierarchical_qualified_canonical_publish',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';oldargv=sys.argv[:]
    try:sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main()
    finally:sys.argv=oldargv
    assert read(pub.DOC/'publication-plan.json')['published']is False
    refs.extend([HERE/'hierarchical_unaffected_diagnostic_contract_v1_20261026.py',HERE/'hierarchical_original_terrain_binding_v1_20261026.py',HERE/'podium323546_original_identity_and_role_review_v1_20261026.py',HERE/'dependency_preflight.py',HERE/'upton_staged_image_review_binding_v1_20261014.py',HERE.parent/'island-detail-integration/publish.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
    module('hierarchical_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-exact-original-hierarchical-non-effect-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=3,newRuntimeCount=6962,publication=False))

if __name__=='__main__':main()
