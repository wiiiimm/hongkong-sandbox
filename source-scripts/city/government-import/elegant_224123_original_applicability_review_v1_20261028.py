"""Bounded ROOT applicability judgement for one complete original; no publication.

Accepts the exact government representation, without correcting footprint height
or certifying contemporary surveyed/as-built elevation. Generic gates unchanged.
"""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-elegant-garden-'
BATCH = PREFIX + '224123-original-applicability-review-v2-20261028'
UID = 'landsd/224123:0'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    leasepath = local / 'reservation.json'
    assert not out.exists()
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('exact-original-applicability-' + str(uuid.uuid4()),
                                   ['building:' + UID], batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath,
                                [sys.executable, __file__, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}

    def take(suffix, name):
        folder = BASE / (PREFIX + suffix + '-20261028')
        if suffix not in pins:
            pins[suffix] = authenticate(folder)[1]
            refs.append(folder / 'result.json')
        path = folder / name
        assert digest(path.read_bytes()) == pins[suffix][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    packet = take('eight-identity-packet-v1', '224123:0-packet.json')
    identity = take('identity-boundary-reviews-v1', '224123:0-identity-review.json')
    assert packet['sourceGraphVerified'] and packet['exactTypedRouteQualified']
    assert packet['uniqueOfficialActiveCSUID'] and packet['completeSourceFaces'] == 264
    assert identity['identityOnlyApproved'] and identity['sourceSHA256'] == packet['sourceSHA256']
    assert packet['officialRecord']['BuildingCSUID'] == '3231116408T20050430'
    assert packet['officialRecord']['Storeys'] == 6
    contextpath = BASE / (PREFIX + 'height-context-draft-v1-20261028') / 'height-context.json'
    context = read(contextpath)
    refs.append(contextpath)
    assert context['sourceSHA256'] == packet['sourceSHA256']
    assert context['governmentStoreys'] == context['osmStoreys'] == 6
    assert context['rawTopHeightConflictUnresolved']
    for key in ['identityPacket', 'osmParentWay']:
        ref = context[key]
        path = ROOT / ref['path']
        assert digest(path.read_bytes()) == ref['sha256']
        refs.append(path)
    osm = read(ROOT / context['osmParentWay']['path'])
    way = next(e for e in osm['elements'] if e['type'] == 'way' and e['id'] == 322839773)
    assert way['tags']['building:levels'] == '6'
    probe = BASE / (PREFIX + 'height-source-revision-probe-v1-20261028')
    revision = read(probe / 'summary.json')
    assert revision['sourceSHA256'] == packet['sourceSHA256']
    assert revision['modelId'] == packet['modelId'] == 'B323111640801063C0'
    assert revision['sameArchiveETag'] and revision['exactDirectoryMembersUnchanged']
    assert len(revision['currentCandidates']) == 1
    refs.extend(p for p in probe.rglob('*') if p.is_file())
    images = []
    for suffix, width in [('full-scene-preview-browser-v2', 1280),
                          ('full-scene-preview-browser-v4', 390)]:
        filename = f'{width}/staged-landsd-224123-0-{width}-1500-canvas.png'
        folder = BASE / (PREFIX + suffix + '-20261028')
        if suffix not in pins:
            pins[suffix] = authenticate(folder)[1]
            refs.append(folder / 'result.json')
        path = folder / filename
        assert digest(path.read_bytes()) == pins[suffix][str(path.relative_to(ROOT))]
        refs.append(path)
        images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == identity['currentManifestSHA256']
    refs.append(manifest)
    result = dict(
        uid=UID, uids=[UID], reviewer='Codex ROOT', sourceSHA256=packet['sourceSHA256'],
        modelId=packet['modelId'], buildingCSUID=packet['officialRecord']['BuildingCSUID'],
        currentManifestSHA256=identity['currentManifestSHA256'],
        sourceSpecificOriginalApplicabilityAccepted=True,
        exactCompleteGovernmentRepresentationAccepted=True,
        rawTopHeightConflictUnresolved=True, recordedElevationsUnchanged=True,
        contemporarySurveyedElevationCertified=False,
        completeCurrentAsBuiltReconstructionCertified=False,
        sourceYRange=packet['sourceYRange'], recordedYRange=identity['recordedYRange'],
        rawIdentityVerbatim=packet['rawIdentityVerbatim'],
        imagesActuallyInspected=images,
        basis=[
            'The requested acquisition deliverable is the complete original government representation at its native fixed 1x pose. This exact current typed source has a verified complete graph, exact active CSUID association, and unchanged archive membership/ETag. There is no evidence of an omitted node or a substituted landmark identity.',
            'Both the official occupation/storey context and separately linked OSM parent classify this feature as six storeys. The reviewed original day views show a coherent lower building with roof/parapet details beside taller neighbouring towers. They support using this complete authored representation; they are not an independent measured elevation survey.',
            'ROOT accepts this exact original as applicable to the registered feature rather than stretching it to the conflicting 2D extrusion height. The 36.84m native top versus 88.7m recorded top remains unresolved and visible in provenance. Neither field is corrected or declared erroneous; this approval does not certify a current as-built height.',
            'Acceptance is limited to this source SHA and current form/manifest context. It introduces no global height tolerance, source clipping, pose adjustment, procedural architectural addition or pass flag on the failed generic spatial tests.',
            'Independent original foundation/support, all neighbouring interfaces, atomic activation, retained BASIC/native guards, full canonical publisher and live browser verification remain mandatory before installation.'
        ],
        requiresIndependentPhysicalAndPublicationQualification=True,
        sourceGeometryChanges=0, sourcePoseChanges=0,
        evidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        placementReviewed=False, physicalAccepted=False,
        installationApproved=False, publication=False)
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('original_applicability_review_freeze',
           HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'root-exact-complete-government-original-applicability-with-retained-height-conflict',
        list(dict.fromkeys(refs)), read(out / 'summary.json'))
    print('Exact original applicability reviewed; conflicting elevation retained; no installation approval.')


if __name__ == '__main__':
    main()
