"""Find source assembly blockers before costly terrain/browser work; no approval."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICY = ROOT / 'source-scripts/city/island-detail-integration/model_dependencies.py'
spec = importlib.util.spec_from_file_location('preflight_dependency_policy', POLICY)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def inspect_dependencies(installed, candidates):
    """Reuse publisher dependency-state semantics, retaining exact affected UIDs."""
    def keyed(models):
        result = {}
        for model in models:
            if model['uid'] in result:
                raise ValueError('Duplicate source UID: ' + model['uid'])
            policy.dependency_rows(model)  # Reject unknown states, as the publisher does.
            result[model['uid']] = model
        return result

    current, proposed = keyed(installed), keyed(candidates)
    combined = {**current, **proposed}
    fallback_users = {}
    for uid, model in combined.items():
        for support, kind in policy.dependency_rows(model):
            if kind == 'fallback':
                fallback_users.setdefault(support, set()).add(uid)
    rows = []
    for uid, model in sorted(proposed.items()):
        blockers = []
        dependents = sorted(fallback_users.get(uid, set()))
        if dependents:
            blockers.append({'reason': 'fallback-dependency-migration-required',
                             'affectedUids': dependents})
        closure, missing, cycles, active = set(), set(), set(), []
        done = set()

        def visit(node):
            if node in active:
                cycles.add(tuple(active[active.index(node):] + [node]))
                return
            if node in done:
                return
            if node not in combined:
                missing.add(node)
                return
            active.append(node)
            for support, kind in policy.dependency_rows(combined[node]):
                if kind == 'native':
                    closure.add(support)
                    visit(support)
                elif support in proposed:
                    blockers.append({'reason': 'native-candidate-conflicts-with-fallback-support',
                                     'dependentUid': node, 'supportUid': support})
            active.pop()
            done.add(node)

        visit(uid)
        if missing:
            blockers.append({'reason': 'missing-native-support', 'affectedUids': sorted(missing)})
        if cycles:
            blockers.append({'reason': 'cyclic-native-support',
                             'cycles': [list(c) for c in sorted(cycles)]})
        rows.append({'uid': uid, 'sourceSHA256': model.get('sha256'),
                     'nativeSupportClosure': sorted(closure),
                     'fallbackDependents': dependents, 'blockers': blockers,
                     'requiresAssemblyInvestigation': bool(blockers),
                     'installationApproved': False})
    return {'policy': 'source-dependency-preflight-v1', 'rows': rows,
            'candidateCount': len(rows),
            'requiresAssemblyInvestigation': sum(r['requiresAssemblyInvestigation'] for r in rows),
            'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
            'qualification': 'Metadata-only early routing. Passing grants no source, terrain, runtime or publication approval; reviewed migrations and all publisher guards still apply.'}


def from_catalogues(manifest_path, candidate_paths):
    manifest_path = Path(manifest_path).resolve()
    viewer = manifest_path.parents[2]
    inputs = {}

    def read(path):
        path = Path(path).resolve()
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_bytes())

    manifest = read(manifest_path)
    installed = [m for url in manifest['officialModelCatalogues']
                 for m in read(viewer / url)['models']]
    candidates = [m for path in candidate_paths for m in read(path)['models']]
    report = inspect_dependencies(installed, candidates)
    for path in (Path(__file__), POLICY):
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {**report, 'inputHashes': inputs}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / '3d-viewer/city/data/manifest.json')
    parser.add_argument('--catalogue', action='append', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = from_catalogues(args.manifest, args.catalogue)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('candidateCount', 'requiresAssemblyInvestigation', 'publication')}))
