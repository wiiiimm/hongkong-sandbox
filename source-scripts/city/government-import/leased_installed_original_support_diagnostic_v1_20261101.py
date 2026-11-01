"""Own the complete nominated actor scope while the existing support diagnostic runs."""
import argparse, subprocess, sys, uuid
from run import ROOT, HERE, read, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

def main():
    p = argparse.ArgumentParser(description=__doc__)
    fields = ['batch', 'scope', 'runtime', 'attributes', 'inventory', 'native-contacts', 'historical-attributes', 'uid', 'support']
    for f in fields: p.add_argument('--' + f, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    _, pins = authenticate(base / a.scope)
    f = base / a.scope / 'summary.json'
    assert digest(f.read_bytes()) == pins[str(f.relative_to(ROOT))]
    scope = read(f)
    assert scope['uids'] == [a.uid]
    nominated = {r['uid'] for r in scope['rows'][0]['nearbyNativeActors']}
    assert a.support in nominated
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == scope['currentManifestSHA256']
    resources = ['building:' + u for u in sorted(nominated | {a.uid})] + ['immutable-source-proof:' + a.batch]
    control = HERE / 'local' / (a.batch + '-lease')
    leasefile = control / 'reservation.json'
    if not a.owned:
        assert not control.exists() and not (base / a.batch).exists()
        claim = reservations.claim('original-installed-support-' + str(uuid.uuid4()), resources, batch=a.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], leasefile, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasefile)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    command = [sys.executable, str(HERE / 'proposed_original_installed_support_diagnostic_v1_20261024.py')]
    for f in fields:
        if f != 'scope': command.extend(['--' + f, getattr(a, f.replace('-', '_'))])
    subprocess.run(command, cwd=ROOT, check=True)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == scope['currentManifestSHA256']

if __name__ == '__main__': main()
