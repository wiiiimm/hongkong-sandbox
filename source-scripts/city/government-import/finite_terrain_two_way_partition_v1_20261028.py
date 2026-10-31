"""Partition Float32 terrain at one plane, with complete parent-face provenance.

This changes terrain triangulation only. It supplies no terrain, model, seam,
appearance or installation approval. Coplanar vertical faces belong to the east.
"""
import numpy as np
from southside_six_strip_partition_diagnostic_v1_20261028 import clip


def partition(triangles, split_x):
    source = np.asarray(triangles, dtype='<f4').astype('<f8')
    assert source.ndim == 3 and source.shape[1:] == (3, 3)
    assert np.isfinite(source).all() and np.isfinite(split_x)
    areas = np.linalg.norm(np.cross(source[:, 1]-source[:, 0], source[:, 2]-source[:, 0]), axis=1)/2
    represented = np.zeros(len(source), int)
    conserved = np.zeros(len(source))
    pieces = {}
    max_displacement = max_height_error = 0.
    for name, greater in [('west', False), ('east', True)]:
        output, parents = [], []
        for i, face in enumerate(source):
            if not greater and np.all(face[:, 0] == split_x):
                continue
            polygon = clip(list(face), split_x, greater)
            if not polygon:
                continue
            while len(polygon) < 3:
                polygon.append(polygon[-1].copy())
            for k in range(1, len(polygon)-1):
                part = np.asarray([polygon[0], polygon[k], polygon[k+1]])
                area = float(np.linalg.norm(np.cross(part[1]-part[0], part[2]-part[0]))/2)
                if area == 0 and areas[i] > 0:
                    continue
                represented[i] += 1
                conserved[i] += area
                output.append(part)
                parents.append(i)
        assert output, 'Both partition members must have geometry'
        exact = np.asarray(output)
        runtime = exact.astype('<f4').astype('<f8')
        max_displacement = max(max_displacement, float(abs(runtime-exact).max()))
        for part, i in zip(runtime, parents):
            original = source[i]
            n = np.cross(original[1]-original[0], original[2]-original[0])
            if n[1] != 0:
                height = original[0, 1]-((part[:, 0]-original[0, 0])*n[0]+(part[:, 2]-original[0, 2])*n[2])/n[1]
                max_height_error = max(max_height_error, float(abs(part[:, 1]-height).max()))
        pieces[name] = dict(triangles=runtime, parentFaceIndices=parents)
    vertices = {tuple(v) for p in pieces.values() for v in p['triangles'].reshape(-1, 3)}
    missing_vertices = [list(v) for v in {tuple(v) for v in source.reshape(-1, 3)}-vertices]
    missing_faces = np.flatnonzero(represented == 0).tolist()
    error = abs(conserved-areas)
    proof = dict(parentFaces=len(source), missingParentFaces=missing_faces,
        missingOriginalVertices=missing_vertices,
        maximumExactAreaErrorM2=float(error.max()),
        maximumRelativeAreaError=float((error/np.maximum(1, areas)).max()),
        maximumFloat32DisplacementM=max_displacement,
        maximumSourcePlaneHeightDriftM=max_height_error,
        verticalFacesOnCutOwnedBy='east', sourceBuildingGeometryChanges=0)
    assert not missing_faces and not missing_vertices, proof
    assert np.all(error <= np.maximum(1, areas)*1e-8), proof
    assert max_height_error < .01, proof
    return pieces, proof
