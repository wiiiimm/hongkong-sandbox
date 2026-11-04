"""Compare the new footing interface with the unchanged pre-existing BASIC body.

Diagnostic views and exact foreign-surface clips only; no placement acceptance.
"""
import argparse
import sys
import uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_footing_prism_contacts_v1_20261028 import surface_contacts
from elegant_basic_footing_foreign_volume_v1_20261028 import BASE, PREFIX, PROPOSAL, RUNTIME, ATTRS

CONTEXT = PREFIX+'basic-footing-foreign-volume-v1-20261028'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith(PREFIX) and '/' not in a.batch
    out, local = BASE/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    lp = local/'reservation.json'
    resources = ['building:landsd/213586:0', 'building:landsd/215726:0']
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('basic-footing-interface-'+str(uuid.uuid4()), resources, batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(resources) <= set(lease['resources'])
    refs, pins = [Path(__file__), HERE/'exact_footing_prism_contacts_v1_20261028.py'], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    summary = take(CONTEXT, 'summary.json')
    selection = take(RUNTIME, 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == 'landsd/215726:0')
    attrs = next(r for r in take(ATTRS, 'attributes.json.gz')['rows'] if r['uid'] == row['uid'])
    asset = ROOT/row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == attrs['sourceSHA256']
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    geometry = take(PROPOSAL, 'geometry.json.gz')
    before = geometry['before']
    body = np.asarray(before['position']).reshape(-1, 3)[np.asarray(before['index']).reshape(-1, 3)]
    after = geometry['after']
    added = np.asarray(after['position']).reshape(-1, 3)[np.asarray(after['index']).reshape(-1, 3)][len(body):]
    top, bottom = body[:, :, 1].max(), body[:, :, 1].min()
    caps = body[(body[:, :, 1] == top).all(1)]
    index = np.asarray(attrs['completeOriginalIndex']).reshape(-1, 3)
    modes = dict(original=tri)
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        modes[mode] = np.asarray(attrs[field]).reshape(-1, 3)[index]
    rows = []
    original_contacts = None
    for mode, foreign in modes.items():
        old = surface_contacts(foreign, caps, bottom, top)
        new = take(CONTEXT, '215726:0--candidate-original--'+mode+'.json.gz')
        assert next(r for r in summary['rows'] if r['uid'] == row['uid'] and r['mode'] == mode and r['role'] == 'candidate-original')['worldSHA256'] == digest(foreign.astype('<f8').tobytes())
        old_ids = sorted({r['sourceFace'] for r in old['contacts']})
        new_ids = sorted({r['sourceFace'] for r in new['contacts']})
        save(out/(mode+'-existing-body.json.gz'), old)
        rows.append(dict(mode=mode, existingBodyContactFaces=old_ids, addedFootingContactFaces=new_ids,
                         newContactFaceIdsAbsentFromExistingBody=sorted(set(new_ids)-set(old_ids)),
                         completeSourceFaces=len(foreign), sourceWorldSHA256=digest(foreign.astype('<f8').tobytes())))
        if mode == 'original':
            original_contacts = new['contacts']
    lo = np.minimum(body.min((0, 1)), tri.min((0, 1)))
    hi = np.maximum(body.max((0, 1)), tri.max((0, 1)))
    lo[1] = min(lo[1], added[:, :, 1].min())
    span = hi-lo
    fig = plt.figure(figsize=(16, 12), dpi=150)
    for n, (azimuth, include_footing) in enumerate([(-55, False), (-55, True), (125, False), (125, True)]):
        ax = fig.add_subplot(2, 2, n+1, projection='3d')
        xyz = lambda t: t[:, :, [0, 2, 1]]
        ax.add_collection3d(Poly3DCollection(xyz(tri), facecolors='#4099de', edgecolors='#1a6094', linewidths=.3, alpha=.25))
        ax.add_collection3d(Poly3DCollection(xyz(body), facecolors='#999999', edgecolors='#333333', linewidths=.4, alpha=.32))
        if include_footing:
            ax.add_collection3d(Poly3DCollection(xyz(added), facecolors='#e6a345', edgecolors='#9c5800', linewidths=.6, alpha=.6))
            for contact in original_contacts:
                points = np.array([[float(Fraction(v)) for v in p] for p in contact['exactClippedPoints']])
                ax.add_collection3d(Poly3DCollection([points[:, [0, 2, 1]]], facecolors='#e63d26', edgecolors='#a60000', alpha=.85))
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[2], hi[2]), zlim=(lo[1], hi[1]), xlabel='world X (m)', ylabel='world Z (m)', zlabel='HKPD elevation (m)')
        ax.set_box_aspect(span[[0, 2, 1]])
        ax.view_init(elev=22, azim=azimuth)
        ax.set_title('Existing BASIC body' if not include_footing else 'Body + proposed footing; contact polygons red')
    fig.suptitle('West Grand original podium (blue) and BASIC 213586 (grey)\nComplete meshes; two views before/after. Diagnostic only; placement/collision approval remains pending.')
    fig.tight_layout(rect=(0, 0, 1, .95))
    image = out/'west-grand-basic-footing-interface-2400x1800.png'
    image.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(image)
    plt.close(fig)
    refs.append(image)
    result = dict(uids=['landsd/213586:0', row['uid']], rows=rows,
                  image=dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes())),
                  sourceGeometryChanges=0, governmentGeometryChanges=0, collisionReviewApproved=False,
                  physicalAccepted=False, visualReviewApproved=False, installationApproved=False,
                  qualification='The new footing contact facets are compared against the complete unchanged pre-existing BASIC body volume in every captured coordinate stream. Shared facet IDs do not prove the extended interface safe, below grade, intentionally owned or visually acceptable. Complete original and BASIC meshes are drawn from two perspectives before/after; render completion alone grants no review approval.')
    save(out/'summary.json', result)
    assert reservations.owns(lease)
    module('basic_footing_interface_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-basic-footing-vs-existing-body-source-interface-context', list(dict.fromkeys(refs)), result)
    print(rows, flush=True)


if __name__ == '__main__':
    main()
