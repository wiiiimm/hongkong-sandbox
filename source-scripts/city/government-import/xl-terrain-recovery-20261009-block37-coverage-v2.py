"""Full original terrain-union coverage correction; no model/terrain edits."""
import json
import numpy as np
import shapely
from run import ROOT,read,save,digest,reservations


def main():
    lease=read('/tmp/xl-terrain-recovery-20261009-228547-lease.json')
    assert reservations.heartbeat(lease)['ok']
    path=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context/diagnostic.json.gz'
    row=read(path)
    gpath=next(x['path'] for x in row['evidenceRefs'] if x['path'].endswith('runtime-geometry.json.gz'))
    g=read(ROOT/gpath)['rows'][0]
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    polygons=shapely.polygons(ground[:,:,[0,2]])
    polygons=polygons[shapely.area(polygons)>1e-10];tree=shapely.STRtree(polygons)
    assert len(tri)==row['sourceFaces'] and row['sourceSHA256']==g['sourceSHA256']
    faces=[]
    for face in row['faces']:
        i=face['sourceFace'];projection=shapely.MultiPoint(tri[i][:,[0,2]]).convex_hull
        union=shapely.union_all(polygons[tree.query(projection,predicate='intersects')])
        missing=projection.difference(union)
        faces.append({'sourceFace':i,'groundProjectionCovered':bool(union.covers(projection)),
            'uncoveredProjectionLengthM':float(missing.length),'uncoveredProjectionAreaM2':float(missing.area),
            'priorClippedUnionCovered':face['groundProjectionCovered']})
        if i%2000==0:assert reservations.heartbeat(lease)['ok']
    affected={f['sourceFace'] for f in row['faces'] if not f['inClosedBuriedComponent']
              and f['minimum'] and f['minimum']['minimumGapM']<-.5}
    component=row['affectedComponentContexts'][0];edges={}
    for i in component['componentFaces']:
        for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
            edges.setdefault(tuple(sorted([tuple(a),tuple(b)])),[]).append(i)
    boundary=[np.asarray(e) for e,ids in edges.items() if len(ids)==1]
    result={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'sourceFaces':len(tri),
        'allOriginalFacesExamined':True,'previousDiagnostic':{'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())},
        'inputGeometry':{'path':gpath,'sha256':digest((ROOT/gpath).read_bytes())},'minimumAlgorithmUnchanged':True,
        'wholeSourceUncoveredFaces':sum(not f['groundProjectionCovered'] for f in faces),
        'affectedUncoveredFaces':sum(not f['groundProjectionCovered'] for f in faces if f['sourceFace'] in affected),
        'priorWholeSourceClippedUnionUncoveredFaces':row['wholeSourceProjectionUncoveredFaces'],
        'priorAffectedClippedUnionUncoveredFaces':row['affectedProjectionUncoveredFaces'],'affectedFaces':len(affected),
        'componentBoundaryEdges':len(boundary),
        'componentBoundaryEdgesBothBelow9Point01HKPD':int(sum((e[:,1]<=9.01).all() for e in boundary)),
        'componentBoundaryEdgesBothAbove9Point01HKPD':int(sum((e[:,1]>9.01).all() for e in boundary)),
        'boundaryElevationClassificationIsDiagnosticOnly':True,
        'coverageMethod':'Full original terrain facet union, no buffer or tolerance credit','faces':faces,
        'installationApproved':False,'newlyInstalled':0,'sourceGeometryChanges':0,'publication':False}
    output=path.parent/'coverage-v2.json.gz'
    if output.exists():assert read(output)==result,'Immutable coverage receipt differs'
    else:save(output,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['faces','previousDiagnostic','inputGeometry']}),flush=True)


if __name__=='__main__':main()
