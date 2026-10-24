"""Draw every saved exact Nam Cheong foreign crossing against current actors.

Plotting context only, no geometry edits or acceptance from contact appearance.
"""
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH = 'government-xl-nam-cheong-foreign-crossing-views-v1-20261023'
CAP = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
GEO = 'government-xl-nam-cheong-foreign-geometry-v1-20261023'
ROLES = 'government-xl-nam-cheong-foreign-contact-roles-v1-20261023'
SCOPE = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-scope'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [CAP, GEO, ROLES, SCOPE]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, path):
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = next(r for r in take(CAP, base / CAP / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/268867:0')
    asset = ROOT / selected['candidate']['path']
    assert digest(asset.read_bytes()) == selected['sourceSHA256']
    refs.append(asset)
    source = decode_original_world_triangles(asset.read_bytes())
    oldnative = take(GEO, base / GEO / 'native-input.json.gz')['rows'][0]
    oldbasic = take(GEO, base / GEO / 'basic-input.json.gz')['rows'][0]
    forms = {r['uid']: r for r in take(SCOPE, base / SCOPE / 'form-obligations.json.gz')}
    assert forms[oldnative['uid']] == oldnative['building']
    assert forms[oldbasic['uid']] == oldbasic
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == read(base / CAP / 'selection.json.gz')['manifestSHA256']
    refs.append(manifestpath)
    found = []
    for url in read(manifestpath)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        for entry in read(path)['models']:
            if entry['uid'] == oldnative['uid']:
                found.append((path, entry))
    assert len(found) == 1 and found[0][1] == oldnative['entry']
    refs.append(found[0][0])
    nativeasset = ROOT / oldnative['path']
    assert digest(nativeasset.read_bytes()) == oldnative['entry']['sha256']
    refs.append(nativeasset)
    native = decode_original_world_triangles(nativeasset.read_bytes())
    basicattrs = take(GEO, base / GEO / 'basic-attributes.json.gz')
    assert basicattrs['startEndAllInputsVerified']
    for path, sha in basicattrs['inputHashes'].items():
        if Path(path).suffix in ['.js', '.mjs']:
            assert digest((ROOT / path).read_bytes()) == sha
            refs.append(ROOT / path)
    basic = basicattrs['rows'][0]
    basicfaces = np.concatenate([np.asarray(m['position']).reshape(-1, 3)[np.asarray(m['index']).reshape(-1, 3)] for m in basic['meshes']])
    rows = []
    for uid, foreign in [('landsd/262871:0', native), ('landsd/233291:0', basicfaces)]:
        contacts = take(ROLES, base / ROLES / (uid.split('/')[1] + '.json.gz'))
        assert contacts and all(c['contactRole'] == 'transverse-surface-crossing' for c in contacts)
        points = np.asarray([[float(Fraction(v)) for v in point] for c in contacts for point in c['exactPoints']])
        sourceids = sorted({c['sourceFaceA'] for c in contacts})
        foreignids = sorted({c['sourceFaceB'] for c in contacts})
        lo, hi = points.min(0) - 4, points.max(0) + 4
        def localids(tri):
            return np.flatnonzero(np.all(tri.max(1) >= lo, axis=1) & np.all(tri.min(1) <= hi, axis=1))
        a, b = localids(source), localids(foreign)
        center = (lo + hi) / 2
        fig = plt.figure(figsize=(16, 8))
        for n, azim in enumerate([-125, 55]):
            ax = fig.add_subplot(1, 2, n + 1, projection='3d')
            for triangles, ids, color, alpha in [(source, a, '#98b8d4', .18), (foreign, b, '#9c9c9c', .14), (source, sourceids, '#ef8e22', .75), (foreign, foreignids, '#326e99', .55)]:
                values = (triangles[ids] - center)[:, :, [0, 2, 1]]
                ax.add_collection3d(Poly3DCollection(values, facecolor=color, edgecolor='none', alpha=alpha))
            q = (points - center)[:, [0, 2, 1]]
            ax.scatter(q[:, 0], q[:, 1], q[:, 2], c='#c72020', s=6, depthshade=False)
            ax.set_xlim(lo[0]-center[0], hi[0]-center[0]); ax.set_ylim(lo[2]-center[2], hi[2]-center[2]); ax.set_zlim(lo[1]-center[1], hi[1]-center[1])
            ax.set_box_aspect((hi-lo)[[0,2,1]])
            ax.view_init(elev=25, azim=azim)
            ax.set(xlabel='Local east (m)', ylabel='Local Z (m)', zlabel='Height (m)')
        fig.suptitle(uid + ': every exact crossing; orange=Nam Cheong, blue=foreign, red=intersection')
        fig.tight_layout()
        path = doc / (uid.split('/')[1] + '-crossings.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=120);plt.close(fig)
        rows.append(dict(foreignUid=uid, contacts=len(contacts), sourceFaces=sourceids, foreignFaces=foreignids,
                         exactContactRecordsUnchanged=True, originalWorldIntersectionBounds=[points.min(0).tolist(), points.max(0).tolist()],
                         plottedSourceContextFaceIds=a.tolist(), plottedForeignContextFaceIds=b.tolist(),
                         imagePath=str(path.relative_to(ROOT)), coordinatesConvertedToFloatForPlotOnly=True))
    summary = dict(uids=[selected['uid']], rows=rows, currentForeignFormsEntriesAndRendererVerified=True,
                   currentManifestSHA256=digest(manifestpath.read_bytes()), sourceSHA256=selected['sourceSHA256'],
                   sourceGeometryChanges=0, installationApproved=False, acceptableContact=False,
                   qualification='Every saved exact crossing retained; float plotting is visualisation only, not a new intersection predicate, geometric repair, identity, support or collision approval. Source/foreign original assets, current forms and native entry/basic renderer modules verified unchanged.')
    save(doc / 'summary.json', summary)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('nam_crossing_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-current-bound-original-crossing-context-views', refs, summary)


if __name__ == '__main__':
    main()
