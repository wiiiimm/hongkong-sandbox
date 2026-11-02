"""Prepare June Garden only after complete browser and inspected-export evidence.

Private stage and canonical dry run only. Never installs or changes source bytes.
"""
import argparse, copy, shutil, sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_coordinated_retained_contract_v1_20261027 import verify_metadata
from june_garden_publisher_hooks_v1_20261103 import SOURCES, SUPPORTS, P, SMALL, install

BASE = ROOT/'docs/astra-city/government-import'
PHYSICAL = 'government-xl-tower3-june-garden-six-original-physical-review-v2-20261102'
TERRAIN = 'government-xl-tower3-june-garden-retained-terrain-context-v1-20261102'
PATCH = 'government-xl-tower3-227380-retained-chain-validated-v4-20261102'
ATOMIC = 'government-xl-tower3-june-garden-six-original-private-atomic-browser-v3-20261102'


def ref(p): return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))


def inspected_exports(inspection, expected, root=ROOT):
    assert inspection['allListedExportsActuallyInspected'] is True
    assert inspection['inspectionScope'] == 'complete-source-and-retained-desktop-mobile-exports'
    images = inspection['images']
    assert len(images) == len(expected) and len({r['path'] for r in images}) == len(images)
    assert {r['path']:r['sha256'] for r in images} == expected
    for row in images:
        p = (root/row['path']).resolve(); assert p.is_relative_to(root.resolve())
        assert digest(p.read_bytes()) == row['sha256']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch',required=True); ap.add_argument('--browser-batch',required=True)
    ap.add_argument('--inspection',required=True); a = ap.parse_args()
    for name in [a.batch,a.browser_batch]: assert name.startswith('government-xl-') and '/' not in name
    doc, stage = BASE/a.batch, HERE/'accepted'/a.batch
    assert not doc.exists() and not stage.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch,name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]; refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    physical = take(PHYSICAL,'ROOT-PHYSICAL-REVIEW.json')
    terrain = take(TERRAIN,'summary.json'); browser = take(a.browser_batch,'summary.json')
    atomic = take(ATOMIC,'summary.json')
    assert physical['sourceSHA256ByUid'] == browser['sourceSHA256ByUid'] == atomic['sourceSHA256ByUid'] == SOURCES
    assert physical['identityAccepted'] and physical['sourceSpecificPhysicalInterpretationAccepted']
    assert physical['completeModelBodyNeighbourInterpretationAccepted'] and physical['rawPhysicalFailuresPreserved']
    assert browser['passed'] and browser['retainedNativeActors'] == 69
    assert atomic['passed'] and atomic['cases'] == 7
    assert terrain['proposalTerrainNonRegressionPassed'] and terrain['retainedNativeActors'] == 69
    retained = {r['uid'] for r in terrain['rows']}; assert len(retained) == 69
    images = {}
    for width in [1280,390]:
        report = take(a.browser_batch,str(width)+'/staged-browser.json')
        assert report['passed'] and not report['errors']
        own = report['views']; views = report['retainedNativeOwnViews']
        assert len(own) == 12 and {(r['uid'],r['time']) for r in own} == {(u,t) for u in SOURCES for t in ['15:00','22:00']}
        assert len(views) == 138 and {(r['uid'],r['time']) for r in views} == {(u,t) for u in retained for t in ['15:00','22:00']}
        for row in [*own,*views]:
            assert row['active'] and row['visible'] and row['fallbackFaces'] == 0
            path = BASE/a.browser_batch/str(width)/row['file']
            assert ref(path)['sha256'] == pins[a.browser_batch][str(path.relative_to(ROOT))]
            refs.append(path); images[str(path.relative_to(ROOT))] = ref(path)['sha256']
    inspection = (ROOT/a.inspection).resolve(); assert inspection.is_relative_to(BASE)
    inspected_exports(read(inspection),images); refs.append(inspection)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; before = ref(manifest); refs.append(manifest)
    assert before['sha256'] == physical['currentManifestSHA256'] == terrain['currentManifestSHA256']
    prior = HERE/'local'/a.browser_batch
    # These private files are themselves authenticated by the completed producer.
    for name in ['catalogue.json','source-forms.json','config.json']:
        path = prior/name
        assert ref(path)['sha256'] == pins[a.browser_batch][str(path.relative_to(ROOT))]; refs.append(path)
    catalogue = read(prior/'catalogue.json'); config = read(prior/'config.json')
    originals = take(a.browser_batch,'complete-unapproved-source-entries.json')
    verify_metadata(catalogue['models'],SOURCES,SUPPORTS,originals,{P:None,SMALL:None})
    qualification = dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,identityAccepted=True,
        sourceSpecificPhysicalInterpretationAccepted=True,visualAcceptance=True,privateStageQualified=True,
        currentManifestSHA256=before['sha256'],sourceGeometryChanges=0,sourcePoseChanges=0,
        existingNativeReaccepted=False,publication=False)
    save(doc/'qualification.json',qualification)
    for m in catalogue['models']:
        asset = prior/m['asset']; assert ref(asset)['sha256'] == SOURCES[m['uid']]
        refs.append(asset); target = stage/m['asset']; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(asset,target)
        m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
            sourceIdentityReview=ref(BASE/PHYSICAL/'ROOT-PHYSICAL-REVIEW.json'),
            sourceFunctionalApplicability=ref(doc/'qualification.json'),aiGeometryModelling=False,
            sourceEvidenceInterpretationUsedAI=True,placementReview=a.batch)
    verify_metadata(catalogue['models'],SOURCES,SUPPORTS,originals,{P:None,SMALL:None})
    save(stage/'catalogue.json',catalogue); save(stage/'source-forms.json',read(prior/'source-forms.json'))
    checks = doc/'full-mesh-terrain-checks.json'
    save(checks,dict(rows=[dict(uid=r['uid'],passed=r['proposalTerrainNonRegressionPassed'],terrain=r['raw']['terrain'],raw=r['raw'],existingSourceReapproved=False,existingSupportReapproved=False) for r in terrain['rows']],aiCalls=0,modelGeometryChanges=0,reviewScope='proposal-terrain-nonregression-only'))
    surface,pins[PATCH] = authenticate(BASE/PATCH); refs.append(BASE/PATCH/'result.json')
    entries = copy.deepcopy(config['terrain']); assert len(entries) == 3
    for member in surface['members']:
        e = next(e for e in entries if e['source'] == member['candidate']['path'])
        assert e['sha256'] == member['candidate']['sha256'] and e['replaces'] == member['replaces']
        candidate = ROOT/e['source']; assert ref(candidate)['sha256'] == e['sha256']; refs.append(candidate)
        review = doc/(member['member']+'-native-review.json')
        save(review,dict(status='approved-for-integration',supersededURL=e['replaces']['url'],supersededSHA256=e['replaces']['sha256'],replacementSHA256=e['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=e['replaces']['retainedUids'],replacementTargetUids=read(candidate)['meta']['targetUids'],fullMeshCheck=ref(checks),reviewScope='proposal-terrain-nonregression-only',existingNativeReaccepted=False))
        e.update(destination=e['replaces']['url'],nativeReview=ref(review),area='June Garden exact original source terrain')
    destination='city/data/official-models/'+a.batch+'/catalogue.json'
    plan=dict(areas=[dict(area='June Garden unchanged originals',catalogue=str((stage/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=entries)
    save(stage/'plan.json',plan)
    config.update(stage=str(stage.relative_to(ROOT))+'/',catalogueURL=destination,terrain=entries)
    save(stage/'live-browser-config.json',config)
    pub = module('june_qualified_dryrun',HERE.parent/'island-detail-integration/publish.py')
    install(pub,ROOT,surface,originals,before['sha256']); pub.DOC=doc/'publisher-dry-run'; previous=sys.argv[:]
    try:
        sys.argv=['publish.py',str((stage/'plan.json').relative_to(ROOT))]; pub.main()
    finally: sys.argv=previous
    assert read(pub.DOC/'publication-plan.json')['published'] is False and ref(manifest) == before
    refs.extend([HERE/'june_garden_publisher_hooks_v1_20261103.py',HERE.parent/'island-detail-integration/publish.py'])
    refs.extend(p for p in stage.rglob('*') if p.is_file()); refs.extend(p for p in doc.rglob('*') if p.is_file())
    module('june_qualified_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'qualified-six-original-three-terrain-private-stage',list(dict.fromkeys(refs)),dict(**qualification,qualifiedForLiveVerification=True,newVisibleModels=6,newlyInstalled=0))


if __name__ == '__main__': main()
