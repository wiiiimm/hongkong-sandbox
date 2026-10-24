"""Draw complete original source and current footprint for a bounded identity review."""
import argparse
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'uid']:
        p.add_argument('--' + key, required=True)
    args = p.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    receipt, pins = authenticate(base / args.capture)
    selected = base / args.capture / 'selection.json.gz'
    assert digest(selected.read_bytes()) == pins[str(selected.relative_to(ROOT))]
    row = next(r for r in read(selected)['rows'] if r['uid'] == args.uid)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    form = row['source']['building']
    tile = ROOT / '3d-viewer' / row['source']['tile']
    assert digest(tile.read_bytes()) == row['source']['tileSHA256']
    assert next(b for b in read(tile)['buildings'] if b['uid'] == args.uid) == form
    tri = decode_original_world_triangles(asset.read_bytes())
    assert len(tri) == row['triangles']
    polygon = shapely.Polygon(form['rings'][0], form['rings'][1:])
    polys = shapely.polygons(tri[:, :, [0, 2]])
    projection = shapely.union_all(polys)
    outside = np.array([q.difference(polygon).area > 1e-10 for q in polys])
    centre = tri.mean((0, 1))
    local = tri - centre
    doc.mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(10, 10))
    faces = PolyCollection(local[:, :, [0, 2]], array=tri[:, :, 1].mean(1), cmap='viridis', edgecolors='none')
    ax.add_collection(faces)
    for ring in form['rings']:
        values = np.asarray(ring) - centre[[0, 2]]
        values = np.vstack([values, values[0]])
        ax.plot(values[:, 0], values[:, 1], color='red', linewidth=1.4)
    ax.autoscale_view();ax.set_aspect('equal')
    ax.set(xlabel='Local east (m)', ylabel='Local viewer Z (m)', title=f"{form.get('name', args.uid)} — all original faces; red=current footprint")
    fig.colorbar(faces, ax=ax, label='Original source height HKPD (m)')
    fig.tight_layout();fig.savefig(doc / 'whole-source-plan.png', dpi=130);plt.close(fig)
    fig = plt.figure(figsize=(14, 7))
    for number, azim in enumerate([-125, 55]):
        ax = fig.add_subplot(1, 2, number+1, projection='3d')
        values = local[:, :, [0, 2, 1]]
        colors = np.where(outside[:, None], np.array([[.95, .35, .2, .85]]), np.array([[.6, .7, .8, .6]]))
        ax.add_collection3d(Poly3DCollection(values, facecolors=colors, edgecolor='none'))
        ax.auto_scale_xyz(values[:, :, 0].ravel(), values[:, :, 1].ravel(), values[:, :, 2].ravel())
        ax.set_box_aspect(np.ptp(values.reshape(-1, 3), axis=0));ax.view_init(elev=24, azim=azim)
        ax.set(xlabel='Local east', ylabel='Local Z', zlabel='Local height', title='Orange: complete faces projecting outside current footprint')
    fig.tight_layout();fig.savefig(doc / 'whole-source-perspectives.png', dpi=130);plt.close(fig)
    save(doc / 'summary.json', dict(uids=[args.uid], sourceSHA256=row['sourceSHA256'], completeSourceFaces=len(tri), facesWithNonzeroOutsideProjection=int(outside.sum()), originalWorldSHA256=digest(tri.astype('<f8').tobytes()), sourceProjectionAreaM2=projection.area, outsideProjectionAreaM2=projection.difference(polygon).area, sourceGeometryChanges=0, installationApproved=False, identityApproved=False, qualification='Evidence diagrams only; colours are geometric footprint classification, not component/identity approval.'))
    refs = [Path(__file__), base / args.capture / 'result.json', selected, asset, tile, HERE / 'exact_packed_world_geometry_20261009.py']
    module('identity_plot_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-complete-original-identity-diagrams', refs, read(doc / 'summary.json'))


if __name__ == '__main__':
    main()
