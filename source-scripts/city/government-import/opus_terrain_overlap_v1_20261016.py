"""Complete affine overlap-equation evidence; never runtime/publication approval."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,save,digest
from native_patch_resolution import projected_context

def qualify(patch,parent,doc,validator,source_files):
    g=patch['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(patch['w']-1)*g['aE'],816500-g['bN']-(patch['h']-1)*g['aN']]
    unapproved=doc/'unapproved-terrain.json';save(unapproved,patch)
    faces,polygons,missing,excess=projected_context(patch,bounds);assert excess>0
    tree=shapely.STRtree(polygons);left,right=tree.query(polygons,predicate='intersects');rows=[];worst=0;count=0
    for i,j in zip(left,right):
        if i>=j:continue
        overlap=polygons[i].intersection(polygons[j])
        if overlap.area<=1e-8:continue
        points=shapely.get_coordinates(overlap);errors=[];height_arrays=[]
        for face in [faces[i],faces[j]]:
            a,b,c=face;u=b-a;v=c-a;n=np.cross(u,v);assert n[1]!=0;d=points-a[[0,2]];det=u[0]*v[2]-u[2]*v[0];s=(d[:,0]*v[2]-d[:,1]*v[0])/det;t=(u[0]*d[:,1]-u[2]*d[:,0])/det;bary=a[1]+s*u[1]+t*v[1];plane=a[1]-(n[0]*d[:,0]+n[2]*d[:,1])/n[1];error=float(np.max(np.abs(bary-plane)));assert np.isfinite(error);errors.append(error);height_arrays.append(plane);count+=len(points)
        delta=height_arrays[0]-height_arrays[1];worst=max(worst,*errors)
        rows.append(dict(faceA=int(i),faceB=int(j),overlapAreaM2=overlap.area,overlapGeoJSON=shapely.to_geojson(overlap),faceVerticesA=faces[i].tolist(),faceVerticesB=faces[j].tolist(),heightDifferenceRangeM=[float(delta.min()),float(delta.max())],perFaceEquationErrorBoundM=errors))
    assert rows and worst<.01
    audit=dict(stagedGeometrySha256=digest(unapproved.read_bytes()),nativeProjectedExcessM2=excess,float32HighestRayAgreement=dict(samples=count,maxError=worst,rows=rows,method='All positive overlap pairs and polygon vertices; affine per-face differences bound both height equations throughout each intersection. MAX preserves this bound. Does not establish production sampler or GPU equivalence.'),source=dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in source_files]),policy='Retain the constructed original-source surfaces and scripted parent transition; use existing highest-native-surface semantics. No source building geometry changes or runtime acceptance.')
    ep=doc/'complete-overlap-proof.json';save(ep,audit);patch['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=excess,evidencePath=str(ep.relative_to(ROOT)),evidenceSHA256=digest(ep.read_bytes()))
    save(doc/'overlap-summary.json',dict(pairs=len(rows),equationVertexChecks=count,maxEquationErrorM=worst,projectedExcessM2=excess,missingAreaM2=missing.area,maxAbsoluteHeightDifferenceM=max(max(abs(v)for v in r['heightDifferenceRangeM'])for r in rows),fullAcceptance=False))
    validator(patch,parent)
