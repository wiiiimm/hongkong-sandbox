"""Exact full-source intersections with every nominated current native actor."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import intersection_points,rational_face,cross,sub
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-full-foreign-intersections-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name):
  folder=BASE/batch;_,pins=authenticate(folder);p=folder/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return read(p)
 def streams(row,attributes):
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);out=dict(original=decode_original_world_triangles(asset.read_bytes()));index=np.asarray(attributes['completeOriginalIndex']).reshape(-1,3)
  for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:out[mode]=np.asarray(attributes[key]).reshape(-1,3)[index]
  return out
 sourceRow=take('government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022','selection.json.gz')['rows'][0];sourceAttrs=take('government-xl-grand-aquarium-original-attributes-v1-20261022','attributes.json.gz')['rows'][0];source=streams(sourceRow,sourceAttrs);plan=take('government-xl-grand-aquarium-foreign-scope-plan-v1-20261022','summary.json');foreignRows=take('government-xl-grand-aquarium-foreign-scope-plan-v1-20261022','selection.json.gz')['rows'];foreignAttrs=take('government-xl-grand-aquarium-current-foreign-attributes-v1-20261022','attributes.json.gz')['rows'];assert {r['uid']for r in foreignRows}==set(plan['touchingNativeUids']);cache={};reports=[]
 for row in foreignRows:
  other=streams(row,next(r for r in foreignAttrs if r['uid']==row['uid']))
  for sm,s in source.items():
   sh=digest(s.tobytes())
   for fm,t in other.items():
    th=digest(t.tobytes());key=(sh,th)
    if key in cache:reports.append(dict(sourceMode=sm,foreignMode=fm,foreignUid=row['uid'],reusedIdenticalStreams=cache[key],sourceWorldSHA256=sh,foreignWorldSHA256=th));continue
    label=sm+'-'+fm+'-'+row['uid'].split('/')[1];lo,hi=t.min(1),t.max(1);tree=shapely.STRtree(shapely.box(lo[:,0],lo[:,2],hi[:,0],hi[:,2]));sr={};tr={};hits=[];pairs=0;collapsedSource=set();collapsedForeign=set()
    def rational(mesh,i,memo,collapsed):
     if i not in memo:memo[i]=rational_face(mesh[i])
     f=memo[i]
     if not any(cross(sub(f[1],f[0]),sub(f[2],f[0]))):collapsed.add(i);return None
     return f
    for i,f in enumerate(s):
     low,high=f.min(0),f.max(0);ids=tree.query(shapely.box(low[0],low[2],high[0],high[2]));ids=ids[(hi[ids,1]>=low[1])&(lo[ids,1]<=high[1])]
     if not len(ids):continue
     a=rational(s,i,sr,collapsedSource)
     if a is None:continue
     for j in ids:
      j=int(j);b=rational(t,j,tr,collapsedForeign)
      if b is None:continue
      pairs+=1;points=intersection_points(a,b)
      if points:hits.append(dict(sourceFace=i,foreignFace=j,exactIntersectionPoints=[[str(v)for v in p]for p in sorted(points)]))
     if i%1000==0:print(dict(streams=label,sourceFacesChecked=i,exactPairs=pairs,hits=len(hits)),flush=True)
    proof=dict(sourceMode=sm,foreignMode=fm,foreignUid=row['uid'],sourceWorldSHA256=sh,foreignWorldSHA256=th,completeSourceFaces=len(s),completeForeignFaces=len(t),closedAABBExactCandidatePairs=pairs,exactIntersections=hits,collapsedSourceCandidateFaces=sorted(collapsedSource),collapsedForeignCandidateFaces=sorted(collapsedForeign),collapsedFacesRemainInOriginalAssetsNoContactBridgeCredit=True,installationApproved=False);save(doc/(label+'.json.gz'),proof);reports.append({k:v for k,v in proof.items()if k!='exactIntersections'}|dict(exactIntersectionCount=len(hits)));cache[key]=label;print(dict(completed=label,pairs=pairs,hits=len(hits)),flush=True)
 result=dict(uids=['landsd/93424:0'],reports=reports,allNominatedNativeActorsAccounted=True,completeCurrentActorScopePlan=plan,sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,qualification='Full original source and current native meshes, all four source/foreign coordinate representations; only byte-identical complete world-triangle streams reuse results. Exact rational finite intersections; every detected contact remains unresolved pending interpretation. No source geometry edits or collision waivers.');save(doc/'summary.json',result);refs.extend(HERE/n for n in ['exact_original_shell_intersections_20261009.py','exact_packed_world_geometry_20261009.py']);module('aquarium_foreign_intersections_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-source-current-native-four-stream-exact-intersections',refs,result)
if __name__=='__main__':main()
