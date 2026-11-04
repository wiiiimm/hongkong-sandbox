"""Named unchanged source-owned boundary strips, never ownership or physics.

Only the two explicit 2D unrelated-excess reasons may be interpreted. Every
original/current actor remains independent for collision, ground and support.
Current/native/provider/source provenance is the promotion adapter's separate
responsibility; this proposal by itself is not an import approval.
"""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import math
import numpy as np
import shapely
from run import digest
from exact_mesh_components import face_components
from exact_original_polygon_triangle_partition_20261010 import exact_partition
from exact_original_component_contacts_20261009 import exact_component_contacts
from no1_garden_original_overhead_roof_edge_identity_20261010 import polygon,primary_polygon

UID='landsd/79883:0'
FOREIGN=('landsd/12728:0','landsd/79882:0')
POLICY='exact-fung-yip-original-distinct-party-edge-identity-proposal-v1'
RAW_REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
EXPECTED={
 UID:('3214116472P20060312',1103117007,'B321411647202063C0',398,'f6034a6d28e0f7d82bc2094e9817ea253fe700695d3d228825ea794c5375b6d5','9a250e3151d3aabd03e14c3f16b3580a3585b11a0a6a153566559a8adb499b12',1492454,'H234/75'),
 FOREIGN[0]:('3217816493P20150615',1810143107,'B321781649302063C0',1655,'4f177100defad797c23530d4577676041bcbc6f6ee79de026f2af01c112552d2','de9d2b8aac972078d0e5855f729db40d76f290bca57f88036a80024eef9be0f0',6031099,'HK32/2015(OP)'),
 FOREIGN[1]:('3210716474P20060312',1103116996,'B321071647402063C0',616,'63636232e9518f29013db9a13431ad9e9d3bc143207dd350c7dd542cdca8bc9a','1d3a1f586b010d01a15fd7d6b90b44b69e4031d8ec197cb8913e5919c1051f18',325282,'H29/86')}
ROLE_FACES={FOREIGN[0]:{0,1,178,179,180,225,226,378},FOREIGN[1]:{17,18,19,20,64,166,168,170,171,172,173,174,175,176,177,219,220,221,222,332,335,336,353,355,356,372,375,387,392,394}}
NO_DIRECT_CONTACT={FOREIGN[0]:{378},FOREIGN[1]:{166,168,170,171,172,173,174,177,219,220,221,222,387}}
# These are narrow named-source adverse guards, not source padding/tolerances.
# Actual retained maximum distances are .069389 m and .004004 m. No projected
# portion is moved, enlarged or treated as zero; both raw areas remain explicit.
BOUNDARY_GUARDS={FOREIGN[0]:.07,FOREIGN[1]:.0041}
CONTACT_COUNTS={FOREIGN[0]:39,FOREIGN[1]:76}

def finite_chain_certificate(coords, chain, guard):
 # A connected finite polyline joins its literal endpoints. The continuous
 # projection along their chord contains every chord coordinate (IVT).
 # Every chain segment lies within delta of its finite chord by convexity.
 # Hence distance of any portion point to the actual chain is bounded by
 # distance to the finite chord + delta. Exact dyadic squared distances and
 # outward-rounded square roots certify the bound; no epsilon/gap credit.
 points=[tuple(Fraction(float(v))for v in q)for q in chain]
 a,b=points[0],points[-1];d=tuple(y-x for x,y in zip(a,b));length=sum(v*v for v in d)
 assert length>0
 def squared(q):
  q=tuple(Fraction(float(v))for v in q);t=sum((q[i]-a[i])*d[i]for i in range(2))/length
  t=max(Fraction(0),min(Fraction(1),t))
  return sum((q[i]-a[i]-t*d[i])**2 for i in range(2))
 def upper(value):
  f=math.sqrt(float(value))
  while Fraction(f)**2<value:f=math.nextafter(f,math.inf)
  return Fraction(f)
 delta2=max(squared(q)for q in chain);portion2=max(squared(q)for q in coords)
 delta,portion=upper(delta2),upper(portion2)
 if delta+portion>Fraction(float(guard)):
  # Sharper exact proof: partition the complete convex hull by the global
  # chord projections of every literal shared-chain vertex. Strict monotone
  # projections create adjacent closed slabs covering the entire hull. Each
  # slab's complete polygon is tested against its actual finite chain edge.
  # No straightened chain, gaps, rounded clipping or larger band is used.
  hull=np.asarray(shapely.MultiPoint(coords).convex_hull.exterior.coords)[:-1]
  poly=[tuple(Fraction(float(v))for v in q)for q in hull]
  project=lambda q:sum((q[k]-a[k])*d[k]for k in range(2))
  boundaries=[project(q)for q in points]
  if not all(x<y for x,y in zip(boundaries,boundaries[1:])):return None
  def clip(vertices,level,below):
   if not vertices:return []
   result=[]
   last=vertices[-1];lv=project(last)-level;inside=lambda v:v<=0 if below else v>=0
   for current in vertices:
    cv=project(current)-level
    if inside(cv)!=inside(lv):
     t=lv/(lv-cv);result.append(tuple(last[k]+t*(current[k]-last[k])for k in range(2)))
    if inside(cv):result.append(current)
    last,lv=current,cv
   return result
  records=[];maximum=Fraction(0)
  for i in range(len(points)-1):
   clipped=poly
   if i>0:clipped=clip(clipped,boundaries[i],False)
   if i<len(points)-2:clipped=clip(clipped,boundaries[i+1],True)
   if not clipped:continue
   aa,bb=points[i],points[i+1];dd=tuple(bb[k]-aa[k]for k in range(2));ll=sum(v*v for v in dd);assert ll>0
   def edge_squared(q):
    t=sum((q[k]-aa[k])*dd[k]for k in range(2))/ll;t=max(Fraction(0),min(Fraction(1),t))
    return sum((q[k]-aa[k]-t*dd[k])**2 for k in range(2))
   bound2=max(edge_squared(q)for q in clipped)
   if bound2>Fraction(float(guard))**2:return None
   maximum=max(maximum,upper(bound2));records.append(dict(literalEdgeIndex=i,exactCompleteClipVertices=[[str(v)for v in q]for q in clipped],exactMaximumFiniteEdgeDistanceSquared=str(bound2)))
  assert records
  return dict(literalFiniteChain=chain.tolist(),exactMonotoneSlabBoundaries=[str(v)for v in boundaries],closedAdjacentSlabsCoverWholeConvexHull=True,exactFiniteSlabCertificates=records,conservativeCompleteDistanceUpperM=float(maximum),exactConservativeCompleteDistanceUpper=str(maximum),completeFiniteChainProjectionContinuity=True)
 return dict(literalFiniteChain=chain.tolist(),exactMaximumChainChordDistanceSquared=str(delta2),
  exactMaximumPortionChordDistanceSquared=str(portion2),conservativeCompleteDistanceUpperM=float(delta+portion),
  exactConservativeCompleteDistanceUpper=str(delta+portion),completeFiniteChainProjectionContinuity=True)

def named_proof(previous,row,worlds,current_forms,primary,relations,structures):
 assert row['uid']==UID and row['modelId']==EXPECTED[UID][2] and row['sourceSHA256']==EXPECTED[UID][4]
 assert previous['uid']==UID and previous['sourceSHA256']==EXPECTED[UID][4]
 assert previous['originalOwnership']['sourceGraphVerified']
 assert set(worlds)==set(EXPECTED),'All three complete original sources required'
 triangles={}
 for u,v in worlds.items():
  t=np.asarray(v,float);e=EXPECTED[u]
  assert t.shape==(e[3],3,3) and np.isfinite(t).all()
  assert digest(t.astype('<f8').tobytes())==e[5],'Complete original world stream/pose differs'
  triangles[u]=t
 own=triangles[UID];parts=face_components(own)
 assert len(parts)==1 and len(parts[0])==398,'Whole source-authored mainbody must remain present'
 forms={b['uid']:b for b in current_forms};assert len(forms)==len(current_forms) and set(EXPECTED)<=set(forms)
 assert forms[UID]==row['source']['building'] and forms[UID]['name']=='FUNG YIP BUILDING'
 assert len(primary)==3 and len(relations)==3 and len(structures)==3
 providers={};provider_structures={s['attributes']['BuildingStructureID']:s['attributes']for s in structures}
 assert len(provider_structures)==3
 for u,e in EXPECTED.items():
  b=forms[u];assert (b['buildingCSUID'],b['buildingId'],b['structureType'])==(e[0],e[1],'Podium')
  matches=[p for p in primary if p['attributes']['BuildingCSUID']==e[0]];assert len(matches)==1
  p=matches[0];a=p['attributes'];providers[u]=p
  assert (a['Status'],a['BuildingID'],a['BuildingBlockType'],str(a['GeoRefNo']))==('Active',e[1],'Podium',e[0][:10])
  assert datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==e[0][11:]
  assert (a['BaseHeight'],a['TopHeight'])==(b['baseHeightHKPD'],b['topHeightHKPD'])
  rel=[r['attributes']for r in relations if r['attributes']['BuildingCSUID']==e[0]];assert len(rel)==1 and rel[0]['BuildingStructureID']==e[6]
  assert (provider_structures[e[6]]['OPNo'],provider_structures[e[6]]['OPBlockType'])==(e[7],'Podium')
 assert len({e[6]for e in EXPECTED.values()})==3 and len({e[7]for e in EXPECTED.values()})==3
 contacts={}
 for u in FOREIGN:
  c=exact_component_contacts(own,range(398),triangles[u],range(EXPECTED[u][3]))
  assert c['allPairsExamined'] and not c['geometryChanges']
  assert len(c['contacts'])==CONTACT_COUNTS[u] and all(x['dimension']>0 for x in c['contacts'])
  contacted={x['sourceFaceA']for x in c['contacts']}
  assert ROLE_FACES[u]-contacted==NO_DIRECT_CONTACT[u],'Whole named original interface census differs'
  contacts[u]=c
 projection=shapely.union_all(shapely.polygons(own[:,:,[0,2]]))
 other_forms=[b for b in current_forms if b['uid'] not in {UID,*FOREIGN}]
 other_shapes=shapely.union_all([polygon(b['rings'])for b in other_forms])
 reasons=[r for r in previous['reasons']if r not in RAW_REASONS];checks={}
 for label,target,foreign_shapes in [('current',polygon(forms[UID]['rings']),{u:polygon(forms[u]['rings'])for u in FOREIGN}),('primary',primary_polygon(providers[UID]),{u:primary_polygon(providers[u])for u in FOREIGN})]:
  extra=projection.difference(target);named={}
  for u,foreign in foreign_shapes.items():
   assert target.intersection(foreign).area==0,'Actual primary/current actor footprints must remain distinct'
   shared=target.boundary.intersection(foreign.boundary)
   assert 24<shared.length<26 and shared.is_simple,'Exact named finite primary/current shared edge required'
   overlap=extra.intersection(foreign);ids={i for i,t in enumerate(own)if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area>0}
   assert ids==ROLE_FACES[u],'Every nonzero named projected portion must retain its exact authored face role'
   maximum=0.;details=[]
   for i in sorted(ids):
    portion=shapely.Polygon(own[i][:,[0,2]]).intersection(overlap)
    coords=shapely.get_coordinates(portion);distance=float(shapely.distance(shapely.points(coords),shared).max())
    # A convex distance-to-chord bound applies to every point in the
    # complete clipped polygon's convex hull, even with holes/disconnections.
    # Chord projection continuity + exact dyadic chain deviation then bounds
    # distance to the actual finite shared boundary without changing it.
    merged=shapely.line_merge(shared)
    pieces=list(merged.geoms)if hasattr(merged,'geoms')else[merged]
    applicable=[]
    polygons=list(shapely.get_parts(portion))
    for polygon_part in polygons:
     assert polygon_part.geom_type=='Polygon' and polygon_part.area>0
     facets=list(shapely.get_parts(shapely.constrained_delaunay_triangles(polygon_part)))
     points=[np.asarray(f.exterior.coords)[:3]for f in facets]
     partition=exact_partition([np.asarray(polygon_part.exterior.coords),*[np.asarray(r.coords)for r in polygon_part.interiors]],points)
     facet_records=[]
     for facet in points:
      certificates=[]
      for edge in pieces:
       if edge.geom_type!='LineString':continue
       certificate=finite_chain_certificate(facet,np.asarray(edge.coords),BOUNDARY_GUARDS[u])
       if certificate:certificates.append(certificate)
      assert certificates,'Complete exact-partition projected facet not associated with finite shared chain within unchanged guard'
      best=min(certificates,key=lambda c:c['conservativeCompleteDistanceUpperM'])
      facet_records.append(dict(literalFacet=facet.tolist(),finiteChainCertificate=best))
     applicable.append(dict(exactCompleteBoundaryPartition=partition,completeFacetCertificates=facet_records,conservativeCompleteDistanceUpperM=max(f['finiteChainCertificate']['conservativeCompleteDistanceUpperM']for f in facet_records)))
    assert applicable,'Complete actual finite projected portion not associated with one exact shared edge'
    certified=max(x['conservativeCompleteDistanceUpperM']for x in applicable);maximum=max(maximum,certified)
    details.append(dict(face=i,rawNonzeroAreaM2=portion.area,originalYBounds=[float(own[i,:,1].min()),float(own[i,:,1].max())],finiteSharedSegmentCertificates=applicable))
   named[u]=dict(rawNamedForeignExcessM2=overlap.area,exactSharedBoundaryLengthM=shared.length,
     allOriginalExcessFaces=sorted(ids),completeFiniteBoundaryMaximumDistanceM=maximum,completeFinitePortionCertificates=details,
     originalFacesWithoutDirectForeignContactRetained=sorted(NO_DIRECT_CONTACT[u]))
  m=dict(targetCoverage=projection.intersection(target).area/target.area,
    maximumSourceExtentM=float(shapely.distance(shapely.points(own[:,:,[0,2]].reshape(-1,2)),target).max()),
    allOtherForeignExcessM2=extra.intersection(other_shapes).area,namedForeignBoundaryRoles=named)
  checks[label]=m
  if not(.95<=m['targetCoverage']<=1.000000001 and m['maximumSourceExtentM']<=10 and m['allOtherForeignExcessM2']<=1):reasons.append('complete-source-'+label+'-spatial-bound')
 raw=sorted(set(previous['reasons'])&RAW_REASONS);assert raw
 out=deepcopy(previous);passed=not reasons
 out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawUnrelatedOverlapReasonsRetained=raw,
  completeOriginalWorldVersions={u:EXPECTED[u][5]for u in EXPECTED},allOriginalPartFaceIds=[p.tolist()for p in parts],
  completeOriginalMutualInterfaces=contacts,independentFullSourceSpatialChecks=checks,
  completeCurrentForeignActorsRetained=current_forms,allOtherActorsStillForeignUIDs=sorted(b['uid']for b in other_forms),
  explicitNamedForeignUIDs=list(FOREIGN),allDistinctPrimaryPermitRolesRetained=True,noCommonOwnershipOrSupportClaim=True,
  foreignRemoval=False,foreignCollisionExemption=False,foreignTerrainExemption=False,
  proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
  physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,
  qualification='Named original mainbody boundary-strip identity proposal only. All398 own faces remain one unchanged component; both distinct original neighbour bodies and every raw2D excess remain. Exactly8+30 named original portions lie along the complete zero-area-intersecting primary/current shared edges;39+76 exact mutual surface contacts corroborate source context but grant no support credit. Fourteen non-direct-contact face roles remain explicit. Three distinct permits imply no shared ownership. Every foreign collision, terrain, foundation and runtime gate remains independent.')
 return out
