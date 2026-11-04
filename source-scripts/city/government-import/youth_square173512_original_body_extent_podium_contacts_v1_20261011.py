"""DRAFT: immutable 13100+22 originals, historical extent/body attribution and finite contacts."""
from pathlib import Path
from collections import Counter, defaultdict, deque
import json
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face, intersection_points, cross, sub, dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B = ROOT / 'docs/astra-city/government-import'
UID, PODIUM = 'landsd/173512:0', 'landsd/139415:0'
OLD = B / 'government-xl-spatial-surface-roles-20261009/173512-0.json.gz'
INPUT = B / 'government-xl-eight-new-original-closures-20261008/support-inputs.json'
FOLLOW = B / 'government-xl-eight-current-component-followups-20261008/173512-0.json'
LEDGER = B / 'government-xl-identity-190-actionable-ledger-20261010/ledger.json.gz'
DISP = B / 'government-xl-current-320-blocker-families-20261009/dispositions.json.gz'
METHOD = B / 'government-xl-youth-square173512-original-source-method-v1-20261011/METHOD.md'
DOC = B / 'government-xl-youth-square173512-original-body-extent-podium-contacts-v1-20261011'
EXPECTED = {UID: ('a3905a76856bc0c622d7f09139995fd2429d294771b68e2385317056987fcea1', 13100, 'B424281381401063C0', '4242813814T20100329'), PODIUM: ('1edf63068d903718bec435d4c9426f38192a1e5f32da1c439867a3cd530375a9', 22, 'B424091381802063C0', '4240913818P20080619')}
def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()
    old, inputs = read(OLD), read(INPUT)
    ledger = next(r for r in read(LEDGER)['rows'] if r['uid'] == UID)
    disposition = next(r for r in read(DISP)['rows'] if r['uid'] == UID)
    assert old['uid'] == UID and not ledger['installed'] and not disposition['installed']
    assert disposition['reasons'] == ['source-identity-fit']
    triangles, sources, censuses, labels = {}, {}, {}, {}
    for uid, (sha, count, model, csuid) in EXPECTED.items():
        s = next(r for r in inputs['sources'] if r['uid'] == uid)
        assert s['sourceSHA256'] == sha and s['modelId'] == model
        assert s['source']['building']['buildingCSUID'] == csuid
        assert s['candidate']['entry']['buildingCSUID'] == csuid
        asset = ROOT / s['candidate']['path']
        assert ref(asset)['sha256'] == sha
        t = decode_original_world_triangles(asset.read_bytes())
        assert t.shape == (count, 3, 3) and np.isfinite(t).all()
        if uid == UID:
            assert ref(asset)['path'] == old['originalPath']
            assert sha == old['sourceSHA256'] == ledger['sourceSHA256'] == disposition['sourceSHA256']
            assert digest(t.astype('<f8').tobytes()) == old['worldTrianglesSHA256'] == '6119e583590a5940678bec0e52b45e463c563fa8441a2f5ebe92fce68f3f5fc5'
        c = census(t, list(range(count)))
        lab = {f: k for k, fs in enumerate(c['sharedEdgeConnectedComponents']) for f in fs}
        assert set(lab).isdisjoint(c['exactNonrenderingOriginalFaces'])
        assert set(lab) | set(c['exactNonrenderingOriginalFaces']) == set(range(count))
        triangles[uid], sources[uid], censuses[uid], labels[uid] = t, ref(asset), c, lab
    t, p = triangles[UID], triangles[PODIUM]
    variant = old['variants']['direct-shared-OSM']
    forms = {f['uid']: f for f in variant['groupForms']}
    assert set(forms) == set(EXPECTED)
    polygons = {uid: shapely.Polygon(f['rings'][0], f['rings'][1:]) for uid, f in forms.items()}
    group = shapely.union_all(list(polygons.values()))
    distance = shapely.distance(shapely.points(t[:, :, [0, 2]].reshape(-1, 2)), group).reshape(-1, 3)
    far = list(map(int, np.flatnonzero(distance.max(1) > 10)))
    assert len(far) == variant['stats']['sourceFacesBeyond10m'] == 286
    assert float(distance.max()) == variant['stats']['maximumSourceExtentM']
    face_edges, incidence = {}, defaultdict(set)
    for i in sorted(labels[UID]):
        face_edges[i] = []
        for j in range(3):
            key = tuple(sorted([tuple(t[i, j]), tuple(t[i, (j + 1) % 3])]))
            assert key[0] != key[1]
            face_edges[i].append(key)
            incidence[key].add(i)
    projected = shapely.polygons(t[:, :, [0, 2]])
    target = set(map(int, np.flatnonzero(shapely.area(shapely.intersection(projected, polygons[UID])) > 0))) & set(labels[UID])
    parent = {i: None for i in sorted(target)}
    queue = deque(sorted(target))
    while queue:
        i = queue.popleft()
        for key in face_edges[i]:
            for j in sorted(incidence[key] - {i}):
                if j not in parent:
                    parent[j] = i
                    queue.append(j)
    far_rows = []
    for i in far:
        path = [i] if i in parent else []
        while path and parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        far_rows.append(dict(originalFace=i, body=labels[UID].get(i), triangle=t[i].tolist(), historicalGroupVertexDistancesM=distance[i].tolist(), exactSharedEdgePathToTowerProjectedFacet=path, pathProvidesNoIdentityOrSupportCredit=True))
    records, tested, rational = [], 0, {}
    plo, phi = p.min(1), p.max(1)
    def face(uid, i):
        key = (uid, i)
        if key not in rational:
            rational[key] = rational_face(triangles[uid][i])
        return rational[key]
    for i in range(len(t)):
        if i not in labels[UID]:
            continue
        js = np.flatnonzero(np.all(phi >= t[i].min(0), axis=1) & np.all(t[i].max(0) >= plo, axis=1))
        for j0 in js:
            j = int(j0)
            if j not in labels[PODIUM]:
                continue
            tested += 1
            a, z = face(UID, i), face(PODIUM, j)
            points = sorted(intersection_points(a, z))
            if not points:
                continue
            measure = contact_measure(points)
            na, nz = cross(sub(a[1], a[0]), sub(a[2], a[0])), cross(sub(z[1], z[0]), sub(z[2], z[0]))
            cop = not any(cross(na, nz)) and all(dot(na, sub(v, a[0])) == 0 for v in z)
            mid = tuple(sum(v[k] for v in points) / len(points) for k in range(3))
            records.append(dict(towerFace=i, podiumFace=j, towerBody=labels[UID][i], podiumBody=labels[PODIUM][j], exactPoints=[[str(v) for v in q] for q in points], coplanar=cop, bothRelativeInteriorCrossing=not cop and measure['dimension'] > 0 and relative_interior(a, mid) and relative_interior(z, mid), **measure))
    obligations = []
    for uid in EXPECTED:
        for k, fs in enumerate(censuses[uid]['sharedEdgeConnectedComponents']):
            v = triangles[uid][fs]
            obligations.append(dict(uid=uid, body=k, originalFaces=fs, originalBounds=[v.min((0, 1)).tolist(), v.max((0, 1)).tolist()], farFaces=[i for i in far if uid == UID and labels[UID].get(i) == k], architectureIdentityMountGroundSupportUnqualified=True))
    paths = [Path(__file__), METHOD, OLD, INPUT, FOLLOW, LEDGER, DISP]
    paths += [ROOT / s['path'] for s in sources.values()]
    paths += [HERE / name for name in ['exact_packed_world_geometry_20261009.py', 'exact_original_shared_edge_component_census_v2_20261011.py', 'test_exact_original_shared_edge_component_census_v2_20261011.py', 'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py', 'science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py', 'test_science_museum_contact_relative_interior_v1_20261011.py']]
    for uid in EXPECTED:
        assert ref(ROOT / sources[uid]['path']) == sources[uid]
    d = dict(uid=UID, podiumUid=PODIUM, sources=sources, worldSHA256={uid: digest(v.astype('<f8').tobytes()) for uid, v in triangles.items()}, completeFaces={UID: 13100, PODIUM: 22}, originalCensuses=censuses, allBodyObligations=obligations, all286HistoricalGroupFarFaces=far_rows, historicalGroupStats=variant['stats'], historicalTowerAndPodiumForms=forms, preservedExact190ForeignExcessM2=11.392121249111536, priorSampledInterface=read(FOLLOW), completeTowerPodiumPairDomain=13100 * 22, exactNonzeroInclusive3DAABBPairsTested=tested, allFiniteTowerPodiumContacts=records, sourceOnly=True, historicalInputsOnly=True, currentAcceptance=False, identityAccepted=False, installationApproved=False, sourceGeometryChanges=0, terrainGeometryChanges=0, structuralRootCredit=False, qualification='Complete unchanged original source census and historical extent attribution, with all nonzero tower/podium finite contacts. Exact zero faces retained separately. Geometric connectivity and positive contacts neither establish architectural role, solid collision nor support. Grouped foreign0 and exact190 separate podium11.392m2 excess are distinct historical measurements, both preserved. Prior one-sample/zero-strict interface and terrain negatives remain. No refreshed remaining membership, primary-plan identity, footprint exemption, current runtime/ground/native/foreign or acceptance proof.', evidenceRefs=[ref(q) for q in paths])
    save(DOC / 'diagnostic.json.gz', d)
    print(json.dumps(dict(completeFaces=d['completeFaces'], bodies={uid: len(c['sharedEdgeConnectedComponents']) for uid, c in censuses.items()}, farFaces=len(far_rows), testedFinitePairs=tested, contacts=len(records), contactDimensions=dict(Counter(r['dimension'] for r in records)), currentAcceptance=False)), flush=True)
if __name__ == '__main__':
    main()
