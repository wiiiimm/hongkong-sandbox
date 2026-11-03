"""Freeze actual ROOT inspection of the four complete lower-source exports.

This records bounded observations, without source-role or physical approval.
"""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
SOURCE = 'government-xl-silvercord-lippo-complete-lower-source-views-v1-20261103'
BATCH = 'government-xl-silvercord-lippo-complete-lower-root-inspection-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    receipt, pins = authenticate(BASE / SOURCE)
    path = BASE / SOURCE / 'summary.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    source = read(path)
    assert receipt['jobId'] == '89fb07d53d299b73b5d0c3a0ef3f51386f38e5c69feafc6a6afc0d66a106617a'
    assert source['uids'] == UIDS and not source['sourceRoleAccepted']
    images = source['exports']
    assert len(images) == 4 and {(r['uid'], r['display']) for r in images} == {
        (uid, display) for uid in UIDS for display in ['whole-original', 'grade-band']}
    refs = [Path(__file__), BASE / SOURCE / 'result.json', path]
    for row in images:
        image = ROOT / row['path']
        assert digest(image.read_bytes()) == row['sha256'] == pins[row['path']]
        refs.append(image)
    review = dict(uids=UIDS, reviewer='Codex ROOT', imagesActuallyInspected=images,
        allListedExportsActuallyInspected=True, imageCount=4, obliqueViewsPerExport=2,
        observations=[
            'Silvercord whole-source and grade-band exports show affected facets concentrated along the lower perimeter wall skins. Red marks the entire partly negative source triangle, including its clear upper portion; it is not a map of buried surface area.',
            'Silvercord grade-band uses the global captured-ground maximum and therefore retains much of the full building height. It is not a tight basement section. The tiny three-face packet is unresolved at this scale; the separately inspected local exports and exact contacts remain necessary.',
            'Lippo whole-source export shows the complete original low podium and perimeter walls against green actual-drawn terrain. Its grade-band export clips the display to the low perimeter: terrain crosses the lower wall context, while upper original surfaces are outside that display crop.',
            'All four exports are transparent finite-geometry context plots, not architectural photographs or live viewer output. They do not identify a particular facet as an as-built basement or foundation. The previously truncated Lippo whole-source tool call is not credited; the complete image was reopened and actually inspected.'
        ], sourceRoleAccepted=False, physicalAcceptance=False, visualAcceptance=False,
        installationApproved=False, publication=False, sourceGeometryChanges=0,
        sourcePoseChanges=0, sourceEvidenceInterpretationUsedAI=True,
        aiGeometryModelling=False, modelAndEffort='Not verified from available runtime metadata',
        qualification='Actual inspection of the four exact exported files only. All raw source, buried-area, rim and support warnings remain; no numerical or publication gate changes.')
    save(BASE / BATCH / 'ROOT-EXPORT-INSPECTION.json', review)
    assert reservations.owns(lease)
    module('silvercord_lippo_lower_actual_inspection', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'actual-four-complete-lower-source-export-inspection', refs, review)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('silvercord-lippo-lower-inspection-' + str(uuid.uuid4()),
            ['building:' + uid for uid in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
