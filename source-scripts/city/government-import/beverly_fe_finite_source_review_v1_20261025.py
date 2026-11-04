"""Bind ROOT's inspected F/E exports and bounded original-joint/support interpretation."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-beverly-fe-finite-source-review-v1-20261025'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accept-exports-actually-viewed-by-root',action='store_true',required=True)
    parser.parse_args()
    out = BASE/BATCH
    assert not out.exists()
    refs,pins = [Path(__file__)],{}
    def take(batch,name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    config_path = BASE/'government-xl-beverly-fe-finite-original-install-config-v1-20261025.json'
    config = read(config_path)
    refs.append(config_path)
    sources = config['sources']
    selection = take(config['runtime'],'selection.json.gz')
    assert {r['uid']:r['sourceSHA256'] for r in selection['rows']} == sources
    identity_batch = 'government-xl-beverly-fe-after-k-identity-v1-20261025'
    identity = {}
    for uid,sha in sources.items():
        proof = take(identity_batch,uid.split('/')[1]+'/identity.json')
        assert proof['passed'] and proof['reasons'] == [] and proof['sourceSHA256'] == sha
        assert all(proof['proof'][k] for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
        identity[uid] = proof['proof']
    for batch in ['government-xl-beverly-256334-after-k-foundations-v1-20261025',
                  'government-xl-beverly-e-after-k-foundations-v1-20261025']:
        foundation = take(batch,'summary.json')
        assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
        assert all(r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
    finite = take(config['finiteEvidence'],'summary.json')
    bindings = take(config['finiteEvidence'],'support-bindings.json')
    assert finite['sourceSHA256ByUid'] == sources and finite['completeFourWorldCanonicalRetainedBasicSupport'] is False
    assert finite['completeFourWorldFiniteRetainedBasicSupport'] is True
    assert sum(r['verifiedPaths'] for r in finite['rows']) == 448
    scope = take(config['scope'],'summary.json')
    forms = {}
    for row in scope['rows']:
        assert not row['nearbyNativeActors'] and row['currentNativeActorsChecked'] == config['currentNativeActors']
        for item in take(config['scope'],row['uid'].split('/')[1]+'-forms.json.gz'):
            form = item['building']
            assert form['uid'] not in forms or forms[form['uid']] == form
            forms[form['uid']] = form
    assert sum(r['currentFormsWithinTwoMetreRegion'] for r in scope['rows']) == config['neighbourForms'] == 7
    locus = take('government-xl-beverly-fe-joint-locus-v1-20261025','summary.json')
    assert locus['sourceSHA256ByUid'] == sources and locus['recordedFootprintOverlapM2'] == locus['recordedFootprintDistanceM'] == 0
    assert {r['structure']['OPNo'] for r in locus['primaryRecords']} == {'H141/88'}
    roles = take(config['pairRoles'],'summary.json')
    assert all(r['contactCount'] == 34 and r['roles'] == {'source-edge-surface-contact':15,'transverse-surface-crossing':15,'surface-point-contact':4} for r in roles['rows'])
    reports,images,metadata = [],[],[]
    browser = config['browser']
    for width in [390,1280]:
        report_path = BASE/browser/str(width)/'staged-browser.json'
        report = take(browser,str(width)+'/staged-browser.json')
        assert report['passed'] and not report['errors'] and report['retainedNativeOwnViews'] == []
        reports.append(dict(path=str(report_path.relative_to(ROOT)),sha256=digest(report_path.read_bytes())))
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 4 and {(v['uid'],v['time']) for v in views} == {(u,t) for u in sources for t in ['15:00','22:00']}
        for view in views:
            assert view['active'] and view['visible'] and view['fullyFramed'] and view['solidAppearance'] and not view['fallbackFaces']
            assert view['pick'] == view['collision'] == view['uid'] and view['sourceSHA256'] == sources[view['uid']]
            support = view['retained']['landsd/233218:0']
            assert support == dict(loaded=True,detailedActive=False,hidden=False,base=41.4,height=34.5,baseSource='landsd')
            path = report_path.parent/view['file']
            key = str(path.relative_to(ROOT))
            assert digest(path.read_bytes()) == pins[browser][key]
            refs.append(path)
            image = dict(path=key,sha256=pins[browser][key])
            images.append(image)
            metadata.append(dict(**image,uid=view['uid'],width=width,time=view['time']))
        if width == 390:
            witnesses = report['candidateDependencyFallbacks']
            assert len(witnesses) == 1 and witnesses[0]['failedUid'] == 'landsd/256142:0' and witnesses[0]['uid'] == 'landsd/256334:0'
            assert not witnesses[0]['active'] and witnesses[0]['ownFeaturePresent']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    pair_ref = dict(path=str((BASE/config['pairRoles']/'summary.json').relative_to(ROOT)),sha256=digest((BASE/config['pairRoles']/'summary.json').read_bytes()))
    review = dict(uids=list(sources),sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,
                  identityAccepted=True,identityProof={k:all(p[k] for p in identity.values()) for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
                  identityProofByUid=identity,completeNeighbourInterpretationAccepted=True,
                  completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=False,
                  completeFourWorldFiniteRetainedBasicSupport=True,completeCurrentNeighbourChecks=7,
                  retainedCurrentBasicSupportUids=['landsd/233218:0'],retainedBasicSupportDependencies=bindings,
                  replacementDependenciesByUid=config['replacementDependenciesByUid'],
                  acceptedExactOriginalPair=True,acceptedOriginalPairRoles=pair_ref,
                  retainedNativeEntries={},retainedImagesActuallyViewed=[],
                  leaseResources=sorted('building:'+u for u in forms),terrainEdits=False,
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),
                  sourceGeometryChanges=0,sourcePoseChanges=0,visualAcceptance=True,originalSourceReviewAccepted=True,
                  imagesActuallyViewed=images,imagesActuallyViewedMetadata=metadata,browserReports=reports,
                  installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,
                  qualification='Accept this exact original F/E pair with its existing narrow façade-joint crossings retained. Both independently identified30-storey towers share occupancy permitH141/88 and touching recorded footprints. All34 original contacts remain, including15 transverse crossings contained in0.078218m east by0.272061m Z; source projection overlap1.435277m2 is diagnostic, not penetration volume or proof of engineering intent. ROOT inspected the joint plan and all8 V3 private desktop/mobile day/night exports: both original façades,balconies,roofs and podium interfaces are readable, with no new visible static defect. V2 foreground-occluded views remain rejected. Original grey/darknight materials and existing BASIC lighting are unchanged. Typed currentBASIC233218 stays visible/unsuppressed;448 exactroof-contact paths and byte-identical4world continuous contexts provide separate positive evidence while canonical failures/coarse global bounds stayraw. F must waitfororiginalE toreplace the mismatching BASIC neighbour; Eoriginal versus F BASIC isclear. Actual mobile Edownloadfailure leavesF inactive withownBASICfeature visible, then retries/joint activation pass. Gnoncandidate isclear, all6955installednativebounds aredisjoint. No source/terrain/scale changes, geometry modelling, structural-closure or zero-interpenetration claim. Guarded live installation and fullreadback remain mandatory.')
    joint_diagram=BASE/'government-xl-beverly-fe-joint-locus-v1-20261025/joint-plan-and-locus.png'
    joint_key=str(joint_diagram.relative_to(ROOT))
    assert digest(joint_diagram.read_bytes())==pins['government-xl-beverly-fe-joint-locus-v1-20261025'][joint_key]
    refs.append(joint_diagram)
    review['jointDiagramActuallyViewedByRoot']=dict(path=joint_key,sha256=digest(joint_diagram.read_bytes()))
    save(out/'ROOT-PHYSICAL-REVIEW.json',review)
    save(out/'ROOT-SOURCE-REVIEW.json',review)
    module('beverly_fe_finite_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'bounded-original-pair-availability-finite-support-and-view-review',list(dict.fromkeys(refs)),review)
if __name__ == '__main__':
    main()
