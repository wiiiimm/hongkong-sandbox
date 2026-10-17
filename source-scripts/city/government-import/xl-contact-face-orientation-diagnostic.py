"""Classify faces incident to existing clearance failures; never approve them.

Exact current runtime/contact hashes are mandatory. Vertical-wall failures do
not by themselves establish foundations, source identity or installation safety.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, read, save, digest


def classify(runtime_path, contact_path):
    runtime = read(runtime_path)
    contacts = read(contact_path)
    assert len(runtime['rows']) == len(contacts['rows']) == 1
    assert contacts['geometry'] == {'path': str(runtime_path.relative_to(ROOT)),
                                    'sha256': digest(runtime_path.read_bytes())}
    for path, sha in runtime['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha, 'Changed runtime input: ' + path
    row, contact = runtime['rows'][0], contacts['rows'][0]
    assert row['uid'] == contact['uid'] and row['sourceSHA256'] == contact['sourceSHA256']
    position = np.asarray(row['position']).reshape(-1, 3)
    index = np.asarray(row['index']).reshape(-1, 3)
    triangles = position[index]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    vertical_normal = np.divide(normals[:, 1], lengths, out=np.zeros(len(lengths)), where=lengths > 1e-10)
    failed_vertices = set()
    failed_faces = set()
    for point in contact['failed']:
        assert point['gap'] < -.5
        if point['kind'] == 'vertex':
            vertex = point['vertex']
            assert 0 <= vertex < len(position)
            assert np.array_equal(position[vertex], point['point'])
            failed_vertices.add(vertex)
        else:
            assert point['kind'] in {'centre', 'lowEdge'}
            assert 0 <= point['face'] < len(index)
            failed_faces.add(point['face'])
    failed_faces.update(np.flatnonzero(np.any(np.isin(index, list(failed_vertices)), axis=1)))
    faces = np.asarray(sorted(failed_faces), dtype=int)
    counts = {'upward': int((vertical_normal[faces] > .15).sum()),
              'downward': int((vertical_normal[faces] < -.15).sum()),
              'vertical': int((abs(vertical_normal[faces]) <= .15).sum()),
              'degenerate': int((lengths[faces] <= 1e-10).sum())}
    heights = position[list(failed_vertices), 1]
    return {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
            'failedCounts': contact['counts'], 'failedIncidentFaces': len(faces),
            'failedIncidentFaceNormals': counts,
            'failedVertexHeightRange': [float(heights.min()), float(heights.max())] if len(heights) else None,
            'allFailedFacesVertical': bool(len(faces) and counts['vertical'] == len(faces) and not counts['degenerate']),
            'minimumClearance': contact['minimumGap'], 'diagnosticOnly': True,
            'installationApproved': False, 'publication': False, 'modelGeometryChanges': 0,
            'qualification': 'Face orientation only. A wall-only failure is neither intentional-foundation evidence nor a clearance exception.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--contact', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    paths = [(ROOT / path).resolve() for path in [args.runtime, args.contact, args.out]]
    assert all(path.is_relative_to(ROOT) for path in paths)
    runtime, contact, out = paths
    assert not out.exists(), 'Fresh diagnostic output required'
    result = classify(runtime, contact)
    result['evidenceRefs'] = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
                              for p in [runtime, contact]]
    result['runnerSHA256'] = digest(Path(__file__).read_bytes())
    save(out, result)
    print(result['uid'], result['failedIncidentFaceNormals'], flush=True)


if __name__ == '__main__':
    main()
