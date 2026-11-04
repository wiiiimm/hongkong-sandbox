"""Bind complete actual renderer arrays to an explicit authenticated source capture."""
import argparse
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--capture', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / args.batch, base / args.capture
    assert not doc.exists()
    _, pins = authenticate(cap)
    selectionpath = cap / 'selection.json.gz'
    assert digest(selectionpath.read_bytes()) == pins[str(selectionpath.relative_to(ROOT))]
    selection = read(selectionpath)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']

    def ref(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

    rows = selection['rows']
    assert 0 < len(rows) <= 40
    expected = {}
    for row in rows:
        entry = row['candidate']['entry']
        assert entry['sha256'] == row['sourceSHA256']
        assert entry['triangles'] == row['native']['model']['triangles'] == row['triangles']
        assert digest((ROOT / row['candidate']['path']).read_bytes()) == row['sourceSHA256']
        expected[row['uid']] = [row['sourceSHA256'], row['triangles']]
    save(doc / 'input.json.gz', dict(currentManifest=ref(manifest), currentCatalogueRefs=[ref(ROOT / '3d-viewer' / url) for url in read(manifest)['officialModelCatalogues']], evidenceRefs=[ref(selectionpath)], expectedSourceByUid=expected, rows=[dict(uid=r['uid'], entry=r['candidate']['entry'], building=r['source']['building'], path=r['candidate']['path']) for r in rows]))
    tool = HERE / 'selected_original_render_attributes_v1.mjs'
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str((doc / 'input.json.gz').relative_to(ROOT)), str((doc / 'attributes.json.gz').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    output = read(doc / 'attributes.json.gz')
    assert output['startEndAllInputsVerified']
    assert {r['uid']: r['sourceSHA256'] for r in output['rows']} == {uid: item[0] for uid, item in expected.items()}
    refs = [Path(__file__), tool, cap / 'result.json', selectionpath]
    for path, sha in output['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    result = dict(uids=sorted(expected), completeFaces=sum(item[1] for item in expected.values()), installationApproved=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    module('selected_attribute_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-original-complete-loader-attributes', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
