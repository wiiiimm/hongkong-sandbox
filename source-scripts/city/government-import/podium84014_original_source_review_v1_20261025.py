"""Bind ROOT's inspected original source/assembly review; never publish assets."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from podium84014_original_catalogue_scope_v1_20261025 import SOURCES,SUPPORTS,verify_metadata
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-podium84014-original-source-review-v1-20261025'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
        path=BASE/name/path;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime='government-xl-84014-three-original-runtime-v1-20261024';selection=take(runtime,'selection.json.gz')
    assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    identity='government-xl-84014-three-original-identity-v1-20261024';ids=take(identity,'summary.json');assert len(ids['rows'])==3
    identity_rows=[]
    for row in ids['rows']:
        uid=row['uid'];proof=take(identity,uid.split('/')[1]+'/identity.json')
        assert proof['originalOwnership']['sourceGraphVerified']and proof['sourceSHA256']==SOURCES[uid]
        assert proof['exactCurrentComponentRoute']['qualified']and proof['exactWholeCellCoverage']['covered']
        current=proof['freshCurrentIdentity'];assert current['exactObjectAndCSUID']and current['targetCoveredBySourceProjection']>=.95 and current['sourceExcessMaximumDistanceFromTargetM']<=10
        if uid=='landsd/84014:0':assert row['reasons']==['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap']
        else:assert row['passed']and not row['reasons']
        identity_rows.append(dict(uid=uid,sourceSHA256=SOURCES[uid],rawReasons=row['reasons'],exactOwnedRoot=proof['originalOwnership']['originalRootName'],exactTypedCurrentRoute=True,wholeGeorefCellCovered=True,fullSourceFaces=proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted'],rawCurrentGeometry=current))
    original=take('government-xl-84014-original-physical-review-v1-20261025','ROOT-PHYSICAL-REVIEW.json');assert original['sourceSpecificPhysicalInterpretationAccepted']and original['sourceSHA256ByUid']==SOURCES
    scope=take('government-xl-84014-three-original-current-scope-v1-20261025','summary.json');assert all(not r['nearbyNativeActors']and r['currentNativeActorsChecked']==6908 for r in scope['rows'])
    for name in ['government-xl-84014-current-foreign-contacts-v1-20261024','government-xl-84014-three-original-pair-context-v1-20261024','government-xl-84014-adjacent-low-basic-contact-views-v1-20261024']:take(name,'summary.json')
    browser='government-xl-84014-three-original-private-browser-v1-20261025';take(browser,'summary.json') if (BASE/browser/'summary.json').exists()else None
    if browser not in pins:pins[browser]=authenticate(BASE/browser)[1];refs.append(BASE/browser/'result.json')
    catalogue=HERE/'local'/browser/'catalogue.json';assert digest(catalogue.read_bytes())==pins[browser][str(catalogue.relative_to(ROOT))]and verify_metadata(read(catalogue)['models']);refs.append(catalogue)
    reports=[]
    for width in [1280,390]:
        path=BASE/browser/str(width)/'staged-browser.json';assert digest(path.read_bytes())==pins[browser][str(path.relative_to(ROOT))];refs.append(path);r=read(path);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==6
        assert all(v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]for v in views)
        assert any({m['uid']for m in j['models']}==set(SOURCES)and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
        if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(SOURCES)
        reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    inspection=BASE/'government-xl-84014-private-export-inspection-v1-20261025/panel-bindings.json';panels=read(inspection);refs.append(inspection);images=[p for row in panels['rows']for p in row['panels']];assert len(images)==12 and len({p['path']for p in images})==12
    for image in images:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==pins[browser][image['path']];refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    identity_proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True,rows=identity_rows,rawPodiumOverlapPreservedM2=20.824579496753515,sourceSpecificInterpretation='Exact uniquely routed original podium root, matching whole1m GeoRef cell and99.85percent current footprint coverage. The authored end façade/canopy projects over the adjacent low basic actor210816, whose geometry is retained. The inspected complete source plan/perspectives and before/after finite interface agree with this small extension; it is not a different building or a reason to remodel/trim the original. No common-property or engineering assertion is made. Both original towers independently pass the unchanged raw identity test.')
    physical=deepcopy(original);physical.update(identityProof=identity_proof,identityAccepted=True,completeCurrentNeighbourChecks=4,completeNeighbourInterpretationAccepted=True,requiredOriginalAssembly=SOURCES,supportByUid=SUPPORTS,neighbourInterpretation='All6908 current native bounds were checked for every source in all4 coordinate streams; no external native overlaps. Four current forms are in scope: the three replaced actors and unchanged basic210816. Exact before/after external contacts and all original assembly pairs are retained. The original tower interfaces replace the coarse-box crossings, and the retained low actor remains visible/unsuppressed. Terrain/forms/other actors are unchanged.',publication=False,installationApproved=False)
    save(out/'ROOT-PHYSICAL-REVIEW.json',physical)
    review={**physical,'reviewer':'ROOT','visualAcceptance':True,'identityAccepted':True,'completeNeighbourInterpretationAccepted':True,'browserReports':reports,'imagesActuallyViewed':images,'privateImageInspectionQualification':'All12 actual exported full frames were inspected via three full-frame sheets. Original dark night materials are retained. The podium early mobile own views include coarse tower companions during failure/retry sequencing; final source own views and final joint checks show all3 originals active. Natural partial foreground occlusion is retained; no unviewed diagnostic region is claimed inspected.','sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'publication':False,'installationApproved':False}
    save(out/'ROOT-SOURCE-REVIEW.json',review);refs.extend([HERE/'podium84014_original_catalogue_scope_v1_20261025.py',HERE/'original_supported_catalogue_scope_v1_20261024.py'])
    module('podium84014_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'reviewed-unchanged-original-podium-two-tower-source-and-private-visual-acceptance',refs,dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyInspected=12,sourceGeometryChanges=0,publication=False))

if __name__=='__main__':main()
