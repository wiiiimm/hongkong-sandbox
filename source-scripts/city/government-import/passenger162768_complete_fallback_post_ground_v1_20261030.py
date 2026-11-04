"""Compare complete surveyed BASIC post footprints against actual before/after ground."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane
P='government-xl-passenger162768-after-civic-five-'
BATCH=P+'complete-fallback-post-ground-v1-20261030'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists()
    refs=[Path(__file__),HERE/'ronsdale_local_inset_v2_20261022.py'];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    name=P+'fallback-post-context-v1-20261030'
    parts=take(name,base/name/'parts.json')['description']['parts']
    grounds={}
    for mode,suffix in [('before','current-ground-v1-20261030'),('after','post-preserving-runtime-v1-20261030')]:
        batch=P+suffix
        data=take(batch,HERE/'local'/batch/'runtime-geometry.json.gz')
        g=next(r for r in data['rows'] if r['uid']=='landsd/162768:0')
        triangles=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
        polygons=shapely.polygons(triangles[:,:,[0,2]])
        valid=shapely.area(polygons)>0
        grounds[mode]=(triangles[valid],polygons[valid])
    rows=[]
    for i,part in enumerate(parts):
        if part['kind']!='post':continue
        footprint=shapely.Polygon(part['rings'][0],part['rings'][1:]);fragments={};row=dict(partIndex=i,bottomM=part['bottom'],topM=part['top'])
        for mode,(tri,polys) in grounds.items():
            clips=[];heights=[]
            for index in np.flatnonzero(shapely.intersects(polys,footprint)):
                fragment=polys[index].intersection(footprint)
                if fragment.area==0:continue
                equation=plane(tri[index]);xz=shapely.get_coordinates(fragment)
                heights.extend((xz@equation[:2]+equation[2]).tolist());clips.append((fragment,equation))
            assert heights
            cover=shapely.union_all([c[0] for c in clips])
            row[mode]=dict(groundRangeM=[min(heights),max(heights)],maximumPostBottomAboveGroundM=part['bottom']-min(heights),uncoveredPostFootprintM2=footprint.difference(cover).area)
            fragments[mode]=clips
        differences=[]
        for old,op in fragments['before']:
            for new,np_ in fragments['after']:
                overlap=old.intersection(new)
                if overlap.area==0:continue
                xz=shapely.get_coordinates(overlap);eq=np_-op
                differences.extend((xz@eq[:2]+eq[2]).tolist())
        assert differences
        row['completeOverlayMaximumAbsoluteGroundChangeM']=max(map(abs,differences));rows.append(row)
    assert len(rows)==8
    result=dict(uids=['landsd/162768:0','landsd/161745:0'],rows=rows,sourceGeometryChanges=0,terrainEdits=False,installationApproved=False,physicalAcceptance=False,qualification='Complete positive-area ground/post-footprint planar overlays from actual production runtime captures, not centroid samples. Raw coverage and floating-point changes retained. No surveyed post/elevation edits or architectural/installation acceptance.')
    save(doc/'summary.json',result)
    module('passenger_complete_fallback_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-surveyed-fallback-post-footprint-ground-before-after',refs,result)
    print([(r['partIndex'],r['after']['maximumPostBottomAboveGroundM'],r['completeOverlayMaximumAbsoluteGroundChangeM'],r['after']['uncoveredPostFootprintM2']) for r in rows])

if __name__=='__main__':main()
