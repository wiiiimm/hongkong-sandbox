"""Save ROOT's actual 100-export inspection and unresolved camera issues in Neon."""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from elegant_basic_footing_foreign_volume_v1_20261028 import BASE, PREFIX

BATCH = PREFIX+'full-scene-image-qa-v1-20261028'


def main():
    out, local = BASE/BATCH, HERE/'local'/BATCH
    assert out.exists() and not (out/'result.json').exists()
    fixture = BASE/(PREFIX+'full-scene-preview-fixture-v2-20261028')
    fixture_receipt, fixture_pins = authenticate(fixture)
    input_path = fixture/'fixture-inputs.json'
    assert digest(input_path.read_bytes()) == fixture_pins[str(input_path.relative_to(ROOT))]
    inputs = read(input_path)
    resources, lp = set(inputs['resources']), local/'reservation.json'
    if '--owned' not in sys.argv:
        assert not local.exists()
        claim = reservations.claim('elegant-full-scene-image-qa-'+str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs = [Path(__file__), fixture/'result.json', input_path, HERE/'original_browser_contact_sheets_v1_20261028.py']
    checked = []
    for name, batch, width in [('desktop', 'full-scene-preview-browser-v2', 1280), ('mobile', 'full-scene-preview-browser-v4', 390)]:
        directory = BASE/(PREFIX+batch+'-20261028')
        receipt, pins = authenticate(directory)
        report_path = directory/str(width)/'staged-browser.json'
        assert digest(report_path.read_bytes()) == pins[str(report_path.relative_to(ROOT))]
        report = read(report_path)
        assert report['passed'] and not report['errors']
        assert len(report['views']) == 32 and len(report['retainedNativeOwnViews']) == 18
        assert len(report['jointViews']) == 16 and all(len(r['models']) == 16 for r in report['jointViews'])
        refs.extend([directory/'result.json', report_path])
        manifest_path = out/(name+'-contact-sheets.json')
        notes_path = out/(name+'-root-observations.json')
        manifest, notes = read(manifest_path), read(notes_path)
        assert manifest['sourceReportSHA256'] == digest(report_path.read_bytes())
        assert len(manifest['originalImages']) == notes['actualOriginalImagesInspected'] == 50
        assert notes['contactSheetsActuallyOpened'] == list(range(1, 14))
        assert notes['visualReviewApproved'] is notes['installationApproved'] is False
        assert {r['path']: r['sha256'] for r in manifest['originalImages']} == notes['sourceImageHashes']
        for r in manifest['originalImages']:
            path = ROOT/r['path']
            assert digest(path.read_bytes()) == r['sha256'] == pins[r['path']]
            refs.append(path)
        for r in manifest['sheets']:
            path = ROOT/r['path']
            assert digest(path.read_bytes()) == r['sha256']
            refs.append(path)
        refs.extend([manifest_path, notes_path])
        checked.append(dict(viewport=width, browserJob=receipt['jobId'], actualExportsInspected=50,
                            flatSceneWarnings=manifest.get('flatSceneWarnings', []), findings=notes['findings']))
    assert reservations.owns(lease)
    module('full_scene_image_qa_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,
        'root-actual-desktop-mobile-export-inspection-with-explicit-camera-obstructions', list(dict.fromkeys(refs)),
        dict(uids=sorted(inputs['sourceSHA256ByUid']), status='image-inspected-camera-follow-up-required', rows=checked,
             actualExportsInspected=100, softwareViewportCasesPassed=[1280, 390],
             sourceGeometryChanges=0, governmentGeometryChanges=0, visualReviewApproved=False,
             physicalAccepted=False, installationApproved=False, publication=False,
             qualification='ROOT actually inspected all100unchanged exported PNGs through26full-resolution labelled sheets plus5individual desktop images. Completed software cases prove source/retained/joint activation, not unobstructed pixels or source placement. Flat/obstructed views and missing3BASICfoundation close-ups stay explicit pending tasks. No model corruption/permanent rejection, source geometry or original-pose change, visual/publication/install approval is inferred.'))
    print(dict(actualExportsInspected=100, visualReviewApproved=False, next='targeted-camera-visibility-and-foundation-views'), flush=True)


if __name__ == '__main__':
    main()
