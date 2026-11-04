"""Complete original/current/primary party-edge diagnosis, no identity credit."""
import importlib.util
import json
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_mesh_components import face_components
from no1_garden_original_overhead_roof_edge_identity_20261010 import polygon, primary_polygon

BATCH = 'government-xl-fung-yip-distinct-original-shared-boundary-diagnostic-v2-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
BASE = DOC.parent
OWN = 'landsd/79883:0'
FOREIGN = ['landsd/12728:0', 'landsd/79882:0']
INPUTS = [BASE / 'government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010/selection.json.gz',
          BASE / 'government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010/selection.json.gz']
PRIMARY = BASE / 'government-xl-fung-yip-three-podium-primary-relationships-20261010/diagnostic.json'
CONTACT = BASE / 'xl-terrain-recovery-20261010-fung-yip-complete-original-foreign-context-v1/diagnostic.json.gz'

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out

def main():
    assert not DOC.exists()
    claim = reservations.claim('fung-yip-distinct-boundary-' + str(uuid.uuid4()),
        ['building:' + u for u in [OWN, *FOREIGN]], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        DOC.mkdir(parents=True)
        manifest = ROOT / '3d-viewer/city/data/manifest.json'
        before = manifest.read_bytes()
        rows = {r['uid']: r for p in INPUTS for r in read(p)['rows']}
        worlds = {}; assets = []
        for uid in [OWN, *FOREIGN]:
            path = ROOT / rows[uid]['candidate']['path']; assets.append(path)
            raw = path.read_bytes(); assert digest(raw) == rows[uid]['sourceSHA256']
            worlds[uid] = decode_original_world_triangles(raw)
        own = worlds[OWN]; assert len(own) == 398
        parts = face_components(own)
        membership = {int(f): i for i, part in enumerate(parts) for f in part}
        final = module('fung_distinct_complete_forms', 'xl-final-script-pass.py')
        low = np.concatenate(list(worlds.values())).min(axis=(0,1))
        high = np.concatenate(list(worlds.values())).max(axis=(0,1))
        forms = final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2])
        current = {b['uid']:b for b,_,_ in forms}
        assert all(u in current for u in [OWN,*FOREIGN])
        providers = {}
        for uid in [OWN,*FOREIGN]:
            matches = [p for p in read(PRIMARY)['primary'] if p['attributes']['BuildingCSUID'] == current[uid]['buildingCSUID']]
            assert len(matches) == 1
            providers[uid] = matches[0]
        projection = shapely.union_all(shapely.polygons(own[:,:,[0,2]]))
        contact_rows = [r for r in read(CONTACT)['rows'] if r['sourceUID'] == OWN]
        report = []
        for other in FOREIGN:
            contact = next(r for r in contact_rows if r['foreignUID'] == other)
            assert contact['ownWorldSHA256'] == digest(own.tobytes())
            assert contact['foreignWorldSHA256'] == digest(worlds[other].tobytes())
            positive = [c for c in contact['completeActualOriginalSurfaceIntersections']['contacts'] if c['dimension'] > 0]
            contacted = {c['sourceFaceA'] for c in positive}
            own_poly = polygon(current[OWN]['rings']); foreign_poly = polygon(current[other]['rings'])
            checks = {}
            for label, a, b in [('current',own_poly,foreign_poly),('primary',primary_polygon(providers[OWN]),primary_polygon(providers[other]))]:
                shared = a.boundary.intersection(b.boundary)
                overlap = projection.difference(a).intersection(b)
                ids = [i for i,t in enumerate(own) if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area > 0]
                details = []
                for i in ids:
                    t = own[i]; n = np.cross(t[1]-t[0],t[2]-t[0])
                    portion = shapely.Polygon(t[:,[0,2]]).intersection(overlap)
                    coords = shapely.get_coordinates(portion)
                    details.append(dict(face=i,part=membership[i],vertices=t.tolist(),normal=n.tolist(),
                        projectedExcessAreaM2=portion.area,projectedExcessGeometry=shapely.to_geojson(portion),
                        exactPositiveOriginalContact=i in contacted,
                        positiveOriginalContactForeignFaceIds=sorted({c['sourceFaceB'] for c in positive if c['sourceFaceA']==i}),
                        maximumExcessVertexDistanceFromExactSharedBoundaryM=None if shared.is_empty else float(shapely.distance(shapely.points(coords),shared).max())))
                checks[label] = dict(fullFootprintIntersectionAreaM2=a.intersection(b).area,
                    exactSharedBoundaryLengthM=shared.length,sharedBoundary=shapely.to_geojson(shared),
                    rawForeignExcessM2=overlap.area,allExcessFaceIds=ids,allExcessFaces=details,
                    excessFacesWithoutDirectPositiveOriginalContact=sorted(set(ids)-contacted))
            report.append(dict(foreignUID=other,completeForeignFaces=len(worlds[other]),
                completeActualOriginalPositiveInterfaces=positive,checks=checks))
        refs = [Path(__file__),*INPUTS,PRIMARY,CONTACT,*assets,
                HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_mesh_components.py',
                HERE/'no1_garden_original_overhead_roof_edge_identity_20261010.py']
        refs += [ROOT/'3d-viewer'/tile for _,_,tile in forms]
        out = dict(uids=[OWN,*FOREIGN],uid=OWN,foreignUIDs=FOREIGN,manifestSHA256=digest(before),completeOwnFaces=398,
            completeOwnParts=len(parts),allOriginalPartFaceIds=[p.tolist() for p in parts],
            completeSourceVersions={u:rows[u]['sourceSHA256'] for u in [OWN,*FOREIGN]},
            completeWorldVersions={u:digest(worlds[u].tobytes()) for u in [OWN,*FOREIGN]},
            allCurrentForms=[b for b,_,_ in forms],primary=providers,distinctPermitEvidence=read(PRIMARY)['structures'],rows=report,
            identityAccepted=False,physicalAccepted=False,structuralSupportAccepted=False,installationApproved=False,sourceGeometryChanges=0,
            qualification='Distinct original/provider/current actors remain separate. Full-source foreign excess and every original face/part/contact are retained. Boundary association and positive interfaces alone imply neither common property/permit nor support/collision acceptance. This diagnosis identifies exact non-contact faces requiring an independently reviewed source role.',
            evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in refs])
        save(DOC/'diagnostic.json.gz',out)
        assert manifest.read_bytes() == before
        fence = module('fung_distinct_boundary_fence','xl-popcorn-source-investigations-checkpoints-20261009.py')
        result = fence.freeze(BATCH,'complete-distinct-original-shared-boundary-diagnosis-v1',refs,out)
        print(json.dumps(dict(jobId=result['jobId'],parts=len(parts),rows=[dict(foreign=r['foreignUID'],checks={k:{x:v for x,v in c.items() if x in ['rawForeignExcessM2','exactSharedBoundaryLengthM','fullFootprintIntersectionAreaM2','excessFacesWithoutDirectPositiveOriginalContact']} for k,c in r['checks'].items()}) for r in report])),flush=True)
    finally:
        assert reservations.release(lease)['ok']

if __name__ == '__main__': main()
