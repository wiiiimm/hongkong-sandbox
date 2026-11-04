"""Bind complete current Parkview16 source, physical, neighbour and actual browser review.
No source/terrain edits or publication; canonical staging and live verification follow.
"""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from parkview256319_installed_support_contract_v1_20261104 import UID,PARENT,PEER,SHA,verify_metadata,verify_native_scope,verify_browser_native_scope
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview256319-whole-source-review-v1-20261104'
CONFIG=BASE/'government-xl-parkview256319-installation-plan-v1-20261104/config.json'
def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json';cfg=read(CONFIG);resources=sorted(['building:'+u for u in [UID,PARENT,PEER]]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH])
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('parkview-whole-source-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__),CONFIG,HERE/'parkview256319_installed_support_contract_v1_20261104.py'];pins={}
    def take(batch,name='summary.json',local=False):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=(HERE/'local'/batch if local else BASE/batch)/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    current='government-xl-parkview256319-after-tung-cheong-v1-20261104';selection=take(cfg['originalSelection'],'selection.json.gz');assert len(selection['rows'])==1;source=selection['rows'][0];assert source['uid']==UID and source['sourceSHA256']==SHA
    original={UID:source['candidate']['entry']};asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    identity=take(current+'-identity','256319:0/identity.json');proof=identity['proof'];assert identity['passed']and identity['reasons']==[]and all(proof[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    context=take(cfg['sourceContextReview'],'ROOT-SOURCE-CONTEXT-REVIEW.json');assert context['sourceSHA256']==SHA and all(context[k]for k in ['sourceSpecificSupportInterpretationAccepted','sourceSpecificBuriedWallInterpretationAccepted','sourceSpecificAdjacentSeamInterpretationAccepted','rawCanonicalFailuresPreserved','negativeParentFlagPreserved'])
    audit=take(cfg['parentApprovalAudit'],'audit.json');scope=take(cfg['scope']);contacts=take(cfg['nativeContacts']);roles=take('government-xl-parkview256319-native-seam-context-v2-20261104');near=take('government-xl-parkview256319-current-neighbours-v1-20261104-basic');assert near['foreignPairs']==0 and near['rows']==[]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());refs.append(manifest);assert mh==selection['manifestSHA256']==context['currentManifestSHA256']==scope['currentManifestSHA256']
    models={};retained={}
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url
        for entry in read(p)['models']:
            assert entry['uid']not in models;models[entry['uid']]=entry
            if entry['uid']in [PARENT,PEER]:
                retained[entry['uid']]=entry;refs.append(p);a=p.parent/entry['asset'];assert digest(a.read_bytes())==entry['sha256'];refs.append(a)
                if entry['uid']==PARENT:assert digest(p.read_bytes())==audit['catalogueSHA256']
    assert len(models)==7108 and set(retained)=={PARENT,PEER}
    forms=take(cfg['scope'],'256319:0-forms.json.gz');assert len(forms)==3 and{r['building']['uid']for r in forms}=={UID,PARENT,PEER}
    for r in forms:
        p=ROOT/'3d-viewer'/r['tile'];assert digest(p.read_bytes())==r['tileSHA256']and [f for f in read(p)['buildings']if f['uid']==r['building']['uid']]==[r['building']];refs.append(p)
    browser=cfg['browser'];cat=take(browser,'catalogue.json',True);assert verify_metadata(cat['models'],cfg['sources'],cfg['supportByUid'],original,models,audit)
    metrics=take(current+'-runtime','metrics.json');policy=module('parkview_whole_source_policy',HERE/'acceptance-policy.py');refs.append(HERE/'acceptance-policy.py');raw_policy=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=proof),metrics['rows'][0],metrics['profiles']['mobile']);assert raw_policy==['terrain-intersects-source-over-0.5m','ground-contact-unresolved']
    support=take('government-xl-parkview256319-installed-support-sequence-v1-20261104-strict-support');clearance=take('government-xl-parkview256319-compound-context-v1-20261104-clearance');buried=take('government-xl-parkview256319-compound-context-v1-20261104-buried')
    assert len(support['rows'])==len(clearance['rows'])==len(buried['rows'])==4
    assert len({r['sourceWorldSHA256ByUid'][UID]for r in support['rows']})==1,'Own-ground foundation reuse requires identical complete source worlds'
    foundation=take(current+'-runtime');assert foundation['rows'][0]['completeTerrainTriangles']==11351 and foundation['rows'][0]['fullyBuriedTriangles']==4 and foundation['rows'][0]['fullyBuriedUpwardTriangles']==0
    # The bounded review authenticates every raw wall/cap/path and burial face,
    # including the five-facet compound envelope and all forty current warnings.
    assert all(r['completeSourceFaces']==11351 and r['compoundCapPathsPassed']and r['negativeNonWallFaces']==[]for r in clearance['rows'])
    reports=[];images=[];oldimages=[];capture_reports=[];seenpath=BASE/'government-xl-parkview256319-private-inspection-sheets-v1-20261104/ROOT-OBSERVATIONS.json';seen=read(seenpath);assert seen['actuallyInspected']and seen['sourceExports']==12;refs.append(seenpath);seen_images={r['path']:r['sha256']for r in seen['exports']};assert len(seen_images)==12
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];capture_reports.append(report);reports.append(ref(BASE/browser/str(width)/'staged-browser.json'))
        source_views=[v for v in report['views']if'time'in v];assert len(source_views)==2
        if width==390:assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}=={UID}
        assert report['jointViews']and all({m['uid']:m['sourceSHA256']for m in r['models']}==cfg['sources']and all(m['active']and m['visible']and not m['fallbackFaces']for m in r['models'])for r in report['jointViews'])
        for is_source,views in [(True,source_views),(False,report['retainedNativeOwnViews'])]:
            assert len(views)==(2 if is_source else 4)
            for v in views:
                assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']
                assert v['sourceSHA256']==(SHA if is_source else retained[v['uid']]['sha256'])
                if is_source:assert v['solidAppearance']and v['pick']==v['collision']==UID
                else:assert all(v['meshVisibility'])and not any(v['wireframeFlags'])and not v['overflow']
                p=BASE/browser/str(width)/v['file'];item=dict(**ref(p),uid=v['uid'],width=width,time=v['time']);assert seen_images[item['path']]==item['sha256']==pins[browser][item['path']];refs.append(p);(images if is_source else oldimages).append(item)
    config=take(browser,'browser-config-390.json',True);assert verify_browser_native_scope(config,cfg['sources'],cfg['supportByUid'],cfg['retainedNativeUids'],models,capture_reports)
    result=dict(uids=[UID],sourceSHA256ByUid=cfg['sources'],requiredOriginalAssembly=cfg['sources'],supportByUid=cfg['supportByUid'],identityAccepted=True,identityProof=proof,identityProofByUid={UID:proof},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=3,leaseResources=['building:'+u for u in sorted([UID,PARENT,PEER])],currentManifest=ref(manifest),currentManifestSHA256=mh,rawCanonicalFailuresPreserved=True,rawDirectPolicyReasons={UID:raw_policy},rawCompoundFoundationRows=support['rows'],rawClearanceRows=clearance['rows'],rawBuriedRows=buried['rows'],boundedSourceContext=context,boundedSourceContextReview=ref(BASE/cfg['sourceContextReview']/'ROOT-SOURCE-CONTEXT-REVIEW.json'),supportEligibilityAudit=audit,supportEligibilityReview=ref(BASE/cfg['parentApprovalAudit']/'audit.json'),retainedNativeEntries=retained,retainedNativeUids=cfg['retainedNativeUids'],acceptedInstalledSupportContacts=[dict(uid=UID,nativeUid=PARENT,physicalInterpretationAccepted=True,rawContactSummary=next(r for r in contacts['rows']if r['nativeUid']==PARENT))],acceptedAdjacentNativeContacts=[dict(uid=UID,nativeUid=PEER,physicalInterpretationAccepted=True,rawContactSummary=next(r for r in contacts['rows']if r['nativeUid']==PEER))],completeCurrentNativeContactRoles=roles['rows'],unresolvedExternalBasicContacts=[],sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,imagesActuallyViewed=images,retainedImagesActuallyViewed=oldimages,browserReports=reports,visualAcceptance=True,originalSourceReviewAccepted=True,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawPolicyReasons=raw_policy,sourceSpecificReviewsResolveApplicability=True,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,executorModelAndEffort='unverified',interpretation=context['basis'],scope='Exact immutable original-source port only. Guarded staging, publication, actual live inspection and independent complete-ledger/old-assets readback remain mandatory; no optimisation or architecture modelling.')
    assert verify_native_scope(scope,contacts,models,cfg['sources'],cfg['supportByUid'],set(cfg['retainedNativeUids']),7108,result)
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('parkview_whole_original_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-parkview-source-physical-neighbour-and-browser-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
