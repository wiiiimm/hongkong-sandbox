"""Capture current parent-domain failures with all crossing terrain faces retained."""
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--failures', required=True)
    args = parser.parse_args()
    assert all(x.startswith('government-xl-') and '/' not in x for x in [args.batch, args.failures])
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    _, pins = authenticate(base / args.failures)
    path = base / args.failures / 'summary.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    failures = read(path)['rows']
    assert 0 < len(failures) <= 40
    rows = [dict(uid=r['uid'], bounds=r['bounds']) for r in failures]
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = digest(manifest.read_bytes())
    save(doc / 'input.json', dict(rows=rows, manifestSHA256=before, historicalFailureContext=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))))
    tool = HERE / 'selected_parent_domain_diagnostics_v1.mjs'
    output = local / 'geometry.json.gz'
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str((doc / 'input.json').relative_to(ROOT)), str(output.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    captured = read(output)
    assert digest(manifest.read_bytes()) == before
    refs = [Path(__file__), tool, base / args.failures / 'result.json', path, output]
    for name, sha in captured['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    assert {r['uid'] for r in captured['rows']} == {r['uid'] for r in rows}
    result = []
    for row in captured['rows']:
        triangles = np.asarray(row['faces'])
        assert len(triangles)
        polygons = shapely.polygons(triangles[:, :, [0, 2]])
        extent = shapely.box(*row['bounds'])
        union = shapely.union_all(polygons).intersection(extent)
        missing = extent.difference(union)
        result.append(dict(uid=row['uid'], bounds=row['bounds'], completeIntersectingFaces=len(triangles), insideFaces=row['insideFaces'], crossingFaces=len(row['crossingFaces']), missingProjectedAreaM2=float(missing.area), installationApproved=False, permanentRejection=False))
        save(doc / (row['uid'].split('/')[1] + '-missing.geojson'), json.loads(shapely.to_geojson(missing)))
    summary = dict(uids=[r['uid'] for r in result], rows=result, manifestSHA256=before,
                   installationApproved=False, newlyInstalled=0, sourceGeometryChanges=0,
                   scriptExternalAICalls=0, qualification='Current actual drawn terrain captured without discarding crossing triangles. Projection clipping is diagnostic only; no terrain or model assets are constructed or published.')
    save(doc / 'summary.json', summary)
    module('parent_domain_diagnostic_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-current-parent-domain-diagnostics', refs, summary)
    print(result, flush=True)


if __name__ == '__main__':
    main()
