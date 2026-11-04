"""Authenticate completed browser evidence and preserve bounded ROOT observations.

Read-only Neon access. No renderer rerun, leases, acceptance or public writes.
"""
from pathlib import Path
from run import ROOT, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-elegant-garden-'
OUT = BASE / (PREFIX + 'completed-browser-audit-v1-20261028')


def main():
    refs = []
    summaries = {}
    receipts = []
    for suffix in ['supported-activation-browser-v3', 'clean-context-views-v1',
                   'exact-camera-views-v1']:
        folder = BASE / (PREFIX + suffix + '-20261028')
        receipt, pins = authenticate(folder)
        receipts.append(dict(batch=folder.name, jobId=receipt['jobId']))
        for relative, sha in pins.items():
            path = ROOT / relative
            assert digest(path.read_bytes()) == sha, relative
        summary = read(folder / 'summary.json')
        assert summary['sourceGeometryChanges'] == summary['sourcePoseChanges'] == 0
        assert summary['installationApproved'] is False and summary['publication'] is False
        summaries[suffix] = summary
        refs.append(dict(path=str((folder / 'result.json').relative_to(ROOT)),
                         sha256=digest((folder / 'result.json').read_bytes())))
    life = summaries['supported-activation-browser-v3']
    assert life['browserPassed'] and life['cases'] == life['expectedCases'] == 17
    for suffix in ['clean-context-views-v1', 'exact-camera-views-v1']:
        assert summaries[suffix]['allPassed']
        assert {r['width'] for r in summaries[suffix]['commands'] if r['passed']} == {1280, 390}
    folder = BASE / (PREFIX + 'exact-camera-views-v1-20261028')
    frames = []
    for width in [1280, 390]:
        report = read(folder / str(width) / 'staged-browser.json')
        assert report['passed'] and len(report['cameraDiagnostics']) == 1
        actor = report['cameraDiagnostics'][0]
        assert actor['uid'] == 'landsd/100673:0'
        assert len(actor['exports']) == 2
        for frame in actor['exports']:
            assert frame['sourceActive'] and frame['sourceSHA256'] == actor['sourceSHA256']
            assert frame['actualMeshBounds'] == frame['collisionBounds'] == actor['bounds']
            assert len(frame['projectedCorners']) == 8
            assert all(-1 < v < 1 for corner in frame['projectedCorners'] for v in corner)
            assert frame['actualNativeCentreRayHits']
            path = folder / str(width) / frame['file']
            assert path.is_file()
            frames.append(dict(width=width, time=frame['time'], path=str(path.relative_to(ROOT)),
                               sha256=digest(path.read_bytes()), meshCollisionBoundsAgree=True,
                               boundingBoxInsideFrustum=True, nativeCentreRayHit=True))
    save(OUT / 'summary.json', dict(
        receipts=receipts, inputRefs=refs, lifecycleCasesPassed=17,
        targetedCleanExports=28, exactCameraFrames=frames,
        rootObservations=[
            'ROOT inspected all 28 targeted clean exports in the preceding continuation, including labelled mobile day/night sheets and desktop day originals/night sheet.',
            'ROOT inspected both exact mobile day/night exports and exact desktop night in this continuation; desktop day was inspected previously.',
            'Tiny original 100673 is a plain low component in similar-coloured original context. Exact source activation, mesh/collision bounds and same-frame native ray hits prove its presence; they do not prove every facet unobscured.',
            'Mobile roof edges are visible in daylight and dark at night. No procedural windows or architectural details were added.',
            'Podiums can be naturally obscured by their towers. These views do not establish measured mobile performance or resolve the separate source-height applicability conflict for 224123.'
        ],
        allLaunchedBrowserWorkersTerminal=True, publicFilesWritten=0,
        neonWrites=0, installationApproved=False, publication=False))
    print('Authenticated three complete Neon receipts; 17 lifecycle cases, 28 clean exports and four exact camera frames. No installation approval.')


if __name__ == '__main__':
    main()
