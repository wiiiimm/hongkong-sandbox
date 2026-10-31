"""DRAFT only: original authored joints, complete minimum openings, historical grade context.
No component role, source identity, structural/root/current or installation approval.
"""
from pathlib import Path
from collections import defaultdict
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,shell_self_intersections,cross,sub,dot
from original_shell_diagnostic_20261009 import shell_context
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_original_simple_lower_opening_mounts_v1_20261011 import binding,verify
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
B=ROOT/'docs/astra-city/government-import';C=B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011';T=B/'government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';U=B/'government-xl-science-museum-original-raw-uv-body-atlas-registration-v1-20261011';X=B/'government-xl-science-museum-original171-cross-body-contact-inventory-v1-20261011';H=B/'xl-terrain-recovery-20261009-80343-wall-context';DOC=B/'government-xl-science-museum-original171-bounded-mount-grade-context-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def minimum_edges(t,fs):
 low=float(t[fs,:,1].min());inc=defaultdict(list)
 for i in fs:
  xyz=list(map(tuple,t[i]))
  for a,b in zip(xyz,xyz[1:]+xyz[:1]):
   if a[1]==b[1]==low and a!=b:inc[tuple(sorted([a,b]))].append(i)
 return low,[dict(edge=[list(a),list(b)],incidentOriginalFaces=rows)for(a,b),rows in sorted(inc.items())]
def main():
 assert not DOC.exists()
 for f in [C,T,U]:
  r=read(f/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 arr=C/'complete-original-viewer-coordinate-diagnostic.npz'
 with np.load(arr,allow_pickle=False)as n:own=n['triangles']
 d=read(C/'diagnostic.json.gz');assert own.shape==(171,3,3)and digest(own.astype('<f8').tobytes())==d['completeAuthoredMatrixWorldTrianglesSHA256'];t=read(T/'diagnostic.json.gz');u=read(U/'diagnostic.json.gz');x=read(X/'diagnostic.json.gz');assert x['source171WorldSHA256']==d['completeAuthoredMatrixWorldTrianglesSHA256'];bodies=t['originalOpenBodyDetails'];assert [z['body']for z in bodies]==list(range(5));uv={r['originalFace']:r for r in u['complete171SourceFaceUVBodyRows']};proper=[r for r in x['allOriginalCrossBodyFiniteContacts']if r['noncoplanarBothRelativeInteriorSurfaceCrossing']];assert len(proper)==17
 selection=B/'government-xl-science-museum-partial-parent-20261005/selection.json.gz';r=next(z for z in read(selection)['rows']if z['uid']=='landsd/80343:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']=='df4eeb38ea777cf3016a497db81c0c2a36ea880da7a3cb5b27a426e8768dbe28';museum=decode_original_world_triangles(asset.read_bytes());assert museum.shape==(11520,3,3);mfs=sorted(f for fs in t['originalMuseum11520FaceCensus']['sharedEdgeConnectedComponents']for f in fs);joined=np.concatenate([own,museum]);hosts=[171+i for i in mfs];rows=[]
 for body in bodies:
  fs=body['originalFaces'];local=own[fs];shell=shell_context(local,list(range(len(local))));assert shell['componentFaces']==list(range(len(fs)));selftest=shell_self_intersections(local,maximum_faces=len(fs));selftest['localToOriginalFaces']=fs
  targets=[('whole-nonzero-original-Museum',hosts)]
  for parent in [0,1]:
   if parent!=body['body']:targets.append(('original-open-body-'+str(parent),bodies[parent]['originalFaces']))
  mounts=[]
  for label,hfs in targets:
   proof=None;failure=None;bind=binding(joined,fs,hfs)
   try:proof=verify(joined,fs,hfs,expected_binding=bind)
   except AssertionError as error:failure=str(error)
   mounts.append(dict(hostLabel=label,exactSourceBodyHostBinding=bind,wholeSimpleMinimumOpeningProof=proof,guardFailure=failure,associationOnlyNoHostGradeOrRole=True))
  low,edges=minimum_edges(own,fs);rows.append(dict(originalBody=body['body'],completeOriginalFaces=fs,originalShellContext=shell,completeBoundedSelfIntersectionContext=selftest,exactMinimumHeightM=low,completeOriginalMinimumHeightEdges=edges,wholeMinimumOpeningAssociations=mounts,directOriginalMuseumPositiveContactPairs=body['positiveDimensionalMuseumContactPairs'],roleAndGroundPathUnresolved=True))
 crossings=[]
 for raw in proper:
  i,j=raw['originalFaces'];a,b=rational_face(own[i]),rational_face(own[j]);points=sorted(intersection_points(a,b));assert len(points)==2;na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));crossings.append(dict(frozenContactVerbatim=raw,exactOriginalIntersectionEndpoints=[[str(v)for v in p]for p in points],completeOriginalFaceGeometry=own[[i,j]].tolist(),originalFaceUVMaterialImageRows=[uv[i],uv[j]],originalFaceUnitNormals=[(np.asarray([float(v)for v in n])/np.linalg.norm([float(v)for v in n])).tolist()for n in [na,nb]],face69Or70CarriesFrontagePhoto=i in [69,70]or j in [69,70],surfaceIntersectionIsNotAuthoredJointApproval=True,closedSolidInterpenetrationNotInferred=True))
 historical=read(H/'diagnostic.json.gz');assert historical['wholeSourceFaces']==11520 and historical['wholeSourceUncoveredFaces']==0
 for e in historical['evidenceRefs']:assert ref(ROOT/e['path'])==e
 runtime=HERE/'local/government-xl-science-museum-partial-parent-20261005/runtime-geometry.json.gz';gr=next(z for z in read(runtime)['rows']if z['uid']=='landsd/80343:0');assert gr['sourceSHA256']==r['sourceSHA256'];ground=np.asarray(gr['drawnGroundGeometry'],float).reshape(-1,3,3);assert np.isfinite(ground).all();valid=np.any(np.cross(ground[:,1]-ground[:,0],ground[:,2]-ground[:,0])!=0,axis=1);ground=ground[valid];grade=[]
 for k,fs in enumerate(t['originalMuseum11520FaceCensus']['sharedEdgeConnectedComponents']):
  low,edges=minimum_edges(museum,fs);proofs=[dict(**edge,fixedBandAgainstCompleteHistoricalDrawnGround=verify_contact_segment(edge['edge'],ground))for edge in edges];grade.append(dict(originalMuseumNonzeroBody=k,completeOriginalBodyFaces=fs,minimumHeightM=low,completeOriginalMinimumHeightEdges=proofs,minimumEdgeInventoryDoesNotExcludeHigherGradeWallInterfaces=True))
 refs=[ref(p)for p in [Path(__file__),arr,C/'diagnostic.json.gz',C/'result.json',T/'diagnostic.json.gz',T/'result.json',U/'diagnostic.json.gz',U/'result.json',X/'diagnostic.json.gz',selection,asset,H/'diagnostic.json.gz',H/'result.json',runtime,HERE/'exact_original_shell_intersections_20261009.py',HERE/'original_shell_diagnostic_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'complete_original_simple_lower_opening_mounts_v1_20261011.py',HERE/'complete_original_lower_opening_mounts_v2_20261011.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'test_complete_original_simple_lower_opening_mounts_v1_20261011.py']]
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/80343:0','landsd/83471:0'],source171WorldSHA256=d['completeAuthoredMatrixWorldTrianglesSHA256'],originalMuseumWorldSHA256=digest(museum.astype('<f8').tobytes()),completeOriginalBodyMountAndTopologyRows=rows,all17InternalBothRelativeInteriorCrossingAttributions=crossings,completeHistoricalMuseumMinimumEdgeGradeInventory=grade,historicalGroundCompleteCapturedArraySHA256=digest(ground.astype('<f8').tobytes()),historicalGradeContextOnly=True,historicalWholeSourceWallDiagnosticSummary={k:historical[k]for k in ['wholeSourceFaces','wholeSourceUncoveredFaces','affectedWallFaces','otherAffectedFaces','upwardContinuousMinimumGapM']},allFiveBodyObligationsPreserved=True,body2DirectMuseumContactsPreserved=46,originalZerosPreserved=t['originalOpen171FaceCensus']['exactNonrenderingOriginalFaces'],preserved53MuseumProperCrossings=True,preservedHistoricalForeignGuardFaces=63,preservedHistoricalForeignGuardRoundedM2=1.855,sourceOnly=True,currentAcceptance=False,identityAccepted=False,roleApproval=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False,geometryChanges=0,qualification='Source-only original finite mount/topology and exact authored internal crossing attribution. Neither photographic texture nor geometric contacts establishes load bearing, joint validity or impossible solid assembly. Simple minimum-opening results are association only; closed-shell context alone is not solid clearance. Historical full drawn-ground array and Museum minimum-edge inventory are explicitly not current ground or a complete higher-wall grade search. A feasible import still requires supported representation roles, genuine qualified Museum grade route, complete original/literal/F32 physical/current identity/foreign/native/runtime and all body/detail obligations.',evidenceRefs=refs));print(json.dumps(dict(sourceOnly=True,completeBodies=len(rows),internalProperCrossings=len(crossings),museumHistoricalMinimumBodyInventories=len(grade),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
