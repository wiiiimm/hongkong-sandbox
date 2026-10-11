import sys,pathlib,json,numpy as np
from shapely.geometry import Point
H=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(H));import support_context as ctx
p,v=ctx.native('landsd/209787:0');v=np.unique(v,axis=0);ground=ctx.ground(v[:,0],v[:,2]);bad=v[(v[:,1]<v[:,1].min()+.5)&(v[:,1]-ground>1)]
manifest=ctx.manifest;tp=H/'staged/11-SW-4D'/manifest['terrain']['url'];tv,_=ctx.model_geometry(ctx.read(tp),lambda u:(tp.parent/u).read_bytes());rows=[]
for v in bad:
 ev=ctx.triangle_evidence(tp,tv,Point(v[0],v[2]).buffer(.01),4.1,4.1,1);rows.append({'nativeBuildingVertex':v.tolist(),'current5mTerrainHKPD':float(ctx.ground(v[0],v[2])),'sourceNativeTerrainRays':ev['rays']})
(H/'studio-terrain-exception.json').write_text(json.dumps({'uid':'landsd/209787:0','problemBottomVertices':rows,'terrainSource':str(tp.relative_to(ctx.R)),'qualifier':'Read-only native TIN comparison; no model shifts or multiplier.'},indent=2)+'\n');print(json.dumps(rows,indent=2))
