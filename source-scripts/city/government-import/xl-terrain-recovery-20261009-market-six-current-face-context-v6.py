"""New continuous authored wall/roof diagnosis on original cached podium."""
import json,sys
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage

UID=sys.argv[1]
assert UID in {'landsd/313033:0','landsd/313034:0','landsd/313116:0','landsd/313118:0','landsd/313119:0','landsd/313121:0'}
BATCH='xl-terrain-recovery-20261009-market-six-current-face-context-v6/'+UID.split('/')[1].replace(':','-')
DOC=ROOT/'docs/astra-city/government-import'/BATCH
GEOMETRY=HERE/'local/government-xl-terrain-recovery-market-six-original-physical-v5-20261009/runtime-geometry.json.gz'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009'
LEASE='/tmp/xl-terrain-recovery-20261009-market-six-face-context-lease.json'

def main():
    assert not DOC.exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok'];assert read(PRIOR/'neon-sync.json')['resultVerified']
    g=next(x for x in read(GEOMETRY)['rows'] if x['uid']==UID);row=next(x for x in read(PRIOR/'selection.json.gz')['rows'] if x['uid']==UID)
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==g['sourceSHA256']==row['sourceSHA256']
    tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1)
    ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0)
    polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
    ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons)
    contexts=[]
    for i,t in enumerate(tri):
        c=face_ground_context(t,ground,polygons,tree) if length[i]>0 else degenerate_ground_context(t,ground,polygons,tree)
        c=apply_exact_coverage(c,t,ground)
        contexts.append(dict(c,sourceFace=i,normalYRatio=float(ratio[i]) if length[i]>0 else None))
        if i%100==0:assert reservations.heartbeat(lease)['ok'];print(json.dumps({'facesChecked':i,'total':len(tri)}),flush=True)
    affected=[i for i,c in enumerate(contexts) if c['minimum'] and c['minimum']['minimumGapM']<-.5]
    wall_faces=[i for i in affected if length[i]>0 and abs(ratio[i])<=.25]
    binding=source_stream_binding(raw);binding.update(decodedWorldTrianglesSHA256=digest(tri.tobytes()),drawnGroundSHA256=digest(ground.tobytes()))
    paths=original_open_paths(tri,contexts,wall_faces,range(len(tri)),expected_binding=binding,current_binding=binding)
    result={'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'wholeSourceFaces':len(tri),'faces':contexts,
        'wholeSourceUncoveredFaces':sum(not c['groundProjectionCovered'] for c in contexts),
        'continuousAffectedFaces':affected,'affectedWallFaces':wall_faces,
        'otherAffectedFaces':[i for i in affected if i not in wall_faces],
        'upwardContinuousMinimumGapM':min(c['minimum']['minimumGapM'] for i,c in enumerate(contexts) if ratio[i]>.25 and c['minimum']),
        'originalOpenExteriorPaths':paths,'allAffectedWallsHaveRoles':paths['allAffectedWallsHaveRoles'],
        'originalZeroAreaFaces':np.flatnonzero(length==0).tolist(),
        'evidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [
            GEOMETRY,PRIOR/'selection.json.gz',PRIOR/'result.json',asset,HERE/'original_face_ground_crossing_v2_20261009.py',
            HERE/'original_face_ground_crossing_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',
            HERE/'unchanged_open_exterior_paths_v2_20261009.py',HERE/'test_unchanged_open_exterior_paths_v2_20261009.py',
            HERE/'exact_projection_coverage_fallback_context_20261009.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'test_exact_original_projection_coverage_20261009.py',HERE/'xl_source_stream_binding_20261009.py',Path(__file__)]],
        'installationApproved':False,'publication':False,'sourceGeometryChanges':0,
        'qualification':'New complete continuous original face-role diagnosis against byte-pinned historical drawn terrain. Historical geometry is not a current live physical acceptance. Whole independent identity/support/neighbour/runtime metrics remain separate; browser/publication still required; raw historical failures retained.'}
    assert reservations.owns(lease);save(DOC/'diagnostic.json.gz',result)
    print(json.dumps({k:result[k] for k in ['uid','wholeSourceFaces','wholeSourceUncoveredFaces','upwardContinuousMinimumGapM','allAffectedWallsHaveRoles','otherAffectedFaces']}),flush=True)

if __name__=='__main__':main()
