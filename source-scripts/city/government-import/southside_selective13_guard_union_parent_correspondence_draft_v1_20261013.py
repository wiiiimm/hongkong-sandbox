"""UNEXECUTED selective13 core preparation; exact closed union/parent correspondence.
No collar/terrain construction, current runtime or source-role credit.
"""
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
from exact_original_projection_coverage_v2_20261010 import exact_coverage,signed_area
from southside_saved_local_core_parent_adapter_v3_20261012 import split,normal,tri_planes,bb,old

CONFLICT_UIDS={'landsd/311760:0','landsd/315028:0','landsd/330243:0'}
def complete_union_atoms(domains_by_uid):
 assert len(domains_by_uid)==13 and not(set(domains_by_uid)&CONFLICT_UIDS)
 atoms={};all_records=[];degenerate=[]
 for uid,domains in sorted(domains_by_uid.items()):
  assert domains and len({d['domainID']for d in domains})==len(domains)
  for d in domains:
   xz=[tuple(F(v)for v in p)for p in d['completeXZPoints']];assert xz and all(len(p)==2 for p in xz)
   lineage=dict(uid=uid,domainID=d['domainID'],domainKind=d['domainKind'],completeXZPoints=[[str(v)for v in p]for p in xz]);all_records.append(lineage)
   area=signed_area(xz)
   if not area:degenerate.append(lineage);continue
   assert len(xz)==3
   if area<0:xz.reverse()
   key=tuple(sorted(xz));atoms.setdefault(key,dict(exactCCWPoints=xz,completeOriginalDomainLineage=[]))['completeOriginalDomainLineage'].append(lineage)
 assert atoms
 return dict(atoms=list(atoms.values()),completeRawDomainRecords=all_records,completeDegenerateDomainRecords=degenerate,exactIdenticalUnionAtomReuseOnly=True,noBuildingOrTerrainFacetsMerged=True)

def parent_plane_correspondence(saved_ground,current_baseline):
 saved=np.asarray(saved_ground,dtype='<f8');current=np.asarray(current_baseline,dtype='<f8')
 assert saved.ndim==current.ndim==3 and saved.shape[1:]==current.shape[1:]==(3,3)and np.isfinite(saved).all()and np.isfinite(current).all()
 canonical=lambda t:tuple(sorted(tuple(F(float(v))for v in p)for p in t));lookup=defaultdict(list)
 for i,t in enumerate(current):lookup[canonical(t)].append(i)
 matches=[lookup[canonical(t)]for t in saved];assert all(len(m)==1 for m in matches)
 return dict(uniqueActualBaselineFacetBySavedGroundFacet=[m[0]for m in matches],wholeVertexTripleEquality=True,noPlaneFitting=True,noRuntimeCredit=True)

def complete_closed_parent_coverage(union,current_baseline):
 baseline=np.asarray(current_baseline,dtype='<f8');rows=[]
 # Inputs are original literal double domain coordinates. No derived rational
 # intersection is rounded before the existing exact coverage kernel.
 for d in union['completeRawDomainRecords']:
  ps=[[F(v)for v in p]for p in d['completeXZPoints']];assert 1<=len(ps)<=3
  ps=ps+[ps[-1]]*(3-len(ps));face=np.asarray([[float(x),0,float(z)]for x,z in ps],dtype='<f8')
  assert all(F(float(face[i,k]))==ps[i][j]for i in range(3)for k,j in [(0,0),(2,1)])
  proof=exact_coverage(face,baseline);rows.append(dict(uid=d['uid'],domainID=d['domainID'],proof=proof))
 assert len(rows)==len(union['completeRawDomainRecords'])
 return dict(completePrimitiveProofs=rows,allClosedPrimitivesCovered=all(r['proof']['exactProjectionCovered']for r in rows),pointsSegmentsAndAreasAllRetained=True,terrainConstruction=False)

def partition_original_surface_by_union(face,union):
 """Original 3D surface partition only. No height change or collar generation."""
 polygon=[tuple(F(v)for v in p)for p in face];assert len(polygon)==3
 n=normal(polygon)
 if not any(n):return dict(originalCollapsedFacetVerbatim=[[str(v)for v in p]for p in polygon],descriptorOnlyNoSurfaceCredit=True,allUnionAtomsRetained=True)
 axis=max(range(3),key=lambda k:abs(n[k]));whole=old.intrinsic_area(polygon,axis);remaining=[polygon];inside=[]
 for atom_id,atom in enumerate(union['atoms']):
  t=[(x,F(0),z)for x,z in atom['exactCCWPoints']];following=[]
  for p in remaining:
   if not old.closed_xz_touch(bb(p),bb(t)):following.append(p);continue
   cut,outside=split(p,tri_planes(t),axis);following.extend(outside)
   if old.intrinsic_area(cut,axis):inside.append(dict(atom=atom_id,exactOriginalSourcePoints=cut))
  remaining=following
 inside_area=sum((old.intrinsic_area(r['exactOriginalSourcePoints'],axis)for r in inside),F(0));outside_area=sum((old.intrinsic_area(p,axis)for p in remaining),F(0));assert inside_area+outside_area==whole
 return dict(exactWholeIntrinsicArea=str(whole),exactInsideUnionIntrinsicArea=str(inside_area),exactOutsideUnionIntrinsicArea=str(outside_area),completeInsideOriginalPieces=[dict(atom=r['atom'],points=[[str(v)for v in p]for p in r['exactOriginalSourcePoints']])for r in inside],completeOutsideOriginalPieces=[[[str(v)for v in p]for p in q]for q in remaining],whole3DPartitionComplete=True,sourceHeightOrPoseChanges=0,closedDomainTouchCannotInventRealArea=True,noRootOrAcceptanceCredit=True)
