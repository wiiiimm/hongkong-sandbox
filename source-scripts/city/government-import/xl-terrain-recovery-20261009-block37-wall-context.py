"""New whole-face terrain context for Block37; no changed acceptance policy."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from original_face_ground_crossing_20261009 import face_ground_context
from original_shell_diagnostic_20261009 import shell_context

BATCH='xl-terrain-recovery-20261009-block37-wall-context'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
SCOPE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-shell-cohort/diagnostic.json.gz'
LEASE=Path('/tmp/xl-terrain-recovery-20261009-228547-lease.json')
UID='landsd/228547:0'


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not (DOC/'diagnostic.json.gz').exists(),'Fresh evidence path required'
    lease=read(LEASE);assert reservations.owns(lease)
    row=next(r for r in read(SCOPE)['rows'] if r['uid']==UID)
    path=ROOT/row['runtimeGeometry'];g=next(r for r in read(path)['rows'] if r['uid']==UID)
    assert g['sourceSHA256']==row['sourceSHA256']
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    polygons=shapely.polygons(ground[:,:,[0,2]])
    valid=shapely.area(polygons)>1e-10;ground,polygons=ground[valid],polygons[valid]
    tree=shapely.STRtree(polygons)
    spec=importlib.util.spec_from_file_location('block37_sample_context',HERE/'xl-final-script-pass.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    pts=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1)
    heights=module.s.context.shared.samples(pts[:,:,[0,2]].reshape(-1,2),ground,tree).reshape(-1,4)
    gaps=pts[:,:,1]-heights
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
    assert (length>0).all(),'Authored degenerate faces need independent review'
    upward=normals[:,1]>.25*length
    shell_faces=set(i for s in row['shells'] for i in s['componentFaces'])
    faces=[]
    for i,face in enumerate(tri):
        context=face_ground_context(face,ground,polygons,tree)
        context.update(sourceFace=i,normalYRatio=float(normals[i,1]/length[i]),
            upward=bool(upward[i]),inClosedBuriedComponent=i in shell_faces,
            sampledMinimumGapM=float(gaps[i].min()),sampledMaximumGapM=float(gaps[i].max()))
        faces.append(context)
        if i%2000==0:
            assert reservations.heartbeat(lease)['ok']
            print(json.dumps({'facesChecked':i,'total':len(tri)}),flush=True)
    outside=[f for f in faces if not f['inClosedBuriedComponent']]
    affected=[f for f in outside if f['minimum'] and f['minimum']['minimumGapM']<-.5]
    sampled_affected=[f for f in outside if f['sampledMinimumGapM']<-.5]
    groups=[];pending=set(f['sourceFace'] for f in affected)
    while pending:
        context=shell_context(tri,[min(pending)]);pending.difference_update(context['componentFaces'])
        context['affectedFaces']=sorted(set(context['componentFaces']).intersection(f['sourceFace'] for f in affected))
        groups.append(context)
    provider=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009/block37-provider-context.json'
    refs=[ref(p) for p in [Path(__file__),HERE/'original_face_ground_crossing_20261009.py',
        HERE/'test_original_face_ground_crossing_20261009.py',SCOPE,path,provider]]+row['historicalEvidenceRefs']
    result={'batch':BATCH,'uid':UID,'sourceSHA256':row['sourceSHA256'],'sourceFaces':len(tri),
        'historicalTerrain':True,'evidenceRefs':list({r['path']:r for r in refs}.values()),
        'allOriginalFacesExamined':True,'sourceGeometryChanges':0,'newlyInstalled':0,
        'publication':False,'installationApproved':False,'rawStrictFailures':row['currentReasons'],
        'closedBuriedComponentFaces':len(shell_faces),'sampledOutsideAffectedFaces':len(sampled_affected),
        'continuousOutsideAffectedFaces':len(affected),
        'affectedUpwardFaces':sum(f['upward'] for f in affected),
        'affectedExactlyVerticalFaces':sum(f['verticalFace'] for f in affected),
        'affectedProjectionUncoveredFaces':sum(not f['groundProjectionCovered'] for f in affected),
        'affectedNoExposedUpperWitnessFaces':sum(f['maximumObservedGapM'] is None or f['maximumObservedGapM']<=0 for f in affected),
        'wholeSourceProjectionUncoveredFaces':sum(not f['groundProjectionCovered'] for f in faces),
        'wholeSourceUpwardMinimumGapM':min(f['minimum']['minimumGapM'] for f in faces if f['upward'] and f['minimum']),
        'outsideMinimumGapM':min(f['minimum']['minimumGapM'] for f in outside if f['minimum']),
        'affectedComponentContexts':groups,'faces':faces,
        'providerExteriorOpenBottomClassification':None,'modelGeometryAI':False,
        'qualification':'Whole original source face intersections against byte-pinned historical drawn ground, including vertical walls. Minimum uses floating-point facet intersections; maximum is only an exposed witness, not a continuous certificate. Generic provider Podium classification does not authorise exterior/open-bottom or below-grade semantics. Existing strict metrics and all independent gates remain unchanged.'}
    assert reservations.owns(lease)
    save(DOC/'diagnostic.json.gz',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['faces','evidenceRefs','affectedComponentContexts','qualification']}),flush=True)


if __name__=='__main__':main()
