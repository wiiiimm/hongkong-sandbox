"""Named six original roof-edge identity proposal with complete current 12-actor scope.

Distinct Silvercord stays a full physical foreign actor. Only these exact six
source-owned roof records have a proposed shared-boundary identity role; every
other source face stays in the unchanged foreign-area calculation. No source
record is omitted from geometry, collision, terrain, runtime or support checks.
Complete current provenance/raw full-cell bindings remain a separate gate.
"""
from datetime import datetime,timezone
import numpy as np
import shapely
from run import digest
from exact_mesh_components import face_components
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from no1_garden_original_overhead_roof_edge_identity_20261010 import polygon,primary_polygon
OWN='landsd/231645:0';FOREIGN='landsd/233997:0';TOWER='landsd/239465:0'
OWN_SHA='cfe390f024ac815a8c8ae3f422724fd72e4cd5c164e7325f9404cd81fc1b46da'
FOREIGN_SHA='11b03482304ea9f139e6863d259891f06aecc5def1df2e18abd921e0a0aebc5d'
OWN_WORLD='208fa1dbc15e358584b0d81389b5afe6222997a4f3e2ed72106cc52b14363bd0'
FOREIGN_WORLD='ca03c51e5b14030a6671f691b92fad931cce781a0a0a06c35bbbba66a17c815e'
EXPECTED={OWN:('3551417531P20050812',1108247418,'Podium'),FOREIGN:('3550417624P20050812',1108247395,'Podium'),TOWER:('3551817554T20050430',1108244114,'Tower')}
ROLE_FACES={11813,11814,11815,11821,11839,11840}
CURRENT_UIDS={'landsd/156599:0','landsd/234188:0','landsd/239032:0','landsd/208070:0','landsd/208602:0','landsd/211439:0',OWN,FOREIGN,'landsd/237843:0',TOWER,'landsd/250891:0','landsd/250893:0'}
def source_proof(own_raw,foreign_raw,current_forms,primary,role_faces=ROLE_FACES):
 assert digest(own_raw)==OWN_SHA and digest(foreign_raw)==FOREIGN_SHA,'Original asset bytes changed'
 a=decode_original_world_triangles(own_raw);b=decode_original_world_triangles(foreign_raw)
 assert a.shape==(13725,3,3) and b.shape==(12258,3,3) and np.isfinite(a).all() and np.isfinite(b).all()
 assert digest(a.astype('<f8').tobytes())==OWN_WORLD and digest(b.astype('<f8').tobytes())==FOREIGN_WORLD,'Full original world/pose changed'
 assert set(role_faces)==ROLE_FACES,'Only the six named original roof records qualify'
 forms={v['uid']:v for v in current_forms};assert len(forms)==len(current_forms) and set(forms)==CURRENT_UIDS,'Complete twelve-actor current source-context census changed'
 assert len(primary)==3;providers={}
 for uid,(csuid,bid,typ) in EXPECTED.items():
  f=forms[uid];assert (f['buildingCSUID'],f['buildingId'],f['structureType'])==(csuid,bid,typ)
  matches=[p for p in primary if p['attributes']['BuildingCSUID']==csuid];assert len(matches)==1
  p=matches[0];v=p['attributes'];assert (v['Status'],v['BuildingID'],v['BuildingBlockType'],str(v['GeoRefNo']))==('Active',bid,typ,csuid[:10])
  assert datetime.fromtimestamp(v['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:]
  assert (v['BaseHeight'],v['TopHeight'])==(f['baseHeightHKPD'],f['topHeightHKPD']);providers[uid]=p
 parts=face_components(a);assert len(parts)==12 and len(parts[0])==12299 and ROLE_FACES<=set(map(int,parts[0]))
 assert len(face_components(b))==44
 role=a[sorted(ROLE_FACES)];normal=np.cross(role[:,1]-role[:,0],role[:,2]-role[:,0]);assert (normal[:,1]>0).all() and (normal[:,[0,2]]==0).all()
 assert (role[:,:,1]==19.361640453338623).all(),'Exact unchanged horizontal source roof plane required'
 # This exact surface association is identity context only, not a supported
 # contact or a claim that either distinct building is load-bearing for the other.
 contacts=exact_finite_contacts(a,sorted(ROLE_FACES),b,range(len(b)))
 for face in ROLE_FACES:
  positive=[c for c in contacts['contacts'] if c['sourceFaceA']==face and c['dimension']>0]
  assert positive and all(c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in positive)
 polys=shapely.polygons(a[:,:,[0,2]]);whole=shapely.union_all(polys[shapely.area(polys)>0])
 ids=[i for i in range(len(a)) if i not in ROLE_FACES];remaining=shapely.union_all(polys[ids][shapely.area(polys[ids])>0])
 other_shapes=shapely.union_all([polygon(f['rings']) for uid,f in forms.items() if uid not in {OWN,FOREIGN}]);checks={}
 for label,target,named in [('current',polygon(forms[OWN]['rings']),polygon(forms[FOREIGN]['rings'])),('primary',primary_polygon(providers[OWN]),primary_polygon(providers[FOREIGN]))]:
  assert target.intersection(named).area==0,'Distinct provider/current footprints must have zero area intersection'
  shared=target.boundary.intersection(named.boundary);assert shared.length>0,'Independent exact common boundary required'
  full_extra=whole.difference(target);nonrole_extra=remaining.difference(target)
  # Keep FULL source projection for every other foreign actor. Recompute the
  # complete non-role projection for Silvercord; never subtract role-area from
  # the whole excess, which could accidentally mask coincident non-role walls.
  nonrole_named=nonrole_extra.intersection(named);ordinary_other=full_extra.intersection(other_shapes)
  effective=shapely.union_all([nonrole_named,ordinary_other])
  coverage=float(whole.intersection(target).area/target.area);extent=float(shapely.distance(shapely.points(a[:,:,[0,2]].reshape(-1,2)),target).max())
  assert .95<=coverage<=1.000000001 and extent<=10 and effective.area<=1,'Unchanged full-source spatial limits failed'
  assert full_extra.intersection(named).area>1,'Named original raw excess must remain documented'
  checks[label]=dict(fullTargetCoverage=coverage,fullMaximumSourceExtentM=extent,rawNamedForeignExcessM2=float(full_extra.intersection(named).area),allNonRoleNamedForeignExcessM2=float(nonrole_named.area),ordinaryAllOtherForeignExcessM2=float(ordinary_other.area),effectiveAllForeignExcessM2=float(effective.area),exactSharedBoundaryLengthM=float(shared.length),roleSourceFaceIDs=sorted(ROLE_FACES))
 return dict(sourceOnlyRoleProposalSupported=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,completeOriginalFaces=13725,completeOriginalParts=12,relatedDistinctOriginalFaces=12258,relatedDistinctOriginalParts=44,roleSourceFaceIDs=sorted(ROLE_FACES),completeOriginalSixRoofContactProof=contacts,independentSourceSpatialChecks=checks,allCurrentForeignActorsRetained=current_forms,foreignCollisionExemption=False,foreignTerrainExemption=False,commonOwnershipClaim=False,structuralSupportClaim=False,functionClaim=False,sourceFacesOmittedAtRuntime=0,sourceGeometryChanges=0,qualification='Source-only interpretation proposal for six exact mainbody-owned upward roof-edge faces continuously associated with the distinct original Silvercord upper boundary. All other own faces and all other actors retain ordinary foreign-area checks. Real raw excess remains; no current raw-preflight acceptance, common ownership, collision, support, terrain, source omission, tolerance change or installation credit.')
