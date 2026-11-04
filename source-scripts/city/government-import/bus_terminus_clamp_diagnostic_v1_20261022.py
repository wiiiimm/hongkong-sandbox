"""Diagnose original retained terrain clamp conflict; no candidate or waiver."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-bus-terminus-clamp-diagnostic-v1-20261022';DOC=BASE/BATCH
def main():
 assert not DOC.exists()
 cap=BASE/'government-xl-source-255415-full-parent-capture-v1-20261022';_,pins=authenticate(cap);p=cap/'ground.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];g=read(p)
 sel=BASE/'government-xl-next-three-terrain-runtime-v1-20261021';_,sp=authenticate(sel);q=sel/'selection.json.gz';assert digest(q.read_bytes())==sp[str(q.relative_to(ROOT))];r=next(r for r in read(q)['rows']if r['uid']=='landsd/255415:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==sp[str(asset.relative_to(ROOT))]
 tri=decode_original_world_triangles(asset.read_bytes());projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri]);core=projection.buffer(1,join_style='mitre');outer=core.buffer(5,join_style='mitre')
 faces=np.asarray([r['actualTriangle']for r in g['completeRestoredOriginalParentFacetsInsideRoutingMask']]).reshape(-1,3,3);ids=np.flatnonzero(faces[:,:,1].min(1)<1.2);rows=[]
 for i in ids:
  f=faces[i];poly=shapely.Polygon(f[:,[0,2]]);rows.append(dict(face=int(i),minimumY=float(f[:,1].min()),coreOverlapM2=poly.intersection(core).area,outerOverlapM2=poly.intersection(outer).area,triangle=f.tolist()))
 result=dict(uids=['landsd/255415:0'],belowClampFaces=len(rows),belowClampMinimumY=float(faces[:,:,1].min()),belowClampCoreOverlapM2=sum(r['coreOverlapM2']for r in rows),belowClampOuterOverlapM2=sum(r['outerOverlapM2']for r in rows),rows=rows,installationApproved=False,thresholdChanged=False,qualification='Original root template diagnostic only. No permission to bypass the terrain clamp and no physical acceptance.')
 save(DOC/'diagnostic.json',result)
 refs=[Path(__file__),p,cap/'result.json',q,sel/'result.json',asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'bus_terminus_local_inset_v2_20261022.py',BASE/'government-xl-bus-terminus-local-inset-v2-20261022/construction-failure.json']
 module('bus_clamp_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-parent-clamp-conflict-diagnostic',refs,result)
 print({k:v for k,v in result.items()if k!='rows'},flush=True)
if __name__=='__main__':main()
