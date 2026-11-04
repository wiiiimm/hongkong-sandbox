"""Bounded exact-source opaque boundary review; not whole-model acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-one-peking-after-twin-'
BATCH = PREFIX + 'hullett-boundary-interface-review-v1-20261101'

def main():
    out = BASE / BATCH
    assert not out.exists()
    refs = [Path(__file__), HERE / 'one_peking_hullett_saved_contact_views_v1_20261101.py']
    pins = {}
    jobs = {}
    def take(batch, name):
        if batch not in pins:
            receipt, pins[batch] = authenticate(BASE / batch)
            jobs[batch] = receipt['jobId']
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    native_batch = PREFIX + 'installed-native-contacts-v1-20261101'
    summary = take(native_batch, 'summary.json')
    assert len(summary['rows']) == 1
    row = summary['rows'][0]
    assert row['uid'] == 'landsd/233985:0' and row['nativeUid'] == 'landsd/73140:0'
    identity = take(PREFIX + 'fresh-current-named-identity-v2-20261101', 'summary.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == identity['currentManifestSHA256']
    refs.append(manifest)
    context_dir = BASE / (PREFIX + 'saved-contact-views-v1-20261101')
    context = read(context_dir / 'context.json')
    assert context['contactJobId'] == jobs[native_batch]
    assert context['approval'] is False
    refs.append(context_dir / 'context.json')
    image = context_dir / 'exact-contact-context-1800x1200.png'
    refs.append(image)
    facets = []
    for source, face_ids in zip(context['sourceRefs'], context['faceIds']):
        path = ROOT / source['path']
        raw = path.read_bytes()
        assert digest(raw) == source['sha256']
        triangles = decode_original_world_triangles(raw)
        facets.append(dict(sourceSHA256=source['sha256'], completeOriginalFaces=len(triangles), contactFacets=[dict(faceId=i, triangle=triangles[i].tolist()) for i in face_ids]))
        refs.append(path)
    modes = []
    expected_pairs = None
    for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
        proof = take(native_batch, '233985:0--73140:0--' + mode + '.json.gz')
        assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0 and proof['geometryChanges'] == 0
        assert len(proof['contacts']) == 12 and all(c['dimension'] == 1 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2 for c in proof['contacts'])
        pairs = sorted((c['sourceFaceA'], c['sourceFaceB']) for c in proof['contacts'])
        if expected_pairs is None:
            expected_pairs = pairs
        assert pairs == expected_pairs
        modes.append(dict(mode=mode, sourceSHA256=row['sourceSHA256'], nativeSHA256=row['nativeSHA256'], contactCount=12, rawFiniteContacts=proof['contacts']))
    decision = dict(uid=row['uid'], nativeUid=row['nativeUid'], reviewer='Codex ROOT', reviewType='bounded-original-opaque-exterior-boundary-interface', interfaceRoleApproved=True,
        sourceSHA256=row['sourceSHA256'], nativeSHA256=row['nativeSHA256'], allFourWorlds=modes, completeContactFacetContext=facets,
        imagesActuallyInspected=[dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes()))], rawCurrentNativeEntry=row['rawCurrentNativeEntry'],
        role='The original podium end-cap and vertical exterior faces meet the retained Hullett southern exterior boundary faces. Preserve both opaque source surfaces and their finite segment intersections.',
        qualification='ROOT inspected the full-source and cropped orthographic views with every contact facet and exact segment. This accepts this specific exterior opaque boundary interface, not shared ownership, legal-boundary accuracy, non-penetrating solids or engineering certification. Neither actor is inferred to support the other. No geometric separation, deletion, suppression, collision exclusion or tolerance change is approved. The complete current retained-neighbour, source foundations, ordinary picking/collision/streaming/fallback checks and guarded publication remain separate requirements. Projected overlap area is not the acceptance basis.',
        evidence=jobs, currentManifestSHA256=identity['currentManifestSHA256'], sourceGeometryChanges=0, sourcePoseChanges=0, installedMetadataChanges=0,
        foreignSupportDependencyApproved=False, collisionExemption=False, physicalAccepted=False, installationApproved=False, publication=False,
        evidenceInterpretationUsedAI=True, aiGeometryModelling=False)
    save(out / 'ROOT-INTERFACE-REVIEW.json', decision)
    save(out / 'summary.json', decision)
    module('one_peking_boundary_review_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-exact-original-opaque-exterior-interface-review', list(dict.fromkeys(refs)), decision)

if __name__ == '__main__':
    main()
