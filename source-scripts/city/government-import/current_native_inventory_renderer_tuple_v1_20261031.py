"""Add an explicit current controller-source tuple to an unchanged bounds proof.

The bounds exporter loads official-model-assets.js, not official-models.js.
This audit does not claim that the controller was executed by that exporter.
"""
import argparse
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'inventory', 'runtime']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--lease')
    args = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n
               for n in [args.batch, args.inventory, args.runtime])
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / args.batch, HERE / 'local' / args.batch
    assert not out.exists()
    resource = 'immutable-source-proof:' + args.batch
    if not args.lease:
        assert not local.exists()
        claim = reservations.claim('current-renderer-tuple-' + str(uuid.uuid4()),
                                   [resource], batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], local / 'reservation.json',
                                [sys.executable, __file__, *sys.argv[1:],
                                 '--lease', str(local / 'reservation.json')])
    lease = read(Path(args.lease))
    assert reservations.owns(lease) and resource in lease['resources']
    inventory, pins = authenticate(base / args.inventory)
    _, prior = authenticate(base / args.runtime)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[str(manifest.relative_to(ROOT))]
    assert inventory['completeNativeActors'] > 0 and inventory['freshEveryActorActualLoad']
    bounds = base / args.inventory / 'complete-bounds.json.gz'
    assert digest(bounds.read_bytes()) == pins[str(bounds.relative_to(ROOT))]
    tuples, modules = [], []
    for name in ['official-models.js', 'official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / name
        relative, sha = str(path.relative_to(ROOT)), digest(path.read_bytes())
        assert sha == prior[relative], 'Historical source/coordinate contract changed'
        if relative in pins:
            assert sha == pins[relative]
        tuples.append(dict(path=relative, sha256=sha,
                           presentInActorBoundsReceipt=relative in pins,
                           unchangedFromHistoricalRuntime=True))
        modules.append(path)
    # Recheck every original bound reference; never re-sign stale public bytes.
    refs = [ROOT / r['path'] for r in inventory['evidenceRefs']]
    for binding, path in zip(inventory['evidenceRefs'], refs):
        assert digest(path.read_bytes()) == binding['sha256'], binding['path']
    out.mkdir()
    target = out / 'complete-bounds.json.gz'
    target.write_bytes(bounds.read_bytes())
    assert digest(target.read_bytes()) == digest(bounds.read_bytes())
    assert reservations.owns(lease)
    result = dict(uids=[], completeNativeActors=inventory['completeNativeActors'],
                  freshEveryActorActualLoad=True, originalBoundsJobId=inventory['jobId'],
                  boundsBytesUnchanged=True, rendererSourceTuple=tuples,
                  controllerExecutedByBoundsExporter=False, installationApproved=False,
                  physicalAcceptance=False, newlyInstalled=0, sourceGeometryChanges=0,
                  qualification='Original complete actual-actor bounds retained byte-for-byte. Fresh controller source hash equals the authenticated historical runtime; asset-loader and geo hashes also equal current bounds inputs. Controller source binding is additional provenance, not a claim of execution, source-role acceptance or scene approval.')
    save(out / 'summary.json', result)
    refs.extend([Path(__file__), target, manifest, *modules,
                 base / args.inventory / 'result.json', base / args.runtime / 'result.json'])
    module('current_inventory_renderer_tuple_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'unchanged-current-actor-bounds-with-explicit-renderer-source-tuple',
        list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
