"""One native mesh: complete original parent outside an exact child rectangle.

This is a candidate representation helper, never an acceptance decision. All
parent triangles participate, including retaining/vertical/degenerate faces.
It does not use a height-only surface subset or infer equivalence from grids.
Internal seam, full outside finite-facet/vertical equivalence, standard native
mesh validation and every model/actor/physics/runtime gate remain mandatory.
"""
import copy,sys,numpy as np
from run import HERE,digest
sys.path.insert(0,str(HERE.parent/'assembly-support-review'));import exact_tin as exact
def faces(patch):
 mesh=patch['nativeMesh'];p=np.asarray(mesh['position'],dtype=np.float32).astype(np.float64).reshape(-1,3);return p[np.asarray(mesh['index'],int).reshape(-1,3)]
def bounds(patch):
 g=patch['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];return [x,z,x+(patch['w']-1)*g['aE'],z-(patch['h']-1)*g['aN']]
def compose(parent,child,*,terrain_budget=100000):
 assert parent.get('nativeMesh') and child.get('nativeMesh') and not parent.get('patches') and not child.get('patches')
 assert not parent.get('hydro') and not child.get('hydro')
 pb,cb=bounds(parent),bounds(child);assert pb[0]<cb[0]<cb[2]<pb[2] and pb[1]<cb[1]<cb[3]<pb[3]
 pt,ct=faces(parent),faces(child);assert np.isfinite(pt).all() and np.isfinite(ct).all()
 regions=[('north',[pb[0],pb[1],pb[2],cb[1]]),('south',[pb[0],cb[3],pb[2],pb[3]]),('west',[pb[0],cb[1],cb[0],cb[3]]),('east',[cb[2],cb[1],pb[2],cb[3]])]
 output=[];records=[];vertical_ids=[]
 for i,t in enumerate(pt):
  lo,hi=t[:,[0,2]].min(axis=0),t[:,[0,2]].max(axis=0);vertical=abs(float(np.cross(t[1]-t[0],t[2]-t[0])[1]))<=1e-10;start=len(output)
  if hi[0]<cb[0] or lo[0]>cb[2] or hi[1]<cb[1] or lo[1]>cb[3]:output.append(t);role='whole-runtime-face-unchanged'
  else:
   seen=set();role='complete-original-face-clipped-only-on-child-boundaries'
   for region,bb in regions:
    poly=exact.rect(list(t),bb)
    for j in range(1,len(poly)-1):
     face=np.asarray([poly[0],poly[j],poly[j+1]],float)
     if np.linalg.norm(np.cross(face[1]-face[0],face[2]-face[0]))<1e-8:continue
     key=tuple(sorted(map(tuple,face)))
     if key not in seen:output.append(face);seen.add(key)
   if len(output)==start:role='original-face-inside-child-replacement'
  if vertical and len(output)>start:vertical_ids.append(i)
  records.append({'originalParentFace':i,'originalRuntimeVertices':t.tolist(),'verticalOrZeroProjection':vertical,'role':role,'retainedOutputFaceRange':[start,len(output)]})
 outside=np.asarray(output,float);combined=np.concatenate([outside,ct]);count=len(combined)
 census={'originalParentFaces':len(pt),'completeChildFaces':len(ct),'allParentFacesAccounted':len(records),'outsideRetainedFaces':len(outside),'fullCombinedFaces':count,'terrainBudget':terrain_budget,'withinUnchangedRuntimeBudget':count<=terrain_budget,'allRetainedVerticalOriginalFaceIds':vertical_ids,'allOriginalParentFaceDispositions':records,'parentRuntimeTriangleSHA256':digest(pt.astype('<f8').tobytes()),'childRuntimeTriangleSHA256':digest(ct.astype('<f8').tobytes()),'allCombinedRuntimeTriangleSHA256':digest(combined.astype('<f8').tobytes()),'parentRectangle':pb,'childRectangle':cb,'physicalAccepted':False,'installationApproved':False,'modelGeometryChanges':0,'qualification':'Exact rectangle ownership and complete parent triangle provenance candidate. All retaining/vertical faces outside/on child boundaries are retained independently of height sampling. Full finite-facet/vertical/outside and internal seam equivalence must be independently proved on Float32 rendered geometry before acceptance.'}
 if count>terrain_budget:return None,census
 out=copy.deepcopy(parent);out['id']=child['id'];out['meta']['targetUids']=sorted(set(parent['meta']['targetUids'])|set(child['meta']['targetUids']));out['nativeMesh']={'position':combined.reshape(-1).tolist(),'index':list(range(len(combined)*3)),'source':{'verticalDatum':'HKPD','verticalScale':1,'policy':'Candidate single-mesh original parent exterior plus exact bounded child; complete independent surface/seam/runtime acceptance still required.','parentRuntimeTriangleSHA256':census['parentRuntimeTriangleSHA256'],'childRuntimeTriangleSHA256':census['childRuntimeTriangleSHA256']}}
 return out,census
