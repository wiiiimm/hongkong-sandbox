"""DRAFT unchanged original open-sided/Museum contact topology attribution.
Reuses complete frozen exact pairs; no new overlap tolerance, root or acceptance.
"""
from pathlib import Path
from fractions import Fraction
import json,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';C=B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011';A=B/'government-xl-science-museum-open-sided-original-gltf-members-acquisition-v1-20261011';BATCH='government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';DOC=B/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def relative_interior(face,point):
 normal=cross(sub(face[1],face[0]),sub(face[2],face[0]));assert any(normal)
 if dot(normal,sub(point,face[0]))!=0:return False
 return all(dot(normal,cross(sub(b,a),sub(point,a)))>0 for a,b in zip(face,face[1:]+face[:1]))
def main():
 assert not DOC.exists();d=read(C/'diagnostic.json.gz')
 for folder in [C,A]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 arr=C/'complete-original-viewer-coordinate-diagnostic.npz'
 with np.load(arr,allow_pickle=False)as n:own=n['triangles'];positions=n['allPositionVertices']
 assert own.shape==(171,3,3)and positions.shape==(513,3)and digest(own.astype('<f8').tobytes())==d['completeAuthoredMatrixWorldTrianglesSHA256']and digest(positions.astype('<f8').tobytes())==d['completeAuthoredMatrixWorldPositionsSHA256']
 selection=B/'government-xl-science-museum-partial-parent-20261005/selection.json.gz';r=next(x for x in read(selection)['rows']if x['uid']=='landsd/80343:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']=='df4eeb38ea777cf3016a497db81c0c2a36ea880da7a3cb5b27a426e8768dbe28';museum=decode_original_world_triangles(asset.read_bytes());assert museum.shape==(11520,3,3)
 oc=census(own,list(range(len(own))));mc=census(museum,list(range(len(museum))));ol={f:i for i,fs in enumerate(oc['sharedEdgeConnectedComponents'])for f in fs};ml={f:i for i,fs in enumerate(mc['sharedEdgeConnectedComponents'])for f in fs};rows=[]
 for family,key in [('positive-dimensional','exactPositiveDimensionalOriginalMuseumSourceContacts'),('point-only','pointOnlyOriginalMuseumContacts')]:
  for raw in d[key]:
   i,j=raw['openSidedOriginalFace'],raw['museumOriginalFace'];a,b=rational_face(own[i]),rational_face(museum[j]);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));assert any(na)and any(nb);points=[tuple(Fraction(x)for x in p)for p in raw['exactIntersectionPoints']];m=contact_measure(points);assert (m['dimension']>0)==(family=='positive-dimensional');coplanar=not any(cross(na,nb))and all(dot(na,sub(p,a[0]))==0 for p in b);assert coplanar or m['dimension']<2;mid=tuple(sum(p[k]for p in points)/len(points)for k in range(3));proper=not coplanar and m['dimension']>0 and relative_interior(a,mid)and relative_interior(b,mid);rows.append(dict(nonCoplanarIntersectionReachesBothRelativeInteriors=proper,properSurfaceCrossingIsNotSolidPenetrationProof=True,openOriginalFace=i,museumOriginalFace=j,openNonzeroEdgeBody=ol[i],museumNonzeroEdgeBody=ml[j],coplanar=coplanar,**m))
 bodies=[]
 for i,fs in enumerate(oc['sharedEdgeConnectedComponents']):
  f=own[fs];cs=[r for r in rows if r['openNonzeroEdgeBody']==i];bodies.append(dict(body=i,originalFaces=fs,completeOriginalBounds=[f.min((0,1)).tolist(),f.max((0,1)).tolist()],positiveDimensionalMuseumContactPairs=sum(r['dimension']>0 for r in cs),pointOnlyMuseumContactPairs=sum(r['dimension']==0 for r in cs),contactIsNotQualifiedAttachmentOrGradeRoot=True,architectureFunctionUnresolved=True))
 context=B/'xl-terrain-recovery-20261009-science-open-structure-context/diagnostic.json.gz';assert digest(context.read_bytes())=='40a100b0103ecfc34db42b2b223c46163211066d0d3e7d15a55e9ff100fed791';saved=read(context)['foreignCurrentForm'];assert saved['uid']=='landsd/83471:0'and saved['buildingCSUID']==d['stableCSUID']and saved['baseHeightHKPD']is None and saved['topHeightHKPD']is None;basic=shapely.Polygon(saved['rings'][0],saved['rings'][1:]);polys=shapely.polygons(own[:,:,[0,2]]);projection=shapely.union_all(polys[shapely.area(polys)>0]);overlap=projection.intersection(basic).area;registration=dict(savedHistoricalBASICForm=saved,stableCSUIDMatches=True,currentObjectIdRemapApproved=False,sourceProjectionAreaM2=projection.area,historicalBASICFootprintAreaM2=basic.area,sourceProjectionHistoricalBASICOverlapM2=overlap,originalProjectionCoveredByHistoricalBASIC=overlap/projection.area,historicalBASICCoveredByOriginalProjection=overlap/basic.area,centroidDistanceM=projection.centroid.distance(basic.centroid),originalSourceYBounds=[positions[:,1].min(),positions[:,1].max()],estimatedHistoricalBASICYBounds=[saved['base'],saved['base']+saved['height']],estimatedBASICHeightIsNotAuthoritativeElevation=True,currentBASICRuntimeNotCaptured=True)
 primary=B/'government-xl-science-museum-open-structure-primary-20261009';pr=read(primary/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(pr['jobId'],)).fetchone()==('complete',pr)
 for e in pr['evidenceRefs']:assert ref(ROOT/e['path'])==e
 pdf=primary/'architectural-services-museum-expansion-existing-plans.pdf';assert digest(pdf.read_bytes())=='33294263d195eac4031045acdd7912da02d2d67a43a6880a4fe00af3f0947878'
 refs=[ref(p)for p in [Path(__file__),C/'diagnostic.json.gz',C/'result.json',A/'result.json',arr,asset,selection,context,primary/'result.json',pdf,*[primary/('plan-page-'+str(i)+'.png')for i in [3,5,6]],HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
 out=dict(uids=['landsd/80343:0','landsd/83471:0'],originalOpen171FaceCensus=oc,originalMuseum11520FaceCensus=mc,originalOpenBodyDetails=bodies,allFrozenExactOriginalSourceContactPairsClassified=rows,completeFrozenExactPairsReusedWithoutRepeat=True,frozenBroadphaseExactPairs=d['completeBroadphaseEligibleExactPairsTested'],nonCoplanarPositiveDimensionalPairs=sum(not r['coplanar']and r['dimension']>0 for r in rows),coplanarPositiveDimensionalPairs=sum(r['coplanar']and r['dimension']>0 for r in rows),pointOnlyPairs=sum(r['dimension']==0 for r in rows),originalSourceYUnchanged=True,sourceRegistrationToHistoricalBASIC=registration,properNoncoplanarRelativeInteriorCrossingPairs=sum(r['nonCoplanarIntersectionReachesBothRelativeInteriors']for r in rows),primaryPlanContext=dict(actualSourceImagesReviewed=[3,5,6],sourceIs2022ExpansionProposalWithExistingMuseumAreas=True,observedContext='Site plan locates Science Museum/Museum of History, ground-floor plan includes existing museum area and ancillary areas, first-floor plan marks courtyard, lobby and existing footbridge. No feature is labelled with83471/83412/providerCSUID; exact original actor registration remains unproved.',georeferencedFeatureRegistrationPerformed=False,architecturalFunctionGranted=False),noSurfaceAbsenceSolidClearanceClaim=True,noGradeSupportOrBridgeCredit=True,currentBASICContactReplayNotClaimed=True,primaryExistingPlanRegistrationUnresolved=True,preservedHistoricalProjectedOverlapFaces=63,preservedHistoricalForeignGuardRoundedM2=1.855,sourceOnly=True,currentAcceptance=False,installationApproved=False,identityAccepted=False,geometryChanges=0,roleApproval=False,qualification='Complete exact original source topology and frozen finite surface-contact attribution only. Noncoplanar contact, coplanar contact, point contact and exact shared-edge connected body are distinct source context. None establishes valid architecture, whole solid clearance, ownership, support/root/bridge or replacement of current BASIC. All whole-original/current/F32/ground/foreign/native/runtime and primary-plan-registration obligations remain.',evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',out);print(json.dumps(dict(openBodies=len(bodies),museumBodies=len(mc['sharedEdgeConnectedComponents']),nonCoplanarPairs=out['nonCoplanarPositiveDimensionalPairs'],coplanarPairs=out['coplanarPositiveDimensionalPairs'],pointOnlyPairs=out['pointOnlyPairs'],currentAcceptance=False)))
if __name__=='__main__':main()
