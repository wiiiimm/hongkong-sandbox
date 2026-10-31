"""Trace failed pair rim witnesses to authenticated complete pair intersections.

Exact shared edges and positive finite self-joins within the target source are traversed. A companion contact is
a diagnostic terminal, not an approved support root or architectural decision.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime', 'attributes', 'contacts', 'strict-support', 'uid']:
        parser.add_argument('--' + k, required=True)
    args = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(args.runtime, 'selection.json.gz')
    attributes = take(args.attributes, 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    row = next(r for r in selection['rows'] if r['uid'] == args.uid)
    attr = next(r for r in attributes['rows'] if r['uid'] == args.uid)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=decode_original_world_triangles(asset.read_bytes()))
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix]
    contacts = take(args.contacts, 'summary.json')
    strict = take(args.strict_support, 'summary.json')
    sources = {r['uid']: r['sourceSHA256'] for r in selection['rows']}
    assert contacts['sourceSHA256ByUid'] == sources
    assert strict['supportedUid'] == args.uid
    assert all(sources[u] == h for u, h in strict['sourceSHA256ByUid'].items())
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == pins[args.contacts][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    results = []
    for mode, tri in worlds.items():
        bound = next(r for r in strict['rows'] if r['mode'] == mode)
        assert bound['sourceWorldSHA256ByUid'][args.uid] == digest(tri.tobytes())
        terminals = []
        uids = contacts['uids']
        assert len(uids) == 2 and args.uid in uids
        measured = next(m for m in contacts['rows'] if m['mode'] == mode)
        assert measured['sourceWorldSHA256ByUid'][args.uid] == digest(tri.tobytes())
        raw = take(args.contacts, mode + '.json.gz')
        assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
        for c in raw['contacts']:
            if c['dimension'] <= 0 or c['sourcePrimitiveDimensionA'] != 2 or c['sourcePrimitiveDimensionB'] != 2:
                continue
            terminal = dict(c, peerUid=uids[1] if uids[0] == args.uid else uids[0])
            if uids[1] == args.uid:
                terminal['sourceFaceA'], terminal['sourceFaceB'] = c['sourceFaceB'], c['sourceFaceA']
            terminals.append(terminal)
        lo, hi = tri.min(1), tri.max(1)
        valid = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) > 0
        targets = []
        for witness in bound['support']['unresolved']:
            point = np.asarray(witness['position'])
            candidates = np.flatnonzero(valid & np.all(lo <= point + .001, axis=1) & np.all(hi >= point - .001, axis=1))
            incident = [int(i) for i in candidates if np.linalg.norm(closest(point, tri[i]) - point) <= .001]
            assert incident
            targets.append(dict(witness=witness, incidentFaces=incident))
        self_contacts = exact_finite_contacts(tri, list(range(len(tri))), tri, list(range(len(tri))))
        assert self_contacts['allPairsExamined'] and self_contacts['sourceFacesOmitted'] == 0
        save(out / (mode + '-complete-self-contacts.json.gz'), self_contacts)
        joins = [dict(c, primitiveDimensions=[c['sourcePrimitiveDimensionA'], c['sourcePrimitiveDimensionB']]) for c in self_contacts['contacts'] if c['sourceFaceA'] < c['sourceFaceB'] and c['dimension'] > 0 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2]
        paths = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=terminals)), joins)
        save(out / (mode + '.json.gz'), dict(mode=mode, rows=paths, terminals=terminals))
        results.append(dict(mode=mode, witnesses=len(paths), finiteAttachmentPaths=sum(r['hasUnrestrictedFiniteAttachment'] for r in paths), pathsWithinEndpointHeight=sum(r.get('passesExistingEndpointHeight', False) for r in paths), disconnected=sum(not r['hasUnrestrictedFiniteAttachment'] for r in paths)))
        print(results[-1], flush=True)
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    result = dict(uids=contacts['uids'], targetUid=args.uid, sourceSHA256ByUid=sources, rows=results,
                  sourceGeometryChanges=0, installationApproved=False, physicalAcceptance=False,
                  companionRootsApproved=False, publication=False,
                  qualification='Every saved strict-support warning is retained. Target-only exact shared-original-edge/positive finite self-contact paths terminate at exact positive finite companion intersections. No intercomponent joins, support-root approval, geometric edits, relaxed endpoint ceiling, source-role acceptance or installation permission. Companion foundation/role/failure dependencies remain separate.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_original_finite_triangle_contacts_20261010.py', 'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py', 'original_face_attachment_minimax_v2_20261024.py', 'pool_incident_wall_contacts_v1_20261017.py', 'exact_packed_world_geometry_20261009.py'])
    module('assembly_rim_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'original-assembly-rim-to-finite-companion-attachment-diagnostic', refs, result)


if __name__ == '__main__':
    main()
