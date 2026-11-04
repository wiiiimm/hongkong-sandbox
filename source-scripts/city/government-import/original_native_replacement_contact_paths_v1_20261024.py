"""Trace saved native replacement probes without changing strict support results.

Consumes only authenticated completed four-world support measurements. This is
source-contact evidence; it cannot update dependencies or approve installation.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from source_closed_components import components
from original_four_world_contact_paths_v1_20261023 import paths


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--support-checks', required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.support_checks])
    base = ROOT / 'docs/astra-city/government-import'
    out, prior = base / a.batch, base / a.support_checks
    assert not out.exists()
    receipt, pins = authenticate(prior)
    refs = [Path(__file__), prior / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    checks = take(prior / 'summary.json')
    assert checks['sourceGeometryChanges'] == checks['dependencyMetadataChanges'] == 0
    assert not checks['installationApproved'] and not checks['publication']
    assert set(r['mode'] for r in checks['rows']) == {'original', 'literal', 'leftF32', 'balancedF32'}
    uid, support_uid = checks['supportedUid'], checks['supportUid']
    rows = []
    for check in checks['rows']:
        mode = check['mode']
        folder = prior / mode / 'proposedOriginal'
        data = take(folder / 'input.json.gz')
        measured = take(folder / 'support.json.gz')
        assert len(data['rows']) == len(measured['rows']) == 1
        source, measurement = data['rows'][0], measured['rows'][0]
        assert source['uid'] == measurement['uid'] == uid
        proof = check['reports']['proposedOriginal']
        assert measurement['proof'] == proof
        for key, sha in measured['inputHashes'].items():
            assert digest((ROOT / key).read_bytes()) == sha == pins[key]
            refs.append(ROOT / key)
        tri = np.asarray(source['position'], dtype='<f8').reshape(-1, 3)[np.asarray(source['index']).reshape(-1, 3)]
        support = np.asarray(data['podium'], dtype='<f8')
        assert np.isfinite(tri).all() and np.isfinite(support).all()
        low, high = tri.min(1), tri.max(1)
        targets = []
        for witness in proof['unresolved']:
            point = np.asarray(witness['position'])
            candidates = np.flatnonzero(np.all(low <= point + .001, axis=1) & np.all(high >= point - .001, axis=1))
            incident = [int(i) for i in candidates if np.linalg.norm(np.cross(tri[i, 1] - tri[i, 0], tri[i, 2] - tri[i, 0])) > 0 and np.linalg.norm(closest(point, tri[i]) - point) <= .001]
            assert incident
            targets.append(dict(witness=witness, incidentFaces=incident))
        incident = {i for target in targets for i in target['incidentFaces']}
        reached = sorted({i for component in components(tri)['components'] if incident.intersection(component['faceIndices']) for i in component['faceIndices']})
        contacts = exact_finite_contacts(tri, reached, support, list(range(len(support)))) if reached else dict(contacts=[])
        if reached:
            assert contacts['allPairsExamined']
        verified = paths(tri, dict(targets=targets, proof=contacts))
        row = dict(mode=mode, targets=len(targets), verifiedPaths=sum(r['verifiedPath'] is not None for r in verified), remaining=sum(r['verifiedPath'] is None for r in verified), strictInterfacePassed=proof['passed'], sourceWorldSHA256=digest(tri.tobytes()), supportWorldSHA256=digest(support.tobytes()))
        save(out / (mode + '.json.gz'), dict(**row, rows=verified, exactContacts=contacts))
        rows.append(row)
        print(row, flush=True)
    result = dict(uids=[uid, support_uid], rows=rows, authenticatedSupportJobId=receipt['jobId'], allUnresolvedHaveFinitePaths=all(r['remaining'] == 0 for r in rows), sourceGeometryChanges=0, dependencyMetadataChanges=0, installationApproved=False, publication=False, qualification='Every saved unresolved probe retained. Exact original surface paths with positive-dimensional contact endpoints use unchanged endpoint height ceilings and residual limits. Strict failures remain. Historical source-contact evidence only; current scene, foundation, source role, dependency replacement and browser approval are separate.')
    save(out / 'summary.json', result)
    refs += [HERE / n for n in ['original_four_world_contact_paths_v1_20261023.py', 'pool_incident_wall_contacts_v1_20261017.py', 'exact_original_finite_triangle_contacts_20261010.py', 'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py', 'source_closed_components.py']]
    module('native_replacement_contact_paths_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'four-world-native-original-replacement-finite-contact-paths', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
