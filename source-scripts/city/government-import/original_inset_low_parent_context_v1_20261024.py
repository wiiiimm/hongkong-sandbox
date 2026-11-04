"""Locate existing low parent terrain relative to a failed inset; no guard exception."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from ronsdale_local_inset_v2_20261022 import plane,lower_region
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','inset-failure','capture','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.inset_failure,a.capture])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    failed=take(a.inset_failure,base/a.inset_failure/'summary.json')
    assert failed['reason']=='native-terrain-near-water-clamp'and not failed['installationApproved']
    scope=take(a.inset_failure,base/a.inset_failure/'scope.json')
    selected=take(a.inset_failure,base/a.inset_failure/'original-face-scope.json')
    assert selected['uid']==a.uid
    data=take(a.capture,HERE/'local'/a.capture/'runtime-geometry.json.gz')
    g=next(r for r in data['rows']if r['uid']==a.uid);assert g['sourceSHA256']==selected['sourceSHA256']
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ids=selected['selectedWhollyBuriedUpwardFaceIds'];assert len(ids)==len(set(ids))and all(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0])[1]>0 for i in ids)
    projection=shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in tri[ids]])
    core=projection.buffer(1,join_style='mitre');outer=core.buffer(3,join_style='mitre')
    assert list(core.bounds)==scope['coreBounds']and list(outer.bounds)==scope['outerBounds']
    parent=take(a.inset_failure,HERE/'local'/a.inset_failure/'parent.json');assert parent['domain']==scope['bounds']
    for name,sha in parent['inputHashes'].items():
        path=ROOT/name;assert digest(path.read_bytes())==sha;refs.append(path)
    faces=np.asarray(parent['triangles']);low=[];regions=[]
    for i,t in enumerate(faces):
        if t[:,1].min()>=1.2:continue
        polygon=shapely.Polygon(t[:,[0,2]])
        if polygon.area<=1e-10:continue
        region=lower_region(polygon,plane(t)-np.array([0.,0.,1.2]))
        if region.is_empty:continue
        regions.append(region);low.append(dict(parentFace=i,minimumHeightM=float(t[:,1].min()),lowRegionAreaM2=region.area,lowRegionInsideOuterAreaM2=region.intersection(outer).area,lowRegionDistanceFromOuterM=region.distance(outer)))
    assert low
    union=shapely.union_all(regions)
    result=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],capturedParentFaces=len(faces),minimumParentHeightM=float(faces[:,:,1].min()),lowParentFaces=len(low),lowParentRegionInsideOuterAreaM2=union.intersection(outer).area,lowParentRegionDistanceFromOuterM=union.distance(outer),rows=low,sourceGeometryChanges=0,terrainEdits=False,installationApproved=False,physicalAcceptance=False,
        qualification='Diagnostic current-parent location only. Existing captured parent terrain triggered the constructor clamp before original-TIN contributions were processed. Float polygon measurements are not exact nonregression proof or permission to bypass the1.2m gate. A future bounded parent-retention method must preserve actual terrain/water/coastal surfaces in all relevant rendered representations, retain the new-source height gate and pass final validators.')
    save(out/'summary.json',result);refs.extend([HERE/'ronsdale_local_inset_v2_20261022.py',HERE/'selected_original_buried_upward_inset_v1_20261024.py'])
    module('original_low_parent_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'failed-inset-existing-low-parent-location-no-exception',list(dict.fromkeys(refs)),result)
    print({k:result[k]for k in ['lowParentFaces','lowParentRegionInsideOuterAreaM2','lowParentRegionDistanceFromOuterM']},flush=True)


if __name__=='__main__':main()
