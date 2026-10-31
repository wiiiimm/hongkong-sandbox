"""Run existing original support-interface checks for explicit assembly edges."""
import argparse
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    p.add_argument('--pair', action='append', required=True, help='sourceUid,supportUid')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    _, pins = authenticate(base / a.capture)
    selection = base / a.capture / 'selection.json.gz'
    assert digest(selection.read_bytes()) == pins[str(selection.relative_to(ROOT))]
    sources = read(selection)['rows']
    uids = {r['uid'] for r in sources}
    pairs = [dict(zip(['uid', 'supportUid'], s.split(','))) for s in a.pair]
    assert len({(r['uid'], r['supportUid']) for r in pairs}) == len(pairs)
    assert all(set(r) == {'uid', 'supportUid'} and r['uid'] in uids and r['supportUid'] in uids and r['uid'] != r['supportUid'] for r in pairs)
    refs = [Path(__file__), base / a.capture / 'result.json', selection]
    for row in sources:
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256'] == row['candidate']['entry']['sha256']
        refs.append(path)
    save(doc / 'support-inputs.json', dict(sources=sources, pairs=pairs))
    tool = HERE / 'original-support-closure-interfaces.mjs'
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(doc.relative_to(ROOT)) + '/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(doc / 'support-checks.json.gz')
    assert [(r['uid'], r['supportUid']) for r in report['rows']] == [(r['uid'], r['supportUid']) for r in pairs]
    for path, sha in report['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    rows = [dict(uid=r['uid'], supportUid=r['supportUid'],
                 **{k: r['interface'][k] for k in ['passed', 'samples', 'strictContacts', 'wallIntersections']},
                 unresolvedSamples=len(r['interface']['unresolved'])) for r in report['rows']]
    result = dict(uids=sorted(uids), rows=rows, sourceGeometryChanges=0,
                  installationApproved=False, physicalSupportAccepted=False,
                  qualification='Canonical original-support interface probes only. All unresolved samples retained. No identity, full-facet collision, foundation, neighbour, device, visual or publication acceptance.')
    save(doc / 'summary.json', result)
    refs += [tool, HERE / 'support-interface.mjs', HERE / 'source-face-query.mjs']
    module('assembly_support_diagnostic_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'explicit-original-assembly-support-interfaces', refs, result)
    print(rows, flush=True)


if __name__ == '__main__':
    main()
