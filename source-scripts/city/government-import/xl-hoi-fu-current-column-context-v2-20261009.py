"""Complete fresh original face/ground and closed-column interface context."""
import json
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_shell_diagnostic_20261009 import shell_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,shell_self_intersections

BATCH='government-xl-hoi-fu-current-column-context-v2-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
CURRENT=HERE/'local/government-xl-hoi-fu-yu-complete-original-physical-v2-20261009/runtime-geometry.json.gz'
OLD=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-shell-cohort/diagnostic.json.gz'

def main():
    assert not DOC.exists()
    claim=reservations.claim('hoi-fu-current-column-'+str(uuid.uuid4()),
        ['building:landsd/177604:0','building:landsd/177605:0'],batch=BATCH,ttl=1800)
    assert claim['ok'],claim;lease=claim['reservation']
    try:
        old=next(r for r in read(OLD)['rows'] if r['uid']=='landsd/177604:0')
        g=next(r for r in read(CURRENT)['rows'] if r['uid']==old['uid'])
        historical=next(r for r in read(ROOT/old['runtimeGeometry'])['rows'] if r['uid']==old['uid'])
        assert g['sourceSHA256']==old['sourceSHA256']
        assert g['position']==historical['position'] and g['index']==historical['index']
        tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
        ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
        polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
        ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons)
        assert len(old['shells'])==1
        shell=shell_context(tri,old['shells'][0]['seedFaces'])
        assert shell['componentFaces']==old['shells'][0]['componentFaces']
        ids=set(shell['componentFaces']);outside=np.asarray(sorted(set(range(len(tri)))-ids))
        lower=tri[outside].min(axis=1);upper=tri[outside].max(axis=1);rational={};interfaces=[]
        for i in sorted(ids):
            face=tri[i];hits=np.flatnonzero(np.all(upper>=face.min(axis=0),axis=1)&np.all(lower<=face.max(axis=0),axis=1))
            a=rational_face(face)
            for j in hits:
                j=int(outside[j])
                if j not in rational:rational[j]=rational_face(tri[j])
                points=intersection_points(a,rational[j])
                if points:interfaces.append({'columnFace':i,'otherOriginalFace':j,'exactIntersectionPoints':[[str(v) for v in p] for p in sorted(points)]})
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
        assert np.isfinite(length).all()
        contexts=[]
        for i,face in enumerate(tri):
            context=(face_ground_context(face,ground,polygons,tree) if length[i]>0
                else degenerate_ground_context(face,ground,polygons,tree))
            context.update(sourceFace=i,inClosedColumn=i in ids,normalYRatio=float(normals[i,1]/length[i]) if length[i]>0 else None)
            contexts.append(context)
            if i%1000==0:
                assert reservations.heartbeat(lease)['ok']
                print(json.dumps({'facesChecked':i,'total':len(tri)}),flush=True)
        cert=shell_self_intersections(tri[sorted(ids)].tolist())
        refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [CURRENT,OLD,Path(__file__),HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_face_ground_crossing_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'original_shell_diagnostic_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'test_original_degenerate_ground_context_20261009.py']]
        refs += [{'path':p,'sha256':sha} for p,sha in read(CURRENT)['inputHashes'].items()]
        result={'uid':old['uid'],'sourceSHA256':g['sourceSHA256'],'sourceFaces':len(tri),
            'sourceGeometryIdenticalToHistorical':True,'originalZeroAreaFaces':int(sum(length==0)),'column':shell,'selfIntersections':cert,
            'originalComponentInterfaces':interfaces,'faces':contexts,'evidenceRefs':refs,
            'ordinaryContinuousMinimumGapM':min(c['minimum']['minimumGapM'] for c in contexts if not c['inClosedColumn'] and c['minimum']),
            'uncoveredOriginalFaces':sum(not c['groundProjectionCovered'] for c in contexts),
            'ordinaryBurialFailures':[c['sourceFace'] for c in contexts if not c['inClosedColumn'] and c['minimum'] and c['minimum']['minimumGapM']<-.5],
            'modelGeometryChanges':0,'installationApproved':False,'newlyInstalled':0,
            'qualification':'Every original face checked continuously against freshly drawn ground. Closed-column topology, exact self-intersections and every broad-phase-relevant other original face intersection are recorded. Source role and independently reviewed typed acceptance remain separate from this diagnostic.'}
        assert reservations.owns(lease)
        save(DOC/'diagnostic.json.gz',result)
        print(json.dumps({k:result[k] for k in ['sourceFaces','ordinaryContinuousMinimumGapM','uncoveredOriginalFaces','ordinaryBurialFailures']}),flush=True)
        print(json.dumps({'exactOriginalContacts':len(interfaces),'closedColumnFaces':len(ids),'selfIntersectionFree':cert['selfIntersectionFree']}),flush=True)
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
