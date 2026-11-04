"""Unexecuted exact source-accounted terrain proposal. Never source/role acceptance."""
from fractions import Fraction as F
import hashlib,math,struct
import numpy as np
ORIGIN=(834500,816500)
def point(p):
 assert len(p)==3 and all(isinstance(v,(int,float,np.integer,np.floating))and math.isfinite(v)for v in p)
 return tuple(F(int(v))if isinstance(v,(int,np.integer))else F(float(v))for v in p)
def normal(t):
 a,b,c=map(point,t);u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
 return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
def area_real(t):return any(normal(t))
def clean(poly):
 out=[]
 for p in poly:
  if not out or p!=out[-1]:out.append(p)
 if len(out)>1 and out[0]==out[-1]:out.pop()
 return out

def clip(poly,plane):
 if not poly:return []
 a,b,c=plane;out=[]
 def value(p):return a*p[0]+b*p[2]+c
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=value(p),value(q)
  if dp>=0:out.append(p)
  if (dp<0<dq)or(dq<0<dp):
   t=dp/(dp-dq);out.append(tuple(p[k]+t*(q[k]-p[k])for k in range(3)))
 return clean(out)
def rect(poly,bb):
 x0,z0,x1,z1=map(F,bb)
 for plane in [(1,0,-x0),(0,1,-z0),(-1,0,x1),(0,-1,z1)]:poly=clip(poly,plane)
 return poly

def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def parent_clip(poly,t):
 p=[(v[0],v[2])for v in t];area=cross2((p[1][0]-p[0][0],p[1][1]-p[0][1]),(p[2][0]-p[0][0],p[2][1]-p[0][1]));assert area
 if area<0:p=p[::-1]
 for a,b in zip(p,p[1:]+p[:1]):
  dx,dz=b[0]-a[0],b[1]-a[1];poly=clip(poly,(-dz,dx,dz*a[0]-dx*a[1]))
 return poly

def fan(poly):return [(poly[0],poly[i],poly[i+1])for i in range(1,len(poly)-1)]if len(poly)>=3 else []
def intrinsic_area(poly,axis):
 axes=[k for k in range(3)if k!=axis]
 return abs(sum(p[axes[0]]*q[axes[1]]-q[axes[0]]*p[axes[1]]for p,q in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>=3 else F(0)
def plane_height(t,p):
 a,b,c=t;u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)];n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]
 return a[1]-(n[0]*(p[0]-a[0])+n[2]*(p[2]-a[2]))/n[1]
def alpha_branches(poly,bb,width):
 x0,z0,x1,z1=map(F,bb);w=F(width);assert w>0
 terms=[(1/w,0,-x0/w),(-1/w,0,x1/w),(0,1/w,-z0/w),(0,-1/w,z1/w),(0,0,F(1))]
 for i,a in enumerate(terms):
  part=poly
  for j,b in enumerate(terms):
   if i==j:continue
   part=clip(part,tuple(b[k]-a[k]for k in range(3)))
   if not part:break
  if not part:continue
  # Closed branch ties are boundaries. A real vertical surface on a tie is
  # deterministically owned by the first branch, never duplicated as a skin.
  if any(j<i and all(sum((terms[j][k]-a[k])*v for k,v in enumerate((p[0],p[2],F(1))))==0 for p in part)for j in range(len(terms))):continue
  yield i,a,part

def f32(v):return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def bbox(triangles):
 q=np.asarray(triangles,dtype='<f8').reshape(-1,3);assert len(q)and np.isfinite(q).all()
 return [q.min(0).tolist(),q.max(0).tolist()]
def rendered_height(parent,k):
 override=parent.get('renderedElev',[]);a=override[k]if override else None;e=parent['elev'][k]
 assert math.isfinite(e)
 return F(a)if type(a)in(int,float)and math.isfinite(a)else F(max(1.2,e)if e>0 else -4)
def node(parent,c,r):
 g=parent['meta']['georef'];k=r*parent['w']+c
 return (F(g['bE'])+c*F(g['aE'])-ORIGIN[0],rendered_height(parent,k),ORIGIN[1]-F(g['bN'])-r*F(g['aN']))
def nominate_cells(own_bounds,parent,halo=20):
 assert own_bounds and halo==20;g=parent['meta']['georef'];assert g['aE']>0 and g['aN']<0 and F(g['aE'])==-F(g['aN'])
 lo=[min(F(b[0][k])for b in own_bounds)for k in range(3)];hi=[max(F(b[1][k])for b in own_bounds)for k in range(3)]
 c0=math.floor((lo[0]-halo+ORIGIN[0]-F(g['bE']))/F(g['aE']));c1=math.ceil((hi[0]+halo+ORIGIN[0]-F(g['bE']))/F(g['aE']))
 # Row orientation in the georeference is negative northing; source Z grows
 # with row. Derive from explicit node Z rather than assuming sign/order.
 rvalues=[(ORIGIN[1]-(lo[2]-halo)-F(g['bN']))/F(g['aN']),(ORIGIN[1]-(hi[2]+halo)-F(g['bN']))/F(g['aN'])]
 r0,r1=math.floor(min(rvalues)),math.ceil(max(rvalues))
 assert 0<=c0<c1<parent['w']and 0<=r0<r1<parent['h'],'proposed-domain-outside-parent'
 a=node(parent,c0,r0);b=node(parent,c1,r1);bb=[float(a[0]),float(a[2]),float(b[0]),float(b[2])]
 assert bb[0]<bb[2]and bb[1]<bb[3]
 core=[bb[0]+10,bb[1]+10,bb[2]-10,bb[3]-10]
 assert all(F(core[0])<=F(v[0][0])<=F(v[1][0])<=F(core[2])and F(core[1])<=F(v[0][2])<=F(v[1][2])<=F(core[3])for v in own_bounds),'complete-source-outside-proposed-core'
 return [c0,r0,c1,r1],bb,core

def parent_faces(parent,cells):
 c0,r0,c1,r1=cells;out=[]
 for r in range(r0,r1):
  for c in range(c0,c1):
   a,b,d,e=node(parent,c,r),node(parent,c+1,r),node(parent,c,r+1),node(parent,c+1,r+1)
   out.extend([(a,b,d),(b,e,d)])
 return out

def sample_parent(parent,x,z,*,rendered):
 g=parent['meta']['georef'];c=(F(x)+ORIGIN[0]-F(g['bE']))/F(g['aE']);r=(ORIGIN[1]-F(z)-F(g['bN']))/F(g['aN']);i=min(parent['w']-2,max(0,math.floor(c)));j=min(parent['h']-2,max(0,math.floor(r)));u,v=c-i,r-j
 def at(k):return rendered_height(parent,k)if rendered else F(parent['elev'][k])
 a,b,d,e=(at(k)for k in (j*parent['w']+i,j*parent['w']+i+1,(j+1)*parent['w']+i,(j+1)*parent['w']+i+1))
 return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)

def refined_parent_grid(parent,cells,bb):
 pg=parent['meta']['georef'];step=min(F(5),F(pg['aE'])/5);assert 0<step<F(pg['aE'])
 width=(F(bb[2])-F(bb[0]))/step;height=(F(bb[3])-F(bb[1]))/step;assert width.denominator==height.denominator==1
 w,h=int(width)+1,int(height)+1;points=[];raw=[];display=[];vegetation=[]
 for r in range(h):
  for c in range(w):
   x,z=F(bb[0])+c*step,F(bb[1])+r*step;y=sample_parent(parent,x,z,rendered=True);points.append((x,y,z));raw.append(float(sample_parent(parent,x,z,rendered=False)));display.append(float(y))
   cc=min(parent['w']-1,max(0,round((x+ORIGIN[0]-F(pg['bE']))/F(pg['aE']))));rr=min(parent['h']-1,max(0,round((ORIGIN[1]-z-F(pg['bN']))/F(pg['aN']))));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
 return step,w,h,points,raw,display,vegetation

def closed_xz_touch(a,b):return a[0]<=b[2]and b[0]<=a[2]and a[1]<=b[3]and b[1]<=a[3]
def terrain_bounds(data):
 g=data['meta']['georef'];x=float(F(g['bE'])-ORIGIN[0]);z=float(ORIGIN[1]-F(g['bN']));x1=float(F(x)+(data['w']-1)*F(g['aE']));z1=float(F(z)-(data['h']-1)*F(g['aN']))
 bb=[min(x,x1),min(z,z1),max(x,x1),max(z,z1)]
 mesh=data.get('nativeMesh')
 if mesh:
  positions=np.asarray(mesh['position'],dtype=np.float32).astype(np.float64).reshape(-1,3);assert len(positions)and np.isfinite(positions).all()
  bb=[min(bb[0],float(positions[:,0].min())),min(bb[1],float(positions[:,2].min())),max(bb[2],float(positions[:,0].max())),max(bb[3],float(positions[:,2].max()))]
 return bb
def parent_child_obligations(bb,patches):
 return [dict(path=p['path'],sha256=p['sha256'],jsonPointer=p['jsonPointer'],targetUids=p['data']['meta'].get('targetUids',[]),wholePatchBounds=terrain_bounds(p['data']),closedIntersectionOrTouch=True,requiresBoundedParentChildPreservation=True)for p in patches if closed_xz_touch(bb,terrain_bounds(p['data']))]

def nominate_natives(domain_bounds,inventory):
 assert inventory['completeNativeActors']==inventory['successfullyCapturedActors']==6649 and not inventory['errors']
 rows=inventory['rows'];assert len(rows)==len({r['uid']for r in rows})==6649
 out=[];excluded=[];fields={'providerOriginal':'originalWholeSourceBounds','actualLiteral':'completeLiteralBounds','explicitLeftAssociatedF32ModelMatrix':'completeLeftAssociatedF32Bounds','explicitBalancedF32ModelMatrix':'completeBalancedF32Bounds'}
 for r in rows:
  assert r['sourceFacesOmitted']==0 and r['wholeUnusedPositionVerticesIncluded']is True and r['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']is True
  assert r['actualRenderMeshes']and all(m['wholePositionVerticesIncludingUnused']for m in r['actualRenderMeshes'])
  assert sum(m['completePositionVertices']for m in r['actualRenderMeshes'])==r['completePositionVertices']
  assert sum(m['completeIndexedFaces']for m in r['actualRenderMeshes'])==r['completeFaces']
  proofs=[];overlaps=[]
  for mode,key in fields.items():
   bounds=r['completeOriginalPOSITIONProof'][key]if mode=='providerOriginal'else r[key]
   assert len(bounds)==2 and all(len(v)==3 and all(type(x)in(int,float)and math.isfinite(x)for x in v)for v in bounds)
   if mode!='providerOriginal':assert bounds==[[min(m[key][0][k]for m in r['actualRenderMeshes'])for k in range(3)],[max(m[key][1][k]for m in r['actualRenderMeshes'])for k in range(3)]]
   gap=None
   for axis in [0,2]:
    if F(domain_bounds[1][axis])<F(bounds[0][axis]):gap=dict(axis=axis,exactGapM=str(F(bounds[0][axis])-F(domain_bounds[1][axis])));break
    if F(bounds[1][axis])<F(domain_bounds[0][axis]):gap=dict(axis=axis,exactGapM=str(F(domain_bounds[0][axis])-F(bounds[1][axis])));break
   if gap is None:overlaps.append(mode)
   else:proofs.append(dict(arithmetic=mode,**gap))
  item=dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],completeActualRow=r,allUnusedPOSITION=True,sourceOrLegacyApprovalTransferred=False)
  if overlaps:out.append(dict(**item,touchingArithmeticModes=overlaps,completeCurrentFourStreamBeforeAfterFiniteRequired=True))
  else:excluded.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],all4StrictPositiveBoundsGaps=proofs))
 return dict(nominated=out,excluded=excluded,completeActorsAccounted=6649,touchesAreFullObligations=True,physicalAccepted=False)

def construct(whole,parent,cells,bb,core,*,expected_sha256,expected_count=774477,triangle_budget=25000):
 whole=np.asarray(whole,dtype='<f8');assert whole.shape==(expected_count,3,3)and np.isfinite(whole).all()and hashlib.sha256(whole.tobytes()).hexdigest()==expected_sha256
 assert triangle_budget==25000 and core==[bb[0]+10,bb[1]+10,bb[2]-10,bb[3]-10]
 parents=parent_faces(parent,cells);pb=[[min(t[k][0]for k in range(3)),min(t[k][2]for k in range(3)),max(t[k][0]for k in range(3)),max(t[k][2]for k in range(3))]for t in parents]
 regions=[('source-core',core),('changed-transition',[bb[0],bb[1],bb[2],core[1]]),('changed-transition',[bb[0],core[3],bb[2],bb[3]]),('changed-transition',[bb[0],core[1],core[0],core[3]]),('changed-transition',[core[2],core[1],bb[2],core[3]])]
 zero=[];vertical=[];outside=[];touch_only=[];account=[];faces=[];lineage=[];collapsed=[];changed_core=[]
 for source_id,tri in enumerate(whole):
  original=tuple(map(point,tri));n=normal(tri);iszero=not any(n)
  if iszero:zero.append(source_id)
  elif n[1]==0:vertical.append(source_id)
  tb=[float(tri[:,0].min()),float(tri[:,2].min()),float(tri[:,0].max()),float(tri[:,2].max())]
  if not closed_xz_touch(tb,bb):outside.append(source_id);continue
  if iszero:
   account.append(dict(globalOriginalFacetId=source_id,sourceKind='exact-zero-area',originalTriangle=tri.tolist(),renderCoverageOrBridgeCredit=False));continue
  axis=max(range(3),key=lambda k:abs(n[k]));domain_poly=rect(list(original),bb);required=intrinsic_area(domain_poly,axis)
  if not required:touch_only.append(source_id);account.append(dict(globalOriginalFacetId=source_id,sourceKind='domain-boundary-touch-only',exactClippedSourcePoints=[[str(v)for v in p]for p in domain_poly],renderCoverageOrBridgeCredit=False));continue
  seen={};covered=F(0);first=len(faces)
  def emit(source_triangle,render_triangle,kind,parent_id=None,branch_id=None):
   nonlocal covered
   key=tuple(sorted(source_triangle));value=tuple(render_triangle);canonical_value=tuple(sorted(zip(source_triangle,value)))
   if key in seen:assert seen[key]==canonical_value,'nonconforming-identical-source-fragment';return
   seen[key]=canonical_value;covered+=intrinsic_area(list(source_triangle),axis)
   out=[[f32(v)for v in p]for p in value];index=len(faces);faces.append(out)
   if not area_real(out):collapsed.append(index)
   if kind=='source-core'and out!=[[float(v)for v in p]for p in source_triangle]:changed_core.append(index)
   lineage.append(dict(outputFacet=index,globalOriginalFacetId=source_id,classification=kind,parentFacet=parent_id,alphaBranch=branch_id,exactOriginalSourceFragment=[[str(v)for v in p]for p in source_triangle],exactProposedFragment=[[str(v)for v in p]for p in value],packedOriginalRealAreaCollapsed=not area_real(out)))
  for kind,region in regions:
   polygon=rect(list(original),region)
   if not polygon:continue
   if kind=='source-core':
    for piece in fan(polygon):
     if intrinsic_area(list(piece),axis):emit(piece,piece,kind)
    continue
   bounds=[min(p[0]for p in polygon),min(p[2]for p in polygon),max(p[0]for p in polygon),max(p[2]for p in polygon)]
   for parent_id,pt in enumerate(parents):
    if not closed_xz_touch(bounds,pb[parent_id]):continue
    clipped=parent_clip(polygon,pt)
    for branch_id,alpha,part in alpha_branches(clipped,bb,10):
     for piece in fan(part):
      if not intrinsic_area(list(piece),axis):continue
      changed=[]
      for p in piece:
       a=alpha[0]*p[0]+alpha[1]*p[2]+alpha[2];assert 0<=a<=1
       changed.append((p[0],a*p[1]+(1-a)*plane_height(pt,p),p[2]))
      emit(piece,changed,kind,parent_id,branch_id)
  assert covered==required,('incomplete-original-source-domain-partition',source_id,str(covered),str(required))
  account.append(dict(globalOriginalFacetId=source_id,sourceKind='vertical-real-area'if n[1]==0 else'real-area',outputFacetStart=first,outputFacetEndExclusive=len(faces),exactIntrinsicClippedArea=str(required),exactIntrinsicAccountedArea=str(covered),wholeDomainSourcePartitionComplete=True))
 assert len(outside)+len(account)==expected_count and set(outside)|{q['globalOriginalFacetId']for q in account}==set(range(expected_count))
 assert faces,'no-source-terrain-in-proposed-domain'
 step,w,h,nodes,raw,display,vegetation=refined_parent_grid(parent,cells,bb)
 domain=bbox([*faces,*[[[float(v)for v in p]]*3 for p in nodes]])
 mesh=dict(position=[v for t in faces for p in t for v in p],index=list(range(3*len(faces))),source=dict(verticalDatum='HKPD',verticalScale=1,policy='Exact dyadic source clipping and explicitly changed parent transition; Float32 packing differences retained.',completeInputFacets=expected_count,completeInputSHA256=expected_sha256))
 patch=dict(id='government-native-southside-pair-private-v1',w=w,h=h,cell=float(step),elev=raw,renderedElev=display,vegetation=vegetation,coarseCells=cells,meta=dict(georef=dict(aE=float(step),aN=-float(step),bE=bb[0]+ORIGIN[0],bN=ORIGIN[1]-bb[1],W=w,H=h),targetUids=['landsd/315025:0','landsd/300867:0']),nativeMesh=mesh)
 return patch,dict(completeInputFacets=expected_count,completeInputSHA256=expected_sha256,exactZeroOriginalFacetIds=zero,allVerticalRealOriginalFacetIds=vertical,allOutsideAlteredDomainOriginalFacetIds=outside,allBoundaryTouchOnlyOriginalFacetIds=touch_only,completeSelectedOriginalFacetAccounts=account,completeOutputFacetLineage=lineage,realOutputFacetsCollapsedByFloat32=collapsed,sourceCoreOutputsChangedByFloat32Packing=changed_core,wholeAlteredDomainAllPackedAndUnusedGridBounds=domain,triangleBudget=triangle_budget,triangleBudgetPass=len(faces)<=triangle_budget,completeFiniteSeamCoverageAndSamplerQualificationPending=True,sourceRoleAccepted=False,physicalAccepted=False,installationApproved=False,terrainExplicitlyChanged=True)


def blocked_inventory(whole,*,expected_sha256):
 whole=np.asarray(whole,dtype='<f8');assert whole.shape==(774477,3,3)and np.isfinite(whole).all()and hashlib.sha256(whole.tobytes()).hexdigest()==expected_sha256
 zero=[];vertical=[]
 for i,t in enumerate(whole):
  n=normal(t)
  if not any(n):zero.append(i)
  elif n[1]==0:vertical.append(i)
 return dict(completeInputFacets=774477,completeInputSHA256=expected_sha256,exactZeroOriginalFacetIds=zero,allVerticalRealOriginalFacetIds=vertical,all774477OriginalFacetIdsRetained=True,noCandidateBuilt=True,noRenderCoverageOrRootCredit=True)
