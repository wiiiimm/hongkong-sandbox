"""Reproduce one selected original's exact sampler failures from an authenticated capture."""
import argparse
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'uid']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / args.batch, base / args.capture
    assert not doc.exists()
    _, pins = authenticate(cap)
    runtimepath = HERE / 'local' / cap.name / 'runtime-geometry.json.gz'
    metricspath = cap / 'metrics.json'
    refs = [Path(__file__), cap / 'result.json', runtimepath, metricspath]
    for path in [runtimepath, metricspath]:
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    matches = [r for r in read(runtimepath)['rows'] if r['uid'] == args.uid]
    assert len(matches) == 1
    save(doc / 'selected-runtime.json.gz', dict(rows=matches))
    tool = HERE / 'china_merchants_actual_samples_v1_20261021.mjs'
    subprocess.run(['node', str(tool), str(doc / 'selected-runtime.json.gz'), str(doc / 'samples.json')], cwd=ROOT, check=True)
    result = read(doc / 'samples.json')
    metric = next(r for r in read(metricspath)['rows'] if r['uid'] == args.uid)
    assert result['checks'] == metric['checks'] and result['missing'] == metric['missingTerrain']
    assert abs(result['minGap'] - metric['minSurfaceGap']) < 1e-12
    summary = dict(uids=[args.uid], sourceSHA256=result['sourceSHA256'], checks=result['checks'], missing=result['missing'], minimumGapM=result['minGap'], failedSamples=len(result['rows']), sourceGeometryChanges=0, installationApproved=False, scriptExternalAICalls=0)
    refs.extend([tool, ROOT / '3d-viewer/city/native-terrain.js', ROOT / '3d-viewer/city/exact-finite-triangle-projection.js'])
    module('selected_sample_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-exact-actual-renderer-sample-residuals', refs, summary)
    print(summary, flush=True)


if __name__ == '__main__':
    main()
