"""Bounded numeric identity review of four exact, unchanged government originals.

This does not make the failed footprint/cell tests pass or approve placement.
"""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-greenfield-after-fung-yip-'
BATCH = P + 'bounded-source-identity-review-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    selection = take(P + 'selection-v1-20261025', 'selection.json.gz')
    rows = {r['uid']: r for r in selection['rows']}
    sources = {u: r['sourceSHA256'] for u, r in rows.items()}
    context = take(P + 'source-footprint-context-v1-20261025', 'summary.json')
    metrics = {r['uid']: r for r in context['rows']}
    official = take(P + 'primary-records-v1-20261025', 'footprints.json')['features']
    official = {f['attributes']['BuildingCSUID']: f['attributes'] for f in official}
    assert len(rows) == len(official) == 4 and set(rows) == set(metrics)
    raw, proofs = {}, {}
    for u, row in rows.items():
        f = row['source']['building']
        a = official[f['buildingCSUID']]
        assert a['Status'] == 'Active' and a['BuildingCSUID'] == f['buildingCSUID']
        assert a['BuildingBlockType'] == f['structureType']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == sources[u]
        refs.append(asset)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(v for v in read(tile)['buildings'] if v['uid'] == u) == f
        refs.append(tile)
        r = raw[u] = take(P + 'identity-v1-20261025', u.split('/')[1] + '/identity.json')
        assert r['sourceSHA256'] == sources[u]
        assert r['originalOwnership']['sourceGraphVerified'] and r['originalOwnership']['originalRootName'] == row['modelId']
        assert r['freshCurrentIdentity']['exactObjectAndCSUID'] and r['exactCurrentComponentRoute']['qualified']
        assert metrics[u]['sourceSHA256'] == sources[u] and metrics[u]['completeOriginalFaces'] == row['triangles']
        proofs[u] = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True,
                         identityAccepted=True, exactOwnedOriginalRoot=row['modelId'],
                         freshOfficialCSUID=f['buildingCSUID'], rawGeometryReasonsRetained=r['reasons'])
    small = metrics['landsd/195705:0']
    assert small['sourceCoverageCurrent'] > .999999 and small['sourceCoverageLive'] > .999999
    assert not small['exactWholeGeorefCellCovered']
    long = metrics['landsd/198115:0']
    assert .943 < long['sourceCoverageCurrent'] < .945 and .938 < long['sourceCoverageLive'] < .940
    assert long['exactWholeGeorefCellCovered'] and 12.58 < long['missingCurrentAreaM2'] < 12.60
    primary = metrics['landsd/258419:0']
    assert primary['sourceCoverageCurrent'] > .99 and primary['publishedPermitFamilyIncludesThisCSUID']
    assert all(not metrics[u]['publishedPermitFamilyIncludesThisCSUID'] for u in rows if u != 'landsd/258419:0')
    assert len(context['imagesActuallyViewed']) == 8
    for q in context['imagesActuallyViewed']:
        assert q['actuallyViewed']
        p = ROOT / q['path']
        assert digest(p.read_bytes()) == q['sha256']
        refs.append(p)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == context['currentManifestSHA256']
    refs.append(manifest)
    result = dict(
        uids=sorted(sources), sourceSHA256ByUid=sources, requiredOriginalAssembly=sources,
        reviewer='ROOT', currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
        identityAccepted=True,
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        identityProofByUid=proofs, rawIdentityProofs=raw, rawGeometryMetrics=metrics,
        figuresActuallyViewed=context['imagesActuallyViewed'],
        genericIdentityPolicyChanges=False, rawFootprintAndCellFailuresPreserved=True,
        footprintCoverageGatePassedFor198115=False, wholeCellGatePassedFor195705=False,
        fullFootprintArchitectureCompletionClaimed=False,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False,
        visualRuntimeAcceptance=False, installationApproved=False,
        observations=[
            'Accept numeric source-to-viewer identity only for these four exact registered originals. Every immutable asset has its exact owned government root, exact current object/CSUID, qualified unique current component route and fresh active official footprint. ROOT inspected all8complete-source plan/perspective figures. This is a faithful import of each full government source body, not reconstruction or a claim that its planar footprint is complete.',
            '195705is the small low rectangular original. It covers100percent of its own current and fresh official footprints. Its one-metre rounded geographic cell extends beyond the original projection; keep that cell failure false. Complete target coverage, the exact owned root, official identity and unique component route provide the independent bounded association.',
            '198115is the long low roof/wall assembly with upstanding roof blocks. Its complete original follows the same distinctive long diagonal current/live footprint at the registered location, and its whole geographic cell and exact component route qualify. Preserve94.4009percent current and93.8749percent live planar coverage and the12.5879m2current difference. Those source/footprint edge discrepancies are a declared limitation of this unchanged government body; neither test is rounded to95percent, and no missing geometry is invented. Numeric identity follows the independent exact registered root/CSUID/route/cell plus inspected complete shape, not a changed coverage threshold.',
            '258419is the complete curved multi-level shopping podium, with99.18percent own coverage and street-side extensions visible in the original diagrams. Its three permit families cover the estate tower/podium records. Preserve its raw10.9202202mextent and overlap failures; the original numeric ownership and complete source body are accepted without moving, cropping or suppressing neighbouring actors.332916is the uniquely routed low circular original, with its own active official footprint and99.55percent planar coverage.',
            'The three auxiliary CSUIDs are absent from the main podium permit families. No common ownership, shared permit or entire-landmark membership is inferred for them from that packet. Their support/interface and physical roles require separate source evidence. Canopy217024remains a separate BASIC actor; no ownership reassignment or suppression is authorised.',
            'Current source-specific physical interpretation, all four coordinate streams, exact ground coverage, full source/terrain neighbours, actual fresh browser exports and guarded publication/readback remain independent requirements. This numeric review grants no installation credit or general footprint/cell exception.'
        ])
    save(out / 'ROOT-IDENTITY-REVIEW.json', result)
    module('greenfield_bounded_identity', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-exact-registered-original-greenfield-numeric-identity-review', refs, {k: v for k, v in result.items() if k != 'rawIdentityProofs'})


if __name__ == '__main__':
    main()
