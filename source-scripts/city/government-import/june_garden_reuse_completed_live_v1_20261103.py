"""Reuse only complete unchanged mobile/atomic execution; never partial desktop.

Called under the new installation lease after canonical reapplication. Current
publication bytes/configuration and every source bound by the passed mobile
readback must match. No visual or installation approval is created here.
"""
import json
import shutil
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT

OLD = ROOT / 'docs/astra-city/government-import/government-xl-june-garden-original-installed-v1-20261103'
OLD_LOCAL = HERE / 'local' / OLD.name


def committed(path):
    raw = path.read_bytes()
    assert subprocess.check_output(['git', 'show', 'HEAD:' + str(path.relative_to(ROOT))], cwd=ROOT) == raw
    return read(path)


def validate_mobile(report, config, sources):
    assert report['passed'] is True and not report['errors'] and report['mode'] == 'live'
    own = [r for r in report['views'] if 'time' in r]; held = report['retainedNativeOwnViews']
    new = set(config['browserUids']); old = set(config['additionalRetainedUids'])
    assert len(new) == 6 and len(old) == 69 and not new & old and set(sources) == new | old
    assert len(own) == len(report['views']) == 12 and len(held) == 138
    assert {(r['uid'], r['time']) for r in own} == {(u, t) for u in new for t in ['15:00', '22:00']}
    assert {(r['uid'], r['time']) for r in held} == {(u, t) for u in old for t in ['15:00', '22:00']}
    for row in own + held:
        assert row['width'] == 390 and row['active'] and row['visible'] and row['fullyFramed'] and not row['fallbackFaces']
        pixels = row['sourcePixelVisibility']
        assert pixels['visiblePixels'] >= 32 and pixels['otherMeshesRetainedAsOpaqueOccluders'] and not pixels['sourceGeometryChanged']
        assert row['sourceSHA256'] == sources[row['uid']]['sha256'] and row['originalTriangles'] == sources[row['uid']]['triangles']
        assert all(row['meshVisibility']) and not any(row['wireframeFlags'])
    for row in own:
        assert row['pick'] == row['collision'] == row['uid'] and row['solidAppearance']
    joints = report['jointViews']
    assert len(joints) == 6 and {r['selectedUid'] for r in joints} == new
    for row in joints:
        assert row['width'] == 390 and {m['uid']: m['sourceSHA256'] for m in row['models']} == {u: sources[u]['sha256'] for u in new}
        assert len(row['models']) == 6 and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in row['models'])
    fallback = report.get('retainedDeselectionFallbacks', [])
    assert len(fallback) == len(config['keepSelectedForRetainedCapture']) and {r['uid'] for r in fallback} == set(config['keepSelectedForRetainedCapture'])
    for row in fallback:
        assert row['selectedId'] is None and not row['active'] and row['basicLoaded'] and not row['basicHidden'] and row['fallbackFaces'] > 0
        assert row['sourceSHA256'] == sources[row['uid']]['sha256']
    return own, held


def reuse(new_doc, config, atomic_config, lease, verify_atomic):
    assert reservations.owns(lease) and not (new_doc / 'viewport-390').exists() and not (new_doc / 'atomic-live').exists()
    failed = read(OLD / 'failure-recovery.json')
    assert failed['allPublicDestinationsRestored'] and not failed['rollbackErrors'] and not failed['derivedInstalledReviewHistoryRetained']
    assert failed['error'] == "RuntimeError('Original installation interrupted by lease supervisor')"
    refs = [Path(__file__), OLD / 'failure-recovery.json']
    old_plan = ROOT / 'docs/astra-city/model-integration-20260909' / OLD.name / 'publication-plan.json'
    plan = read(old_plan); assert plan['published'] and len(plan['after']) == 5
    for name, sha in plan['after'].items():
        path = ROOT / name
        assert digest(path.read_bytes()) == sha, 'Reapplied public byte context differs: ' + name
        refs.append(path)
    refs.append(old_plan)
    history = read(OLD / 'historical-input-context.json')
    for record in history['originalEvidenceRefs']:
        path = ROOT / record['path']
        expected = plan['after'].get(record['path'], record['sha256'])
        assert digest(path.read_bytes()) == expected, record['path']
        if record['path'] not in MUTABLE_CURRENT:
            refs.append(path)
    refs.append(OLD / 'historical-input-context.json')
    old_config_path = OLD_LOCAL / 'browser-config-390.json'
    old_config, expected = read(old_config_path), dict(config)
    old_config.pop('doc'); expected.pop('doc')
    expected.pop('checkpointInputRefs', None)
    assert old_config == expected, 'Mobile runtime configuration changed'
    report_path = OLD / 'viewport-390/live-browser.json'
    report = committed(report_path)
    assert report['passed'] and not report['errors'] and report['mode'] == 'live'
    own = [r for r in report['views'] if 'time' in r]
    held = report['retainedNativeOwnViews']
    assert len(own) == 12 and len(held) == 138
    source_uids = set(config['browserUids']); retained_uids = set(config['additionalRetainedUids'])
    assert len(source_uids) == 6 and len(retained_uids) == 69
    assert {(r['uid'], r['time']) for r in own} == {(u, t) for u in source_uids for t in ['15:00', '22:00']}
    assert {(r['uid'], r['time']) for r in held} == {(u, t) for u in retained_uids for t in ['15:00', '22:00']}
    root_readback_path = OLD / 'ROOT-MOBILE-RUNTIME-READBACK.json'
    root_readback = committed(root_readback_path)
    assert root_readback['completedLiveMobileReport']['sha256'] == digest(report_path.read_bytes())
    sources = {r['uid']: r for r in root_readback['all75CurrentSourceAssetsRehashed']}
    assert set(sources) == source_uids | retained_uids
    validate_mobile(report, config, sources)
    for entry in sources.values():
        asset = ROOT / entry['asset']; assert digest(asset.read_bytes()) == entry['sha256']; refs.append(asset)
    for row in own + held:
        assert row['active'] and row['visible'] and row['fullyFramed'] and not row['fallbackFaces']
        assert row['sourcePixelVisibility']['visiblePixels'] >= 32
        assert row['sourceSHA256'] == sources[row['uid']]['sha256'] and row['originalTriangles'] == sources[row['uid']]['triangles']
        if row in own: assert row['pick'] == row['collision'] == row['uid'] and row['solidAppearance']
        image = OLD / 'viewport-390' / row['file']
        assert subprocess.check_output(['git', 'show', 'HEAD:' + str(image.relative_to(ROOT))], cwd=ROOT) == image.read_bytes()
        refs.append(image)
    command = read(OLD / 'command-003.json')
    assert command['exitCode'] == 0 and Path(command['command'][1]).name == 'ronsdale_three_live_browser_v20_20261027.mjs'
    assert command['command'][2:] == ['live', str(old_config_path.relative_to(ROOT))]
    atomic_report_path = OLD / 'atomic-live/report.json'
    atomic_report = committed(atomic_report_path); assert verify_atomic(atomic_report)
    old_atomic_config = OLD_LOCAL / 'atomic-live-config.json'
    assert read(old_atomic_config) == atomic_config, 'Atomic lifecycle configuration changed'
    atomic_command = read(OLD / 'command-002.json')
    assert atomic_command['exitCode'] == 0 and Path(atomic_command['command'][1]).name == 'model_atomic_lifecycle_live_browser_v1_20261027.mjs'
    assert atomic_command['command'][2:] == [str(old_atomic_config.relative_to(ROOT)), str((OLD / 'atomic-live').relative_to(ROOT))]
    atomic_images = sorted((OLD / 'atomic-live').glob('*.png')); assert len(atomic_images) == 7
    for image in atomic_images:
        assert subprocess.check_output(['git', 'show', 'HEAD:' + str(image.relative_to(ROOT))], cwd=ROOT) == image.read_bytes()
        refs.append(image)
    shutil.copytree(OLD / 'viewport-390', new_doc / 'viewport-390')
    shutil.copytree(OLD / 'atomic-live', new_doc / 'atomic-live')
    refs += [report_path, root_readback_path, atomic_report_path, OLD / 'command-003.json', old_config_path, old_atomic_config, OLD / 'command-002.json']
    result = dict(uids=sorted(source_uids), reusedCompleteMobileViews=150, reusedCompleteAtomicCases=7,
                  partialDesktopReused=False, executedAgain=False, exactCurrentPublicAndSourceBytesRevalidated=True,
                  exactMobileConfigRevalidated=True, newDesktopSoftwareRequired=True, visualAcceptance=False,
                  installationApproved=False, publication=False, sourceGeometryChanges=0, sourcePoseChanges=0,
                  originalMobileReport=dict(path=str(report_path.relative_to(ROOT)), sha256=digest(report_path.read_bytes())),
                  qualification='Reuse complete passed execution only under exact reapplied public/source/runtime bytes and identical mobile config. Old122partial desktop images have no complete software report and cannot be reused as passing desktop software. New desktop150checks and full actual307export review remain mandatory.')
    out = ROOT / 'docs/astra-city/government-import' / (new_doc.name + '-reused-live-proof')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    receipt = module('june_reused_completed_live_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name, 'exact-unchanged-complete-live-mobile-and-atomic-execution-reuse', list(dict.fromkeys(refs)), result)
    return dict(result, proofJobId=receipt['jobId'], proofReceipt=dict(path=str((out / 'result.json').relative_to(ROOT)), sha256=digest((out / 'result.json').read_bytes())))
