"""Read-only saved exact-source contact diagrams; no acceptance or model edits."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
CONTACT = BASE / 'government-xl-one-peking-after-twin-installed-native-contacts-v1-20261101'
DOC = BASE / 'government-xl-one-peking-after-twin-saved-contact-views-v1-20261101'

def main():
    assert not DOC.exists()
    receipt, pins = authenticate(CONTACT)
    path = CONTACT / '233985:0--73140:0--original.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    contact = read(path)
    assert contact['allPairsExamined'] and len(contact['contacts']) == 12
    assert all(c['dimension'] == 1 for c in contact['contacts'])
    identity, _ = authenticate(BASE / 'government-xl-one-peking-after-twin-fresh-current-named-identity-v2-20261101')
    meshes = []
    sources = []
    for sha in ['73c65ee4568e2feb34e51e379db43a189824eb71eebba995b13de9d5456e9331', 'de03f5a51ec4b294a3e5c7d3e924324dbc21709f648f33c7d69254e19f484bc1']:
        ref = next(r for r in identity['evidenceRefs'] if r['sha256'] == sha and r['path'].endswith('.glb.gz'))
        raw = (ROOT / ref['path']).read_bytes()
        assert digest(raw) == sha
        meshes.append(decode_original_world_triangles(raw))
        sources.append(ref)
    assert [len(m) for m in meshes] == [4114, 32635]
    ids = [sorted({c['sourceFace' + side] for c in contact['contacts']}) for side in ['A', 'B']]
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), dpi=100)
    for row, bounds in enumerate([[[980, -980, 0], [1120, -820, 30]], [[997, -936, 3], [1005, -926, 11]]]):
        # Plot coordinates are X,Z,Y; crop is display-only and never an acceptance mask.
        lo, hi = map(np.asarray, bounds)
        for col, dims in enumerate([(0, 2), (0, 1), (2, 1)]):
            ax = axes[row, col]
            for mesh, face_ids, color in zip(meshes, ids, ['#267bbc', '#cb873d']):
                t = mesh[:, :, [0, 2, 1]]
                keep = ((t.max(1) >= lo) & (t.min(1) <= hi)).all(1)
                ax.add_collection(PolyCollection(t[keep][:, :, dims], facecolors=color, edgecolors=color, linewidths=.15, alpha=.12))
                ax.add_collection(PolyCollection(t[face_ids][:, :, dims], facecolors='none', edgecolors=color, linewidths=1.4))
            for c in contact['contacts']:
                p = np.asarray([[float(Fraction(v)) for v in xyz] for xyz in c['exactPoints']])[:, [0, 2, 1]]
                ax.plot(p[:, dims[0]], p[:, dims[1]], color='#c00061', linewidth=2)
            ax.set(xlim=(lo[dims[0]], hi[dims[0]]), ylim=(lo[dims[1]], hi[dims[1]]), xlabel=['X', 'Z', 'Y'][dims[0]], ylabel=['X', 'Z', 'Y'][dims[1]])
            ax.set_aspect('equal', adjustable='box')
            ax.grid(alpha=.2)
    fig.suptitle('Exact unchanged original meshes: One Peking podium (blue), Hullett (ochre), 12 finite contacts (magenta)\nFull context above; display crop below. Projection diagram only: no ownership, support or collision approval.')
    fig.tight_layout(rect=(0, 0, 1, .94))
    DOC.mkdir()
    fig.savefig(DOC / 'exact-contact-context-1800x1200.png')
    plt.close(fig)
    save(DOC / 'context.json', dict(sourceRefs=sources, contactJobId=receipt['jobId'], contactRef=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), faceIds=ids, sourceGeometryChanges=0, approval=False))

if __name__ == '__main__':
    main()
