"""Record exact below-grade Tian Tan Buddha source faces against recovered government terrain; never AI."""
import importlib.util,sys
from pathlib import Path

import numpy as np
import shapely

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('third',Path(__file__).with_name('xxl-third-pass.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=m.s
UID='landsd/241332:0'


def main():
    row=next(r for r in s.read(s.DOC/'selection.json.gz')['rows'] if r['uid']==UID)
    triangles=s.glb_triangles(row)
    lo,hi=triangles.min(axis=(0,1)),triangles.max(axis=(0,1))
    sources=s.read(s.DOC/'recovery.json')['sheets']+s.read(s.DOC/'adjacent-terrain-results.json')['sources']
    parts=[]
    for source in sources:
        for path in source['terrainPaths']:
            native=s.context.triangles(s.ROOT/path)
            native=native[(native[:,:,0].max(1)>=lo[0]-1)&(native[:,:,0].min(1)<=hi[0]+1)&(native[:,:,2].max(1)>=lo[2]-1)&(native[:,:,2].min(1)<=hi[2]+1)]
            if len(native):parts.append(native)
    native=np.concatenate(parts)
    polygons=shapely.polygons(native[:,:,[0,2]])
    valid=shapely.area(polygons)>1e-10
    native=native[valid];tree=shapely.STRtree(polygons[valid])
    points=np.concatenate([triangles,triangles.mean(1)[:,None,:]],1)
    heights=s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,tree).reshape(-1,4)
    gaps=points[:,:,1]-heights
    complete=np.isfinite(heights).all(1)
    buried=complete&(gaps<-.5).all(1)
    cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
    upward=cross[:,1]>.25*np.linalg.norm(cross,axis=1)
    rows=[]
    for index in np.where(buried)[0]:
        rows.append({'triangle':int(index),'vertices':triangles[index].tolist(),'centroid':triangles[index].mean(0).tolist(),'normal':(cross[index]/np.linalg.norm(cross[index])).tolist(),'area':float(np.linalg.norm(cross[index])/2),'gaps':gaps[index].tolist(),'upward':bool(upward[index])})
    result={'uid':UID,'sourceSHA256':row['sourceSHA256'],'modelBounds':[lo.tolist(),hi.tolist()],'fullyBuried':rows,'aiCalls':0,'geometryChanges':0,'publication':False}
    assert len(rows)==5 and sum(item['upward'] for item in rows)==1
    s.save(s.DOC/'third-pass/tian-tan-buried-faces.json',result)
    print({'fullyBuried':len(rows),'upward':sum(item['upward'] for item in rows),'aiCalls':0})


if __name__=='__main__':main()
