"""Locate all sampled hotel/TIN intersections; preserve source faces and thresholds."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import disney_hotel_original_terrain_feasibility_v1_20261015 as prior

BATCH='government-xl-disney-hotel-original-terrain-gap-attribution-v1-20261015'
DOC=ROOT/'docs/astra-city/government-import'/BATCH

def main():
    assert not DOC.exists()
    receipt=read(prior.DOC/'result.json');refs=[Path(__file__),Path(prior.__file__),prior.DOC/'result.json']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'];refs.append(ROOT/ref['path'])
    helper=module('hotel_gap_attribution',HERE/'xl-final-script-pass.py')
    terrain=helper.s.context.triangles(next((prior.TERRAIN/'decoded').rglob('*.gltf')))
    original_ids=np.arange(len(terrain));polygons=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
    terrain,polygons,original_ids=terrain[valid],polygons[valid],original_ids[valid]
    source=read(HERE/'local'/prior.PRIOR.name/'runtime-geometry.json.gz')['rows'][0]
    triangles=np.asarray(source['position']).reshape(-1,3)[np.asarray(source['index']).reshape(-1,3)]
    points=np.concatenate([triangles,triangles.mean(axis=1)[:,None,:]],axis=1)
    tree=shapely.STRtree(polygons)
    heights=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain,tree).reshape(-1,4)
    gaps=points[:,:,1]-heights
    failures=np.argwhere(np.isfinite(heights)&(gaps<-.5));rows=[]
    for face,point in failures:
        p=points[face,point];ids=tree.query(shapely.Point(p[[0,2]]),predicate='covered_by')
        values=[]
        for i in ids:
            t=terrain[i];n=np.cross(t[1]-t[0],t[2]-t[0]);y=(np.dot(n,t[0])-n[0]*p[0]-n[2]*p[2])/n[1]
            if abs(y-heights[face,point])<1e-7:values.append(int(original_ids[i]))
        assert values
        rows.append(dict(sourceFace=int(face),sample=int(point),position=p.tolist(),gapM=float(gaps[face,point]),terrainFaceIds=values,sourceTriangle=triangles[face].tolist()))
    rows.sort(key=lambda r:r['gapM'])
    summary=dict(sourceFaces=len(triangles),sampleFailures=len(rows),affectedFaces=len({r['sourceFace']for r in rows}),minimumGapM=rows[0]['gapM']if rows else None,completeFaces=int(np.isfinite(heights).all(axis=1).sum()),terrainFacesCausingMaximum=sorted({i for r in rows for i in r['terrainFaceIds']}),fullAcceptance=False)
    DOC.mkdir();save(DOC/'attribution.json.gz',dict(summary=summary,rows=rows));save(DOC/'summary.json',summary)
    refs.append(Path(helper.s.context.shared.__file__))
    result=module('hotel_attribution_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-hotel-all-negative-samples-original-terrain-v1',refs,dict(uids=['landsd/236354:0'],summary=summary,fullAcceptance=False,newlyInstalled=0))
    print(dict(jobId=result['jobId'],summary=summary,worstSamples=rows[:2]),flush=True)

if __name__=='__main__':main()
