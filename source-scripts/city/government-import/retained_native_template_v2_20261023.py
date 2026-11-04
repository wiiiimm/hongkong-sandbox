"""Reuse a complete installed envelope; never author terrain below its clamp."""
import copy
from collections import Counter
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, read, save, digest


def exact_rendered_face_multiset(original, captured):
    original, captured = np.asarray(original), np.asarray(captured)
    assert original.shape == captured.shape and original.ndim == 3 and original.shape[1:] == (3, 3)
    assert np.isfinite(original).all() and np.isfinite(captured).all()
    # Production stores Float32 positions and may reverse winding. Compare
    # complete vertex tuples, including duplicate-face multiplicity; no halo.
    def canonical(triangles):
        return Counter(tuple(sorted(map(tuple, face))) for face in triangles)
    return canonical(original.astype('float32').astype('float64')) == canonical(captured)


def verify_existing_low_faces(baseline, output, lineage, outer):
    baseline, output = np.asarray(baseline), np.asarray(output)
    assert len(output) == len(lineage)
    low = np.flatnonzero(baseline[:, :, 1].min(1) < 1.2)
    for i in low:
        projection = shapely.MultiPoint(baseline[i][:, [0, 2]]).convex_hull
        assert projection.distance(outer) > 0, 'Existing below-clamp face touches the proposed edit region'
    retained = set()
    for face, record in zip(output, lineage):
        if face[:, 1].min() >= 1.2:
            continue
        assert record['kind'] == 'unchanged', 'New or split terrain below existing clamp is forbidden'
        i = record['parentFace']
        assert i in low and np.array_equal(face, baseline[i]), 'Existing low terrain changed'
        retained.add(int(i))
    assert retained == set(map(int, low)), 'Existing low terrain lost'
    return dict(existingLowFaces=len(low), allExistingLowFacesRetainedExactly=True,
                allExistingLowFacesDisjointFromEdit=True, newlyAuthoredLowFaces=0,
                allowNativeBelowClamp=False)


def reuse_template(cells, parent, baseline, retained, outer, doc, local, builder):
    assert len(retained) == 1, 'Exact envelope reuse requires one complete existing patch'
    path = ROOT / '3d-viewer' / retained[0]['url']
    assert digest(path.read_bytes()) == retained[0]['sha256']
    template = read(path)
    assert cells == template['coarseCells'], 'Expanded envelope needs a separately validated template'
    assert not template.get('patches') and not template.get('hydro')
    assert template['meta']['parentTerrain'] == 'city/data/terrain.json'
    assert template['meta']['parentSha256'] == digest((ROOT / '3d-viewer/city/data/terrain.json').read_bytes())
    original = np.asarray(template['nativeMesh']['position']).reshape(-1, 3)[np.asarray(template['nativeMesh']['index']).reshape(-1, 3)]
    assert exact_rendered_face_multiset(original, baseline), 'Captured retained ground differs from exact rendered installed faces'
    unchanged = [dict(kind='unchanged', parentFace=i) for i in range(len(baseline))]
    proof = verify_existing_low_faces(baseline, baseline, unchanged, outer)
    builder.validate_patch(template, parent)
    save(doc / 'retained-template-proof.json', dict(proof, templatePath=str(path.relative_to(ROOT)),
        templateSHA256=retained[0]['sha256'], coarseCells=cells,
        qualification='Exact existing validated template reused only for its identical complete envelope. Every existing below-clamp face is outside the edit region and must remain byte-identical; every new face still obeys the 1.2m guard. No below-clamp option is enabled.'))
    return copy.deepcopy(template)
