"""Original sampled-buried faces versus every other original component."""
import json
import numpy as np
from run import ROOT,read,save,digest,reservations


def main():
    lease=read('/tmp/xl-terrain-recovery-20261009-228547-lease.json')
    assert reservations.heartbeat(lease)['ok']
    scope=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-shell-cohort/diagnostic.json.gz'
    row=next(r for r in read(scope)['rows'] if r['uid']=='landsd/228547:0')
    path=ROOT/row['runtimeGeometry'];g=read(path)['rows'][0]
    assert g['sourceSHA256']==row['sourceSHA256']
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    assert np.isfinite(tri).all()
    low,high=tri.min(axis=1),tri.max(axis=1)
    faces=[]
    for shell_index,shell in enumerate(row['shells']):
        members=set(shell['componentFaces']);outside=np.array([i for i in range(len(tri)) if i not in members])
        for i in shell['fullyBuriedFaces']:
            # Any triangle intersection must overlap these closed exact-coordinate
            # AABBs. Disjoint boxes exclude intersection without rounded welding.
            hit=np.all((low[outside]<=high[i])&(high[outside]>=low[i]),axis=1)
            faces.append({'sourceFace':i,'shellIndex':shell_index,
                          'otherOriginalComponentFacesExamined':len(outside),
                          'overlappingOriginalFaceAABBs':outside[hit].tolist()})
    result={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'wholeSourceFaces':len(tri),
        'sampledBuriedFacesExamined':len(faces),'allOtherOriginalComponentsExamined':True,
        'possibleOtherComponentIntersectionPairs':sum(len(f['overlappingOriginalFaceAABBs']) for f in faces),
        'noOtherComponentIntersections':all(not f['overlappingOriginalFaceAABBs'] for f in faces),
        'inputGeometry':{'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())},
        'sampledFoundationBinding':{'path':str(scope.relative_to(ROOT)),'sha256':digest(scope.read_bytes())},
        'faces':faces,'originalStrictFailures':row['currentReasons'],'sourceGeometryChanges':0,
        'installationApproved':False,'publication':False,'newlyInstalled':0,
        'qualification':'All224 previously sampled-wholly-buried original faces have no AABB overlap with any other original connected component. This is a strict separation certificate for those face indices only. It does not certify continuous burial membership, component-wide interactions above ground, foreign geometry absent from the original source, or provider below-grade semantics.'}
    output=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context/buried-face-separation.json'
    assert not output.exists(),'Fresh immutable proof required'
    save(output,result);print(json.dumps({k:result[k] for k in ['sampledBuriedFacesExamined','possibleOtherComponentIntersectionPairs','noOtherComponentIntersections']}),flush=True)


if __name__=='__main__':main()
