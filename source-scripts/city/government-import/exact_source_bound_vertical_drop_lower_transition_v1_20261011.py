"""DRAFT two-wall source-step collar, exact finite branches and drawn contacts only."""
from fractions import Fraction as F
from exact_branch_aware_rendered_nodes_seams_v1_20261011 import actual_point,whole_rendered_seam
from exact_faithful_source_step_junction_feasibility_v2_20261011 import native_footprints,native_query_inventory,project
from exact_finite_original_core_max_preservation_v1_20261011 import added_native_core_max,closed_piece_coverage
from exact_compute_transition_mesh_v1_20261011 import height
from exact_original_shell_intersections_20261009 import intersection_points,cross,sub,dot
from exact_faithful_multisurface_transition_domain_v1_20261011 import closed_pairs

def lower_endpoint(native,p):
 p=tuple(map(F,p));q=(p[0],p[2]);inventory=native_query_inventory(native,q);lower=[]
 for i in inventory['allIndexedFiniteOwners']:
  y=height(native['tri'][i],q)
  if y<p[1]:lower.append(dict(originalFace=i,exactFiniteLowerHeight=y))
 if not lower:return dict(qualified=False,reason='No genuine finite original lower branch at unchanged source endpoint',completeEndpointInventory=inventory,allStrictlyLowerOriginalBranches=[])
 y=max(r['exactFiniteLowerHeight']for r in lower);point=(p[0],y,p[2]);actual=actual_point(point);ids=[r['originalFace']for r in lower if r['exactFiniteLowerHeight']==y];exact_incidence=actual[0]==p[0]and actual[2]==p[2]and all(height(native['tri'][i],q)==actual[1]for i in ids)
 return dict(qualified=exact_incidence,completeEndpointInventory=inventory,allStrictlyLowerOriginalBranches=lower,selectedHighestGenuineLowerOriginalOwners=ids,exactLowerPoint=point,actualFloat32LowerPoint=actual,noSourceHeightOrXZSnap=True,actualCastRetainsExactFiniteLowerPlaneIncidence=exact_incidence,reason=None if exact_incidence else 'Ordinary Float32 lower encoding leaves genuine original plane; no snap')

def strict_inside(p,t):
 n=cross(sub(t[1],t[0]),sub(t[2],t[0]));return all(dot(cross(sub(b,a),sub(p,a)),n)>0 for a,b in zip(t,t[1:]+t[:1]))
def contacts(source,generated):
 src=native_footprints(source);new=native_footprints(generated);rows=[];allnominees=[]
 for gi,t in enumerate(new['tri']):
  ids,proof=src['ground'].select(t);allnominees.append(dict(generatedFace=gi,completeClosedXZNominees=[int(i)for i in ids],completeClosedAABBProof=proof))
  for i in map(int,ids):
   s=src['tri'][i];points=sorted(intersection_points(s,t))
   if not points:continue
   ns=cross(sub(s[1],s[0]),sub(s[2],s[0]));coplanar=all(dot(ns,sub(p,s[0]))==0 for p in t);dimension=0 if len(points)==1 else(2 if any(any(cross(sub(p,points[0]),sub(q,points[0])))for p in points[1:]for q in points[1:])else 1);mid=tuple(sum(p[k]for p in points)/len(points)for k in range(3));rows.append(dict(generatedFace=gi,originalFace=i,exactFiniteIntersectionPoints=points,intersectionDimension=dimension,coplanar=coplanar,properNoncoplanarInteriorSegment=dimension==1 and not coplanar and strict_inside(mid,s)and strict_inside(mid,t),contactNotAutomaticallyQualified=True))
 return dict(allCompleteGeneratedOriginalContactNominations=allnominees,allFiniteOriginalGeneratedContacts=rows,notSolidCollisionOrApproval=True)

def domain_proof(generated,domain):
 n=native_footprints(generated);rows=[];literal=[]
 for i,t in enumerate(generated):
  p=project(t);ids=sorted({j for _,j in closed_pairs([p],domain)});proof=closed_piece_coverage(p,[domain[j]for j in ids]);literal.append(dict(generatedFace=i,completeClosedDomainPieceNominations=ids,completeClosedDomainCoverage=proof))
 for i,p in enumerate(n['polys']):
  ids=sorted({j for _,j in closed_pairs([p],domain)});proof=closed_piece_coverage(p,[domain[j]for j in ids]);rows.append(dict(generatedFace=i,completeClosedDomainPieceNominations=ids,completeClosedDomainCoverage=proof))
 return dict(allLiteralWholeDomainCoverage=literal,allActualFloat32WholeDomainCoverage=rows,wholeGeneratedClosedProjectionWithinDomain=all(r['completeClosedDomainCoverage']['wholeFiniteCovered']for r in rows+literal))

def nominate(source,a,b,q,outer_anchor,domain):
 a,b=actual_point(a),actual_point(b);q=tuple(map(F,q));outer=tuple(map(F,outer_anchor));assert len(q)==2 and len(outer)==3 and a!=b;native=native_footprints(source);bottom=[lower_endpoint(native,p)for p in[a,b]];out=dict(allExactGenuineLowerEndpointProofs=bottom,sourceOriginalEndpoints=[a,b],noCandidate=True,sourceGeometryChanges=0,notEngineeringSupport=True)
 if not all(p['qualified']for p in bottom):out.update(localFeasibility=False,reason='Missing or unencodable exact finite lower endpoint');return out
 lo_a,lo_b=[p['actualFloat32LowerPoint']for p in bottom];assert lo_a[1]<a[1]and lo_b[1]<b[1];s=((a[0]+b[0])/2,(a[2]+b[2])/2);yi=(lo_a[1]+lo_b[1])/2;di=sum((q[k]-s[k])**2 for k in[0,1]);do=sum((q[k]-outer[(0,2)[k]])**2 for k in[0,1]);assert di+do>0;y=(do*yi+di*outer[1])/(di+do);tq=(q[0],y,q[1]);generated=[[b,a,lo_a],[b,lo_a,lo_b],[lo_b,lo_a,tq]];actual=native_footprints(generated);assert all(any(cross(sub(t[1],t[0]),sub(t[2],t[0])))for t in actual['tri']),'Degenerate actual generated facet';walls=actual['indexed'][:2];wallzero=walls==[False,False]and all(v==0 for v in actual['determinants'][:2]);seams=dict(wholeCopiedHighSourceEdge=whole_rendered_seam(a,b,[(b,a)]),wholeWallInternalDiagonal=whole_rendered_seam(b,lo_a,[(lo_a,b)]),wholeWallToLowerTransitionEdge=whole_rendered_seam(lo_a,lo_b,[(lo_b,lo_a)]));maxproof=added_native_core_max(source,generated);contained=domain_proof(generated,domain);finite=contacts(source,generated);newpairs=[]
 for i in range(3):
  for j in range(i):
   pair=contacts([generated[j]],[generated[i]]);newpairs.append(dict(generatedFaces=[j,i],allFiniteContactAttribution=pair))
 out.update(allCompleteGeneratedPairContactAttribution=newpairs,allComputeOnlyLiteralFacets=generated,allActualFloat32Facets=actual['tri'],exactConvexLowerAndCurrentWeights=[do/(di+do),di/(di+do)],genuineFiniteCurrentOuterAnchor=outer,allActualNativeIndexExclusions=[i for i,v in enumerate(actual['indexed'])if not v],actualZeroProjectedWallAndNativeExclusion=wallzero,allWholeActualCopiedAndInternalSeams=seams,completeClosedCoreMAXProof=maxproof,completeClosedActualDomainProof=contained,completeNewOriginalFiniteContactAttribution=finite,allNewContactsAndUnpairedTerminationsStillUnqualified=True,localFeasibility=wallzero and all(v['wholeFiniteRenderedSeamCovered']for v in seams.values())and maxproof['wholeOriginalClosedCoreMAXPreserved']and contained['wholeGeneratedClosedProjectionWithinDomain'],qualification='Necessary two-wall/lower-band feasibility only. Contacts retained unqualified; all complete candidate/global actor/runtime/production winding gates remain. No original cuts, snap, inferred engineering support, source deletion or overlap waiver.');return out
