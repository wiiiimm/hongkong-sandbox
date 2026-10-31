"""Test exact low-height joins within an unchanged source, without support approval."""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_face_attachment_minimax_v2_20261024 import attachment_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime', 'attributes', 'attachments', 'uid']:
        parser.add_argument('--' + k, required=True)
    args = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(args.runtime, 'selection.json.gz')
    attributes = take(args.attributes, 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    source = next(r for r in selection['rows'] if r['uid'] == args.uid)
    attr = next(r for r in attributes['rows'] if r['uid'] == args.uid)
    previous = take(args.attachments, 'summary.json')
    assert previous['targetUid'] == args.uid
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == previous['sourceSHA256ByUid'][args.uid]
    refs.append(asset)
    index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=decode_original_world_triangles(asset.read_bytes()))
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    summaries = []
    for mode, tri in worlds.items():
        old = take(args.attachments, mode + '.json.gz')
        targets = [dict(witness=r['witness'], incidentFaces=r['incidentFaces']) for r in old['rows']]
        report = dict(targets=targets, proof=dict(contacts=old['terminals']))
        assert attachment_paths(tri, report, []) == old['rows']
        assert targets and all(r['hasUnrestrictedFiniteAttachment'] for r in old['rows'])
        ceiling = max(r['endpointHeightCeilingM'] for r in old['rows'])
        eligible = np.flatnonzero(tri[:, :, 1].min(1) <= ceiling).tolist()
        print(dict(mode=mode, eligibleFaces=len(eligible), completeFaces=len(tri), ceiling=ceiling), flush=True)
        proof = exact_finite_contacts(tri, eligible, tri, eligible)
        assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
        save(out / (mode + '-self-contacts.json.gz'), proof)
        joins = [dict(c, primitiveDimensions=[2, 2]) for c in proof['contacts']
                 if c['sourceFaceA'] < c['sourceFaceB'] and c['dimension'] > 0
                 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2
                 and min(Fraction(p[1]) for p in c['exactPoints']) <= Fraction(float(ceiling))]
        paths = attachment_paths(tri, report, joins)
        save(out / (mode + '-paths.json.gz'), dict(rows=paths, joins=joins, diagnosticCeilingM=ceiling))
        summaries.append(dict(mode=mode, eligibleFaces=len(eligible), completeFaces=len(tri), diagnosticCeilingM=ceiling,
                              finiteSelfJoins=len(joins), witnesses=len(paths),
                              finiteAttachmentPaths=sum(r['hasUnrestrictedFiniteAttachment'] for r in paths),
                              pathsWithinEndpointHeight=sum(r.get('passesExistingEndpointHeight', False) for r in paths)))
        print(summaries[-1], flush=True)
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    result = dict(uids=[args.uid], sourceSHA256=source['sourceSHA256'], rows=summaries,
                  sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False,
                  installationApproved=False, publication=False,
                  qualification='Reproduces every prior shared-edge-only path, then adds exact positive finite joins within the same unchanged original asset below the maximum prior endpoint height. All eligible faces and their pair contacts retained; no epsilon bridging, geometry edit, height-limit waiver, companion root or architectural approval. This is a bounded low-height connectivity test, not a complete internal collision census.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'exact_original_finite_triangle_contacts_20261010.py', 'original_face_attachment_minimax_v2_20261024.py'])
    module('low_rim_self_join_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'exact-low-rim-original-self-join-attachment-diagnostic', refs, result)


if __name__ == '__main__':
    main()
