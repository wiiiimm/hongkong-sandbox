"""Freeze bounded ROOT inspection of six camera-diagnostic exports; no acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-elegant-garden-targeted-camera-diagnostic-v1-20261028'
OUT = 'government-xl-elegant-garden-targeted-camera-image-review-v1-20261028'

def main():
    receipt, pins = authenticate(BASE/BATCH)
    path = BASE/BATCH/'390/staged-browser.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    report = read(path)
    assert report['passed'] and report['diagnosticOnly'] and not report['errors']
    rows = report['cameraDiagnostics']
    assert [r['uid'] for r in rows] == ['landsd/100673:0','landsd/171904:0','landsd/213816:0']
    images = []
    for row in rows:
        assert len(row['candidates']) == 36 and len(row['exports']) == 2
        for image in row['exports']:
            p = path.parent/image['file']
            assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
            images.append(p)
    notes = dict(uids=[r['uid'] for r in rows], diagnosticJob=receipt['jobId'],
        actualExportsInspected=6, sourceGeometryChanges=0, visualReviewApproved=False,
        installationApproved=False, physicalAccepted=False, publication=False,
        findings=[
          '100673: prior camera collides with Louis Mansion volume173767. Alternate camera clears collision and reaches17/18sampled source faces. Day/night exports show the stepped component; selected highlight remains.',
          '171904: prior camera collides with174224; centre sightline first hits84940. Alternate camera reaches89/89sampled source faces. Day/night exports expose Fortune building with selection highlight.',
          '213816: prior centre sightline hits174224. Best tested safe angle reaches8/71samples, with171902and171904blocking others. Exports still obscure much of the low podium. No permanent rejection follows.',
          'These selected/private mobile views do not replace the full16joint scene, collision/support/identity, clean unselected views, desktop evidence or three BASIC foundation close-ups.',
          'Inherited selection-order.json allSixteenJointAssertionsRetained=true describes the V4 scaffold and is not a claim that this targeted run executed joint assertions. Only the3target cameraDiagnostics were executed.'],
        next='Targeted clean/unselected joint-context views and three BASIC foundation close-ups; keep all original bytes/poses and runtime budgets unchanged.')
    save(BASE/OUT/'root-observations.json', notes)
    module('camera_image_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        OUT, 'root-targeted-camera-export-inspection-with-bounded-visibility',
        [Path(__file__),BASE/BATCH/'result.json',path,*images],notes)

if __name__ == '__main__':
    main()
