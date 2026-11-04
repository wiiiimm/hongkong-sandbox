"""Test exact-gap terrain caps below existing finite surfaces; no model approval."""
from pathlib import Path
import copy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_gap_float32_caps_v1_20261023 import enclosing_hull,lower_cap
from exact_original_projection_coverage_v2_20261010 import exact_coverage


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-paired-gap-caps-v1-20261023';out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=ROOT/name if name.startswith('source-scripts/')else base/batch/name
        assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    surface='government-xl-island-industrial-paired-surface-binding-v3-20261023';summary=take(surface,'summary.json');templates=[];arrays=[]
    for member in summary['members']:
        patch=take(surface,member['candidate']['path']);mesh=patch['nativeMesh'];t=np.asarray(mesh['position'],dtype='float32').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)].astype(float);arrays.append(t);templates.append(patch)
    old=np.concatenate(arrays);polygons=shapely.polygons(old[:,:,[0,2]]);normal=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);valid=np.abs(normal[:,1])>1e-10;ground=old[valid];polygons=polygons[valid];tree=shapely.STRtree(polygons)
    gaps='government-xl-island-industrial-exact-gap-pieces-v1-20261023';runtime='government-xl-island-industrial-paired-current-runtime-v1-20261023';geometry=take(runtime,'source-scripts/city/government-import/local/'+runtime+'/runtime-geometry.json.gz');added=[[],[]];caps=[];seen=set();crossings=[]
    for row in geometry['rows']:
        data=take(gaps,row['uid'].replace('/','-').replace(':','-')+'.json.gz');assert data['sourceSHA256']==row['sourceSHA256']
        for record in data['faces']:
            for gap in record.get('pieces',[]):
                hull=enclosing_hull(gap['rationalXZ']);a,b,c,d=hull.bounds
                if b<-4027.5<d:
                    crossings.append(dict(uid=row['uid'],sourceFace=record['sourceFace'],hullWKT=hull.wkt));continue
                key=hull.wkb
                if key in seen:continue
                seen.add(key);faces,proof=lower_cap(hull,ground,polygons,tree)
                member=0 if d<=-4027.5 else 1;added[member].extend(faces);caps.append(dict(uid=row['uid'],sourceFace=record['sourceFace'],member=member,**proof))
    assert caps
    outputs=[]
    for member,t,patch,faces in zip(summary['members'],arrays,templates,added):
        candidate=copy.deepcopy(patch);mesh=candidate['nativeMesh'];combined=np.concatenate([t,np.asarray(faces)])if faces else t
        mesh['position']=combined.reshape(-1).tolist();mesh['index']=list(range(combined.size//3));mesh.pop('sourceOverlap',None)
        for key in ['coordinatedBoundary','numericalCoverageGap','numericalProjectionOverlap']:mesh['source'].pop(key,None)
        mesh['source']['exactGapCapDiagnostic']=dict(policy='Constant finite adjacent-surface minimum rounded down one Float32 ULP; all old facets retained; no source building edits',publicationApproved=False)
        path=local/(member['member']+'-unapproved.json');save(path,candidate);refs.append(path);outputs.append(dict(member=member['member'],candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),replaces=member['replaces'],oldFaces=len(t),addedFaces=len(faces),terrainFaces=len(combined)))
    combined=np.concatenate([old,*[np.asarray(f)for f in added if f]]);rows=[]
    coverage='government-xl-island-industrial-paired-prephysical-20270-v1-20261023-coverage'
    for row in geometry['rows']:
        t=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];prior=take(coverage,row['uid'].split('/')[1]+'.json.gz');proofs=[]
        for face in prior['stillUncoveredFaces']:proofs.append(dict(sourceFace=face,**exact_coverage(t[face],combined)))
        save(out/(row['uid'].replace('/','-').replace(':','-')+'.json.gz'),dict(uid=row['uid'],proofs=proofs));rows.append(dict(uid=row['uid'],testedFaces=len(proofs),covered=sum(p['exactProjectionCovered']for p in proofs),stillUncovered=[p['sourceFace']for p in proofs if not p['exactProjectionCovered']]));print(rows[-1],flush=True)
    result=dict(uids=[r['uid']for r in rows],rows=rows,members=outputs,caps=len(caps),crossingBoundaryCapsNotApplied=crossings,allTestedFacesCovered=all(not r['stillUncovered']for r in rows),sourceGeometryChanges=0,installationApproved=False,status='private-exact-gap-cap-feasibility',qualification='All original terrain faces retained. Caps derived solely from exact failed projection gaps and authenticated finite adjacent terrain minima, no below-clamp faces. Only previously failed literal source projections tested; fresh source whole/four-world/native/shared-boundary/neighbour/base/browser acceptance required.')
    save(out/'caps.json.gz',caps);save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_gap_float32_caps_v1_20261023.py','test_exact_gap_float32_caps_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py'])
    module('gap_cap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-source-bound-exact-gap-terrain-cap-feasibility',refs,result)

if __name__=='__main__':main()
