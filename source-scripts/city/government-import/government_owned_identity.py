"""Positive identity for an unchanged, individually owned government building.

This explicit alternative to the projected roof-area ratio requires the whole
GeoRef coordinate cell inside both original source geometry and current GIS form.
Cached spatial checks and current coverage/extent/unrelated-form bounds remain.
It provides identity only; placement, support and publication are separate gates.
"""
import hashlib
import json
import re
import importlib.util
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon, box
from original_source_ownership import evidence
from georef_projection_coverage import whole_cell_coverage

POLICY = 'original-government-owned-georef-identity-v1'
SOURCES = [
    'https://www.hkmapmeta.gov.hk/mcs/home/web/data/lands/b1000.faq.html',
    'https://static.csdi.gov.hk/csdi-webpage/download/common/5fae157cd31d217e580ea22cd65cc3e12f4bd55a26bf26339693b2865204ae1e',
]


def verify_files(row, context, local):
    """Re-decode exact source bytes and recheck current forms for each use."""
    from run import ROOT, HERE, digest
    local = Path(local).resolve()
    assert local.is_relative_to(HERE / 'local'), 'Established local cache only'
    source = (ROOT / row['candidate']['path']).resolve()
    assert source.is_relative_to(ROOT)
    raw = source.read_bytes()
    assert digest(raw) == row['sourceSHA256']
    assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
    for tile, sha in context['neighbourTileHashes'].items():
        assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    target = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target != source: target.write_bytes(raw)
    spec = importlib.util.spec_from_file_location('owned_identity_original_decoder', HERE / 'xl-second-pass.py')
    decoder = importlib.util.module_from_spec(spec); spec.loader.exec_module(decoder)
    decoder.LOCAL = local
    triangles = decoder.glb_triangles(row)
    return verify(raw, row, context, triangles)


def geographic_cell(model_id, csuid, structure):
    # LandsD trims decimals and the leading 8 from positive HK1980 coordinates.
    # A GeoRef describes a one-metre cell, never a recovered fractional point.
    if not re.fullmatch(r'B[0-9]{10}(01|02)06(2G|3C)[0-9A-Z]', model_id):
        raise ValueError('Unsupported government building model identifier')
    if not re.fullmatch(r'[0-9]{10}[TP][0-9]{8}', csuid):
        raise ValueError('Unsupported building CSUID')
    expected = {'Tower': ('01', 'T'), 'Podium': ('02', 'P')}.get(structure)
    if expected is None or (model_id[11:13], csuid[10]) != expected or model_id[1:11] != csuid[:10]:
        raise ValueError('Government GeoRef or tower/podium type differs')
    east = 800000 + int(csuid[:5]); north = 800000 + int(csuid[5:10])
    return box(east - 834500, 816500 - north - 1,
               east - 834500 + 1, 816500 - north)


def verify(raw, row, context, triangles):
    previous = evidence(raw, row, context)
    reasons = list(previous['reasons'])
    tri = np.asarray(triangles, dtype=float)
    form = row['source']['building']
    geometry_sha = hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest()
    cell_proof = {}
    if tri.shape != (row['triangles'], 3, 3) or not np.isfinite(tri).all():
        reasons.append('invalid-original-world-triangles')
    else:
        actual = np.array([tri.min(axis=(0, 1)), tri.max(axis=(0, 1))])
        expected = np.asarray(row['native']['model']['worldBounds'])
        if expected.shape != (2, 3) or not np.isfinite(expected).all() or np.max(np.abs(actual - expected)) >= .002:
            reasons.append('original-world-pose-or-bounds')
        try:
            cell = geographic_cell(row['modelId'], form['buildingCSUID'], form['structureType'])
            target = Polygon(form['rings'][0], form['rings'][1:])
            projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
            source_cell = whole_cell_coverage(tri, cell, projection)
            if not target.is_valid or target.area <= 0 or not target.covers(cell):
                reasons.append('current-target-does-not-cover-whole-georef-cell')
            if not projection.is_valid or projection.area <= 0 or not source_cell['coversWholeCell']:
                reasons.append('original-source-does-not-cover-whole-georef-cell')
            inside = projection.intersection(target).area
            measured = {'sourceProjectionAreaM2': float(projection.area),
                        'targetCoveredBySourceProjection': float(inside / target.area),
                        'sourceProjectionInsideTarget': float(inside / projection.area)}
            for key, value in measured.items():
                if abs(value - context['identity'][key]) > 1e-7:
                    reasons.append('full-source-projection-evidence-differs')
            cell_proof = {'worldXZBounds': list(cell.bounds), 'precisionMetres': 1,
                          'basis': 'GeoRef truncation of positive HK1980 easting/northing',
                          'targetCoversWholeCell': target.covers(cell),
                          'originalProjectionCoversWholeCell': source_cell['coversWholeCell'],
                          'projectionNumericalCoverage': source_cell}
        except (ValueError, KeyError, shapely.errors.GEOSException) as error:
            reasons.append('geographic-cell-proof:' + str(error))
    passed = not reasons
    return {'policy': POLICY, 'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
            'worldTrianglesSHA256': geometry_sha, 'sourceFormSHA256': hashlib.sha256(
                json.dumps(form, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'passed': passed, 'reasons': sorted(set(reasons)), 'geographicCell': cell_proof,
            'originalOwnership': previous, 'officialSpecificationSources': SOURCES,
            'proof': {'exactObjectId': passed, 'exactBuildingCSUID': passed,
                      'uniqueViewerMatch': passed, 'identityAccepted': passed},
            'roofAreaRatioReplacedByPositiveIdentity': passed,
            'installationApproved': False, 'modelGeometryChanges': 0,
            'qualification': 'Identity only: original byte/root/mesh ownership, exact unique government IDs, unmodified pose, whole geographic coordinate cell and cached/current spatial guards. Projected roof area is retained as evidence. No support, terrain, foundation, neighbour, runtime or publication gate is waived.'}
