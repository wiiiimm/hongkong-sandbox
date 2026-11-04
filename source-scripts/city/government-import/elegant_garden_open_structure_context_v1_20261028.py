"""Display the retained BASIC canopy against the unchanged original podium.

Diagnostic materials/sections only; no deletion, ownership or support approval.
"""
import uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from southside_original_gap_sections_v1_20261028 import section

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-elegant-garden-open-structure-context-v1-20261028'
DOC = BASE/BATCH
CAP = BASE/'government-xl-elegant-garden-seven-original-private-runtime-v1-20261028'
CONTACT = BASE/'government-xl-elegant-garden-seven-original-current-foreign-contacts-v1-20261028'
UID, FOREIGN = 'landsd/236170:0', 'landsd/99061:0'


def main():
    assert not DOC.exists()
    refs, pins = [Path(__file__), HERE/'southside_original_gap_sections_v1_20261028.py',
                  HERE/'exact_packed_world_geometry_20261009.py'], {}
    for directory in [CAP, CONTACT]:
        _, bound = authenticate(directory)
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(CAP/'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    raw_path = ROOT/row['candidate']['path']
    assert digest(raw_path.read_bytes()) == row['sourceSHA256']
    refs.append(raw_path)
    basic = next(r for r in take(CONTACT/'basic.json')['rows'] if r['uid'] == FOREIGN)
    proof = take(CONTACT/'236170:0--99061:0--original.json.gz')
    assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0 and len(proof['contacts']) == 84
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    claim = reservations.claim('elegant-open-structure-context-'+str(uuid.uuid4()),
        ['building:'+UID, 'building:'+FOREIGN], batch=BATCH, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        original = decode_original_world_triangles(raw_path.read_bytes())
        assert len(original) == row['triangles']
        points = np.asarray(basic['position']).reshape(-1, 3)
        geometry = points[np.asarray(basic['index']).reshape(-1, 3)]
        centre = np.asarray(basic['currentBuilding']['centre'])
        bounds = [points.min(0), points.max(0)]
        fig, axes = plt.subplots(2, 2, figsize=(14, 11), constrained_layout=True)
        for ax, zoom in [(axes[0, 0], False), (axes[0, 1], True)]:
            ax.add_collection(PolyCollection(original[:, :, [0, 2]], facecolors='#1674b2', edgecolors='#1674b2', alpha=.15, linewidths=.25))
            ax.add_collection(PolyCollection(geometry[:, :, [0, 2]], facecolors='#ec7a22', edgecolors='#ac4d08', alpha=.4, linewidths=.6))
            low, high = (bounds if zoom else [original.min((0, 1)), original.max((0, 1))])
            ax.set_xlim(low[0]-3, high[0]+3); ax.set_ylim(low[2]-3, high[2]+3)
            ax.set_aspect('equal'); ax.grid(alpha=.2)
            ax.set_xlabel('world X (m)'); ax.set_ylabel('world Z (m)')
            ax.set_title('Whole original podium / BASIC canopy' if not zoom else 'Canopy footprint — display crop only')
        counts = []
        for ax, axis, horizontal, coordinate in [(axes[1, 0], 0, 2, centre[0]), (axes[1, 1], 2, 0, centre[1])]:
            for key, tri, color in [('original podium', original, '#1674b2'), ('current BASIC canopy', geometry, '#d36813')]:
                cut = section(tri, axis, coordinate)
                ax.add_collection(LineCollection(cut[:, :, [horizontal, 1]], colors=color, linewidths=1.1, label=key))
                counts.append(dict(geometry=key, planeAxis=axis, planeCoordinate=float(coordinate), sectionSegments=len(cut)))
            ax.set_xlim(bounds[0][horizontal]-3, bounds[1][horizontal]+3)
            ax.set_ylim(bounds[0][1]-4, bounds[1][1]+4)
            ax.set_aspect('equal'); ax.grid(alpha=.2)
            ax.set_xlabel(('world Z' if horizontal == 2 else 'world X')+' (m)')
            ax.set_ylabel('HKPD elevation (m)'); ax.legend(fontsize=8)
            ax.set_title(f"{'X' if axis == 0 else 'Z'} = {coordinate:.6f} m")
        fig.suptitle('Elegant Garden: original podium 236170 and retained open-sided structure 99061\nBlue: every original podium face · orange: actual current BASIC mesh\nEstimated BASIC heights are context, not surveyed source identity. No geometry changes or approval.', fontsize=12)
        path = DOC/'original-podium-basic-canopy-context-2100x1650.png'
        path.parent.mkdir(parents=True)
        fig.savefig(path, dpi=150); plt.close(fig)
        out = dict(uids=[UID, FOREIGN], sourceSHA256=row['sourceSHA256'], sourceFaces=len(original),
            completeBasicFaces=len(geometry), basicBounds=[b.tolist() for b in bounds],
            rawSourceContactPairs=len(proof['contacts']), sections=counts,
            image=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), width=2100, height=1650),
            basicSourceMetadata={k:basic['currentBuilding'].get(k) for k in ['base','height','baseSource','heightSource','baseHeightHKPD','topHeightHKPD','structureType','buildingCSUID']},
            sourceGeometryChanges=0, installationApproved=False, sourceRoleAccepted=False,
            qualification='All unchanged original podium faces and actual current BASIC mesh retained. Axis-aligned float64 sections and camera crops are explanatory only; exact original finite contacts remain separately bound. Estimated BASIC canopy elevation is not an authoritative government model surface. No visibility suppression, source-role, structural or installation acceptance.')
        save(DOC/'summary.json', out)
        assert reservations.owns(lease)
        module('elegant_open_structure_context_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'original-podium-current-basic-open-structure-context', list(dict.fromkeys(refs)), out)
        print(dict(image=str(path), sourceFaces=len(original), basicFaces=len(geometry)), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
