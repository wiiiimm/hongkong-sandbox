"""Persist completed Airport Angle Station diagnostics without granting acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-airport-angle-two-after-pier-'
BATCH = PREFIX + 'progress-checkpoint-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, phases = [Path(__file__)], []
    for folder in sorted(BASE.glob(PREFIX + '*-20261025')):
        if not (folder / 'result.json').exists():
            continue
        receipt, pins = authenticate(folder)
        refs.append(folder / 'result.json')
        phases.append(dict(batch=folder.name, jobId=receipt['jobId']))
    browser = BASE / (PREFIX + 'unapproved-browser-v1-20261025')
    _, pins = authenticate(browser)
    images = []
    for width in [390, 1280]:
        report = read(browser / str(width) / 'staged-browser.json')
        assert report['passed'] and not report['errors']
        for view in report['views']:
            if 'time' not in view:
                continue
            path = browser / str(width) / view['file']
            key = str(path.relative_to(ROOT))
            assert digest(path.read_bytes()) == pins[key]
            refs.append(path)
            images.append(dict(uid=view['uid'], width=width, time=view['time'],
                               path=key, sha256=pins[key]))
    assert len(images) == 8
    result = dict(
        uids=['landsd/177765:0', 'landsd/176472:0'], phases=phases,
        newlyInstalled=0, installationApproved=False, physicalAcceptance=False,
        identityAccepted=False, visualAcceptance=False, publication=False,
        permanentRejection=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        aiGeometryModelling=False, imagesActuallyViewedByRoot=images,
        currentFixedXL=dict(installed=373, unfinished=148, total=521),
        currentOfficialDetailedActors=6944,
        observations=[
            'ROOT opened all eight private desktop/mobile day/night exports. Original gantry roofs, pillars and machinery are visible. Night materials remain dark. The first mobile 177765 capture retains the other member as BASIC while it loads; later 176472 captures show the original pair. Automated checks and image inspection are distinct from final assembly acceptance.',
            'Both final four-world foundation contexts pass the existing policy, with zero upward burial. 176472 retains one downward basal face 460, area fraction about 0.000587448, below the existing 0.001 limit. ROOT opened the V1 diagnostic region-1 image of this exact original facet; it is a lower closure, not an upward exposed surface. All 19 affected wall paths pass. Preserve raw aggregate nonwall/cap flags.',
            'The final 3358-triangle terrain retains all 3233 previous triangles plus 125 bounded seam covers. Exact residual coverage passes for both full originals; both current neighbour forms pass. No building geometry changes.',
            'Exact compound projection now persists 99.474144/99.715194 percent coverage of the two current footprints. Raw individual coverage/extent failures remain; maximum extents are 18.873669/43.120926 metres. Same permit PR11/2006(OP), exact source roots and source graphs are evidence, not blanket physical approval.',
        ],
        remainingWork=[
            'Complete source-specific compound identity and source-role review, retaining raw extent and own-footprint failures.',
            'Bind final four-world ground, exact terrain coverage, neighbour, original-pair contact and actually viewed image evidence into final review.',
            'Only after qualification: commit/push, guarded installation, fresh live exports, independent full-old-assets/full-521 readback, inventory refresh and installation commit/push.',
        ])
    save(out / 'remaining-work.json', result)
    module('airport_angle_progress_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-airport-angle-completed-diagnostics-checkpoint', refs, result)


if __name__ == '__main__':
    main()
