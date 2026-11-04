"""Reconcile existing exact original checks; retain all unresolved physical reasons."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from installed_support_acceptance import resolve_contact

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-pacifica-physical-reconciliation-v1-20261019'
DOC = BASE / BATCH
def folder(name):
    return BASE / ('government-xl-pacifica-' + name + '-20261019')

def main():
    assert not DOC.exists()
    pair = folder('original-assembly-v1')
    ordinary = folder('ordinary-validation-v2')
    foundation = folder('four-mode-foundations-v1')
    binding = folder('wall-binding-v1')
    identities = folder('tower-identity-review-v1')
    podium = folder('podium-identity-review-v1')
    pins, refs = {}, [Path(__file__), HERE / 'installed_support_acceptance.py', HERE / 'acceptance-policy.py']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for d in [pair, ordinary, foundation, binding, identities, podium]:
            receipt = read(d / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(d / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    rows = read(pair / 'selection.json.gz')['rows']
    metrics = read(pair / 'metrics.json')
    validation = read(ordinary / 'validation.json')
    assert validation['loaderAccepted'] == validation['checksPassed'] == len(rows) == 5 and not validation['exceptions']
    supports = {r['uid']: r['proof'] for r in read(pair / 'support.json.gz')['rows']}
    bindings = read(binding / 'exact-source-face-bindings.json.gz')['bindings']
    policy = module('pacifica_reconcile_policy', HERE / 'acceptance-policy.py')
    output = []
    for row in rows:
        uid, key = row['uid'], row['uid'].split('/')[1]
        if key == '283036:0':
            identity = read(podium / (key + '-review.json'))
        elif key in ['79250:0', '77278:0']:
            identity = read(identities / (key + '-review.json'))
        else:
            identity = read(pair / (key + '-identity.json'))
        if 'identityOnlyApproved' in identity:
            assert identity['identityOnlyApproved'] and identity['sourceSHA256'] == row['sourceSHA256']
            proof = identity['identityProof']
        else:
            assert identity['passed'] and identity['sourceSHA256'] == row['sourceSHA256']
            proof = identity['proof']
        metric = next(r for r in metrics['rows'] if r['uid'] == uid)
        raw = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=row['sourceSHA256'], identityProof=proof), metric, metrics['profiles']['mobile'])
        diagnostics = next(r for r in validation['results'] if r['uid'] == uid).get('concerns', [])
        foundations = []
        for mode in ['original', 'literal', 'explicitLeftF32', 'explicitBalancedF32']:
            f = read(foundation / (key + '-' + mode + '.json'))
            b = next(r for r in bindings if (r['uid'], r['mode']) == (uid, mode))
            assert f['wholeWorldSHA256'] == b['wholeWorldSHA256']
            assert f['sourceSHA256'] == b['sourceSHA256'] == row['sourceSHA256']
            assert f['foundation']['triangles'] == f['foundation']['completeTerrainTriangles'] == b['completeFaces'] == row['triangles']
            foundations.append(f)
        all_foundations = all(f['strictFoundationAccepted'] for f in foundations)
        support = supports.get(uid, {})
        # A private assembly check, not a claim that the podium is installed.
        remaining = resolve_contact(raw, support, {'strictFoundationAccepted': all_foundations})
        remaining_diagnostics = resolve_contact(diagnostics, support, {'strictFoundationAccepted': all_foundations})
        output.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], identityAccepted=True,
            rawPolicyReasons=raw, rawDiagnosticReasons=diagnostics,
            remainingPolicyReasons=remaining, remainingDiagnosticReasons=remaining_diagnostics,
            rawStrictSupport=support, allFourFoundationsPassed=all_foundations,
            failedFoundationModes=[f['mode'] for f in foundations if not f['strictFoundationAccepted']],
            supportStatus='private-assembly-only' if support else 'terrain', installationApproved=False))
    native = read(ordinary / 'native-neighbour-checks.json')
    assert not set(native['blocked']) - set(native['resolved'])
    neighbour_rows = []
    for r in read(ordinary / 'neighbour-checks.json')['rows']:
        remaining = [reason for reason in r['reasons'] if not (reason == 'existing-native-neighbour-requires-full-mesh-check' and r['uid'] in native['resolved'])]
        neighbour_rows.append(dict(uid=r['uid'], rawReasons=r['reasons'], remainingReasons=remaining))
    assert not any(r['remainingReasons'] for r in neighbour_rows)
    result = dict(rows=output, neighbours=neighbour_rows, completeLoaderChecksPassed=True,
        completeNeighbourChecksPassed=True, sourceGeometryChanges=0, installationApproved=False,
        qualification='Existing strict resolver only. Raw failures retained. Private assembly dependency must be installed together; final viewer and publication gates remain required.')
    save(DOC / 'physical-reconciliation.json', result)
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    summary = dict(uids=[r['uid'] for r in output], rows=[{k: r[k] for k in ['uid', 'remainingPolicyReasons', 'remainingDiagnosticReasons', 'failedFoundationModes']} for r in output], installationApproved=False)
    module('pacifica_physical_reconcile_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'five-original-existing-policy-physical-reconciliation', list(dict.fromkeys(refs)), summary)
    print(summary, flush=True)

if __name__ == '__main__':
    main()
