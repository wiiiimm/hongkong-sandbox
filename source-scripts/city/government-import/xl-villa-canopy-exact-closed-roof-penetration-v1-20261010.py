"""Exact negative witnesses inside the actual closed procedural canopy roof.

All current canopy surfaces and source walls stay untouched. A strictly interior
source-face point in a verified closed vertical roof extrusion distinguishes
actual penetration from a finite boundary-only intersection. No acceptance.
"""
from collections import defaultdict,Counter
from fractions import Fraction as F
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,sub,dot,cross
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-villa-canopy-exact-closed-roof-penetration-v1-20261010';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-villa-canopy-complete-actual-foreign-wall-context-v1-20261010';PHYS=BASE/'government-xl-villa-five-original-coupled-physical-v3-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def barycentric(p,t):
 u=sub(t[1],t[0]);v=sub(t[2],t[0]);w=sub(p,t[0]);assert dot(cross(u,v),w)==0
 aa=dot(u,u);bb=dot(u,v);cc=dot(v,v);dd=dot(w,u);ee=dot(w,v);den=aa*cc-bb*bb
 assert den>0;b=(cc*dd-bb*ee)/den;c=(aa*ee-bb*dd)/den;return [1-b-c,b,c]
def main():
 assert not DOC.exists();prior=read(PRIOR/'diagnostic.json.gz');export=read(PRIOR/'actual-canopy-rendered-geometry.json')['rows'][0]
 foreign=np.asarray(export['position'],float).reshape(-1,3)[np.asarray(export['index']).reshape(-1,3)];edgefaces=defaultdict(list)
 for i,t in enumerate(foreign):
  vertices=[tuple(p) for p in t]
  for a,b in zip(vertices,vertices[1:]+vertices[:1]):edgefaces[tuple(sorted((a,b)))].append(i)
 adjacency=[set() for t in foreign]
 for ids in edgefaces.values():
  for i in ids:adjacency[i].update(ids)
 components=[];seen=set()
 for i in range(len(foreign)):
  if i in seen:continue
  pending=[i];part=[];seen.add(i)
  while pending:
   k=pending.pop();part.append(k)
   for j in adjacency[k]-seen:seen.add(j);pending.append(j)
  components.append(sorted(part))
 touched={c["sourceFaceB"] for t in prior["sourceAndLiteralAllWallTrials"] for c in t["exactActualSurfaceContacts"]["contacts"]}
 candidates=[]
 for ids in components:
  normal=np.cross(foreign[ids,1]-foreign[ids,0],foreign[ids,2]-foreign[ids,0]);length=np.linalg.norm(normal,axis=1)
  tops=[i for i,n,l in zip(ids,normal,length) if l and n[1]/l==1]
  if set(ids)&touched:candidates.append((ids,tops))
 assert len(candidates)==1;ids,tops=candidates[0];roof=foreign[ids];low=F.from_float(float(roof[:,:,1].min()));high=F.from_float(float(roof[:,:,1].max()));assert high>low
 edgecounts=Counter();directions=defaultdict(list)
 for t in roof:
  vs=[tuple(p) for p in t]
  assert len(set(vs))==3
  for a,b in zip(vs,vs[1:]+vs[:1]):
   key=tuple(sorted((a,b)));edgecounts[key]+=1;directions[key].append((a,b))
 assert set(edgecounts.values())=={2} and all(v[0]==tuple(reversed(v[1])) for v in directions.values())
 topids=[];bottomids=[];sideids=[]
 for i in ids:
  t=rational_face(foreign[i]);normal=cross(sub(t[1],t[0]),sub(t[2],t[0]));ys={p[1] for p in t}
  if ys=={high}:assert normal[1]>0;topids.append(i)
  elif ys=={low}:assert normal[1]<0;bottomids.append(i)
  else:assert ys=={low,high} and normal[1]==0;sideids.append(i)
 def projected_keys(indices):return sorted(tuple(sorted((p[0],p[2]) for p in rational_face(foreign[i]))) for i in indices)
 assert projected_keys(topids)==projected_keys(bottomids) and topids==tops
 mid=(low+high)/2;sections=[[(p[0],mid,p[2]) for p in rational_face(foreign[i])] for i in topids]
 selection=read(PHYS/'selection.json.gz')['rows'];runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath)['rows'];witnesses=[];tested=[];assets=[]
 for trial in prior['sourceAndLiteralAllWallTrials']:
  uid=trial['uid'];row=next(r for r in selection if r['uid']==uid);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];assets.append(asset)
  tri=decode_original_world_triangles(raw) if trial['representation']=='completeOriginal' else np.asarray(next(r for r in runtime if r['uid']==uid)['position'],float).reshape(-1,3)[np.asarray(next(r for r in runtime if r['uid']==uid)['index']).reshape(-1,3)]
  for fi in trial['allCreditedWallFaces']:
   t=rational_face(tri[fi]);count=0
   for cap,section in zip(topids,sections):
    points=intersection_points(t,section)
    if len(points)<2:continue
    count+=1;measure=contact_measure(points)
    if measure['dimension']!=1 or measure['maximumSpanM']<=0:continue
    pts=sorted(points);point=tuple(sum((p[k] for p in pts),F(0))/len(pts) for k in range(3));own=barycentric(point,t);roofb=barycentric(point,section)
    if min(own)>0 and min(roofb)>0:
     witnesses.append(dict(uid=uid,representation=trial['representation'],sourceFace=fi,completeSourceTriangle=tri[fi].tolist(),foreignRoofComponentFaces=ids,completeTopCapFace=cap,midSectionExactTriangle=[[str(v) for v in p] for p in section],exactInteriorPoint=[str(v) for v in point],strictSourceFaceBarycentric=[str(v) for v in own],strictRoofInteriorBarycentric=[str(v) for v in roofb],strictlyBetweenRoofLevels=True,positiveSourceInteriorSegment=measure,penetrationWitness=True))
   tested.append(dict(uid=uid,representation=trial['representation'],sourceFace=fi,allActualTopCapSections=len(sections),positiveMidSectionIntervals=count))
 assert witnesses,'No strict penetration witness; retain boundary-only investigation'
 result=dict(manifestSHA256=prior['manifestSHA256'],foreignUID=prior['foreignUID'],completeActualForeignFaces=len(foreign),completeRoofComponentFaces=ids,otherFullForeignComponents=components,completeClosedOrientedRoofEdgePairs=len(edgecounts),allEdgesExactlyTwoOppositelyOriented=True,fullUpperLowerCapXYPartitionsIdentical=True,fullVerticalSides=sideids,exactRoofLowerY=str(low),exactRoofUpperY=str(high),exactInteriorSectionY=str(mid),completeWallSectionTests=tested,strictInteriorPenetrationWitnesses=witnesses,positiveRenderedRoofVolumePenetration=True,boundaryOnlyContact=False,estimatedHeightsRemainEstimated=True,sourceGeometryChanges=0,identityAccepted=False,currentTypedPhysicalAccepted=False,fullAcceptance=False,publication=False,humanDecisionRequired=False,qualification='Exact original and literal source wall interior points lie strictly inside the actual generated closed canopy roof extrusion. This is a current procedural-render conflict, not surveyed canopy height, source corruption, or a property-ownership finding. No omission, distance padding or geometry edits.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[__file__,PRIOR/'result.json',PRIOR/'diagnostic.json.gz',PRIOR/'actual-canopy-rendered-geometry.json',PHYS/'result.json',PHYS/'selection.json.gz',runtimepath,HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',*assets]
 s=importlib.util.spec_from_file_location('villa_penetration_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'exact-current-closed-procedural-canopy-roof-positive-source-and-literal-penetration-negative-v1',sorted(set(map(__import__('pathlib').Path,refs))),dict(uids=[r['uid'] for r in selection]+[prior['foreignUID']],positiveRenderedRoofVolumePenetration=True,strictInteriorWitnesses=len(witnesses),sourceGeometryChanges=0,currentTypedPhysicalAccepted=False,fullAcceptance=False,humanDecisionRequired=False,humanStatus='held-current-foreign-procedural-roof-penetration',revisitConditions=['Recover the exact current government canopy original and recheck complete actual source collision/terrain/runtime; or explicitly reviewed source-backed current basic rendering correction with all strict gates. No source geometry edits, suppression, tolerance increases or NULL-height waiver.']))
 print(dict(strictInteriorPenetrationWitnesses=len(witnesses),sourceFaces=sorted(set(w['sourceFace'] for w in witnesses)),boundaryOnly=False),flush=True)
if __name__=='__main__':main()
