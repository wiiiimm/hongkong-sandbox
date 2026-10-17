"""Proposed exact Lei Tung lower-platform/upper-commercial assembly identity.

This contract requires both complete original assets in the eventual runtime
assembly. It provides no standalone import, physical support or actor exemption.
The caller independently binds current/native/provider/scene/stream receipts.
"""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
import json,numpy as np,shapely
from run import digest
from source_closed_components import components
from exact_original_slab_projection_coverage_20261010 import slab_coverage
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_polygon_triangle_partition_20261010 import exact_partition
UID='landsd/254604:0';PLATFORM='landsd/126434:0'
SOURCE_SHA='584d51298a5394f6805284ff87c9d7b12796feac3dbe8950ff55549b1c0cb133'
PLATFORM_SHA='368ec3bcb2b011f8db942a2e294f500043762b15851e55113c95443a48ff5f15'
WORLD_SHA='fc346bef2e91446e1379ce403ca4305a06f3413fe76bb46cae8717debb4a02b3'
PLATFORM_WORLD_SHA='4ba251e37ac08ac9ae11ab967871f420fc8c7a97d8d577d5d7148740170ded6a'
EXPECTED={UID:('3417011358T20050430',1103139137,'Tower'),PLATFORM:('3417111358P20060312',1103119420,'Podium')}
RAW_REASONS={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
POLICY='proposed-exact-lei-tung-two-original-lower-platform-upper-commercial-identity-v1'
def polygon(rings):
 p=shapely.GeometryCollection()
 for r in rings:p=p.symmetric_difference(shapely.Polygon(r))
 assert p.is_valid and p.area>0
 return p

def provider_polygon(f):return polygon([[(x-834500,816500-y) for x,y in r] for r in f['geometry']['rings']])
def fraction_area(ring):return abs(sum(Fraction(float(a[0]))*Fraction(float(b[1]))-Fraction(float(a[1]))*Fraction(float(b[0])) for a,b in zip(ring,ring[1:]+ring[:1])))/2

def exact_missing_platform(missing,upward):
 parts=shapely.get_parts(missing);result=[]
 for p in parts:
  assert p.geom_type=='Polygon';rings=[list(p.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in p.interiors];area=fraction_area(rings[0])-sum(fraction_area(r) for r in rings[1:]);actual=Fraction(0);facets=[]
  for t in shapely.get_parts(shapely.constrained_delaunay_triangles(p)):
   v=np.asarray(t.exterior.coords)[:3];actual+=fraction_area(v.tolist());tri=np.column_stack([v[:,0],np.zeros(3),v[:,1]]);proof=slab_coverage(tri,upward);assert proof['exactProjectionCovered'],'A complete missing upper-target facet/edge is not covered by the original lower platform';facets.append({'literalProofTriangle':tri.tolist(),'exactFiniteCoverage':proof})
  partition=exact_partition(rings,[[[v[0],v[2]] for v in f['literalProofTriangle']] for f in facets]);assert actual==area,'Missing target finite area census differs';result.append({'completeMissingPolygonGeoJSON':json.loads(shapely.to_geojson(p)),'exactAreaFraction':str(area),'independentExactOrientedBoundaryPartition':partition,'completeFiniteFacets':facets})
 return result

def named_proof(previous,upper_row,platform_row,upper,platform,current_forms,primary):
 assert upper_row['uid']==UID and upper_row['modelId']=='B341701135801063C0' and upper_row['sourceSHA256']==SOURCE_SHA
 assert platform_row['uid']==PLATFORM and platform_row['modelId']=='B341711135802063C0' and platform_row['sourceSHA256']==PLATFORM_SHA
 assert previous['uid']==UID and previous['sourceSHA256']==SOURCE_SHA and previous['originalOwnership']['sourceGraphVerified']
 a=np.asarray(upper,float);b=np.asarray(platform,float);assert a.shape==(874,3,3) and b.shape==(432,3,3) and np.isfinite(a).all() and np.isfinite(b).all();assert digest(a.astype('<f8').tobytes())==WORLD_SHA and digest(b.astype('<f8').tobytes())==PLATFORM_WORLD_SHA
 forms={f['uid']:f for f in current_forms};assert len(forms)==len(current_forms) and {UID,PLATFORM}<=set(forms)
 assert forms[UID]==upper_row['source']['building'] and forms[PLATFORM]==platform_row['source']['building']
 assert forms[UID]['name']=='Lei Tung Commercial Centre (Ph.2)' and forms[PLATFORM]['name']=='LEI TUNG COMMERCIAL CENTRE'
 assert len(primary)==3 and len({p['attributes']['BuildingCSUID'] for p in primary})==3 and {p['attributes']['BuildingCSUID'] for p in primary}=={'3417011358T20050430','3417111358P20060312','3417311416T20050430'},'Complete exact primary family inventory must remain unique'
 providers={}
 for uid,(csuid,bid,kind) in EXPECTED.items():
  f=forms[uid];assert (f['buildingCSUID'],f['buildingId'],f['structureType'])==(csuid,bid,kind);matches=[p for p in primary if p['attributes']['BuildingCSUID']==csuid];assert len(matches)==1;p=matches[0];q=p['attributes'];providers[uid]=p
  assert (q['Status'],q['BuildingID'],q['BuildingBlockType'],str(q['GeoRefNo']))==('Active',bid,kind,csuid[:10]);assert datetime.fromtimestamp(q['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:];assert q['BaseHeight']==f['baseHeightHKPD'] and q['TopHeight']==f['topHeightHKPD']
 assert forms[PLATFORM]['topHeightHKPD']==forms[UID]['baseHeightHKPD']==62.4
 aparts=components(a)['components'];bparts=components(b)['components'];assert len(aparts)==19 and len(bparts)==3;body=bparts[2]['faceIndices'];assert len(body)==166
 normal=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);up=[i for i in body if normal[i,1]>0];assert up
 contacts=exact_component_contacts(a,range(len(a)),b,range(len(b)),maximum_pairs=1000000);positive=[c for c in contacts['contacts'] if c['dimension']>0];assert len(positive)==124
 own_projection=shapely.union_all(shapely.polygons(a[:,:,[0,2]]));pair=np.concatenate([a,b]);paired_projection=shapely.union_all(shapely.polygons(pair[:,:,[0,2]]));others=[f for f in current_forms if f['uid'] not in {UID,PLATFORM}];foreign=shapely.union_all([polygon(f['rings']) for f in others]);checks={};reasons=[r for r in previous['reasons'] if r not in RAW_REASONS]
 for label,upper_target,platform_target in [('current',polygon(forms[UID]['rings']),polygon(forms[PLATFORM]['rings'])),('primary',provider_polygon(providers[UID]),provider_polygon(providers[PLATFORM]))]:
  target=upper_target.union(platform_target);missing=upper_target.difference(own_projection);assert not missing.is_empty;suppliers=[i for i in up if shapely.Polygon(b[i][:,[0,2]]).intersection(missing).area>0];assert suppliers and all(forms[PLATFORM]['baseHeightHKPD']<b[i,:,1].min()<=b[i,:,1].max()<=forms[PLATFORM]['topHeightHKPD'] for i in suppliers),'Every supplying upward floor surface must lie within the exact lower-platform metadata span';finite=exact_missing_platform(missing,b[suppliers]);standalone=own_projection.intersection(upper_target).area/upper_target.area;assert .94<standalone<.95,'Raw upper standalone95% failure must remain explicit'
  if label=='current':assert missing.difference(platform_target).is_empty,'Every missing current upper region must lie on its exact named lower platform target'
  metrics={'rawStandaloneUpperCoverage':standalone,'wholePairedTargetCoverage':paired_projection.intersection(target).area/target.area,'wholePairedMaximumSourceExtentM':float(shapely.distance(shapely.points(pair[:,:,[0,2]].reshape(-1,2)),target).max()),'allOtherForeignExcessM2':paired_projection.difference(target).intersection(foreign).area,'rawUpperTargetOutsidePlatformM2':upper_target.difference(platform_target).area,'rawMissingUpperTargetAreaM2':missing.area,'rawMissingUpperOutsidePlatformM2':missing.difference(platform_target).area,'completeOriginalSupplyingUpwardPlatformFaceIds':suppliers,'completeMissingUpperOriginalPlatformFiniteProofs':finite};checks[label]=metrics
  if not(.95<=metrics['wholePairedTargetCoverage']<=1.000000001 and metrics['wholePairedMaximumSourceExtentM']<=10 and metrics['allOtherForeignExcessM2']<=1):reasons.append('complete-paired-'+label+'-spatial-bound')
 raw=sorted(set(previous['reasons'])&RAW_REASONS);assert raw
 out=deepcopy(previous);passed=not reasons;out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawStandaloneUpperCoverageReasonsRetained=raw,mandatoryOriginalRuntimeUIDs=[UID,PLATFORM],standaloneOriginalImportAccepted=False,completeOriginalFaceCounts=[874,432],completeOriginalPartCounts=[19,3],completeLowerPlatformPartFaceIds=body,completeOriginalPositiveInterfaces=positive,independentPairedCurrentProviderChecks=checks,completeCurrentForeignActorsRetained=current_forms,foreignCollisionExemption=False,foreignTerrainExemption=False,foreignRemoval=False,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},qualification='Proposed narrowly named mandatory-two-original lower-platform/upper-commercial assembly. Raw94.79% standalone upper source remains a failure; complete1306 original faces together must satisfy unchanged95%/10m/1m² current and provider paired targets. Every omitted upper region is exactly covered by upward original166-face lower platform part,124 original positive interfaces retained and all19+3 components remain. No commonOP/legal ownership, structural support, actor removal or physical exemption is claimed. Actual staging must include both verified unchanged originals.')
 return out
