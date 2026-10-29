"""Bind exact unchanged low-facet lineage to the private depot construction."""
from pathlib import Path
import subprocess
import sys
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from unchanged_low_parent_lineage_v1_20261029 import qualify


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-depot120104-exact-low-lineage-v1-20261029'
    construction = 'government-xl-depot120104-land-inset-construction-v3-20261029'
    parent = 'government-xl-depot120104-terrain-sequence-v1-20261029-120104-0-inset'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(base / name)[1]
            refs.append(base / name / 'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    before = take(parent, HERE / 'local' / parent / 'parent.json')
    for name, sha in before['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    summary = take(construction, base / construction / 'summary.json')
    after = take(construction, HERE / 'local' / construction / 'global-triangles.json.gz')
    lineage = take(construction, base / construction / 'global-lineage.json.gz')
    proof = qualify(before['triangles'], after['triangles'], lineage)
    assert proof['unchangedLowParentFaces'] == 14
    out.mkdir()
    with (out / 'tests.log').open('w') as log:
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE), '-p', 'test_unchanged_low_parent_lineage_v1_20261029.py'], stdout=log, stderr=subprocess.STDOUT, check=True, cwd=ROOT)
    result = dict(uids=['landsd/120104:0'], sourceSHA256=summary['sourceSHA256'], proof=proof,
                  conservativeEnvelopePrecheckPassed=False,
                  exactActualLowFacetPreservationPassed=True,
                  installationApproved=False, publication=False,
                  qualification='All14 complete original low parent facets are retained at identical original and Float32 coordinates, winding and multiplicity, with unchanged parent lineage exactly once. No low parent is edited and every new fragment remains above1.2m. Eight guard mutation tests pass. This resolves the actual low-facet preservation question without pretending the nominal-envelope precheck passed; canonical patch, renderer, neighbours and browser acceptance remain separate.')
    save(out / 'summary.json', result)
    refs.extend(HERE / name for name in ['unchanged_low_parent_lineage_v1_20261029.py', 'unchanged_low_parent_faces_v1_20261024.py', 'test_unchanged_low_parent_lineage_v1_20261029.py'])
    module('depot_exact_low_lineage_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'complete-original-low-parent-facet-preservation-with-lineage', refs, result)


if __name__ == '__main__':
    main()
