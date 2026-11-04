"""UNEXECUTED complete Ocean Walk finite/grade/shared-edge/cap diagnostic.
Unchanged existing kernels; raw non-wall, uncovered, exposure and edge failures
remain explicit. No role/foundation/support/current acceptance or terrain change.
"""
import importlib.util,json,subprocess,sys,uuid,traceback
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_bound_facet_wall_context_20261010 import canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-ocean-walk-current-actual-ground-capture-v1-20261012'
BATCH='government-xl-ocean-walk-complete-four-stream-current-grade-paths-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
INVENTORY=BASE/'government-xl-ocean-walk-current-grade-paths-draft-v1-20261012/historical-source-and-obligation-inventory.json'
UID='landsd/81743:0';SOURCE='52e0d6b6341f664cc18ee8a894e1c4c5e5dbc1b05729bb43deb8c109e0fac8cb';MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
HELPERS=['run.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_projection_coverage_20261009.py','exact_original_projection_coverage_v2_20261010.py','exact_original_closed_projection_intersection_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','original_bound_facet_wall_context_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_v3_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
def normal(face):
 p,q,r=[[F.from_float(float(x))for x in v]for v in face];u=[q[i]-p[i]for i in range(3)];v=[r[i]-p[i]for i in range(3)];return[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
def finite(face,ground):
 a=coarse(face,ground);b=None if a['existingOrdinaryClearanceBoundProved']else paired(face,ground)
 return dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
def strict(proof):
 p=proof['coarse']if proof['coarse']['existingOrdinaryClearanceBoundProved']else proof['paired']
 return bool(p and p['groundProjectionCovered']and F(p['exactCertifiedLowerClearanceM'])>0)
def preflight():
 assert not DOC.exists();receipt=read(INPUT/'result.json');refs=[Path(__file__),INPUT/'result.json',INVENTORY]+[HERE/n for n in HELPERS]+[HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']]
 for pin in receipt['evidenceRefs']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 inputs=read(INPUT/'capture-inputs.json.gz');assert inputs['manifestSHA256']==MANIFEST
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');assert data['uid']==UID and data['sourceSHA256']==SOURCE and set(data['completeWorldStreams'])==set(MODES)
 capture=read(INPUT/'complete-current-actual-source-and-ground-81743-0.json.gz')
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 history=read(INVENTORY);assert len(history['sourceActors'])==18 and history['completeOriginalActorFaces']==28858 and len(history['sixPriorBasicRegressions'])==6 and len(history['unresolvedInterfaceUIDs'])==11
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 return receipt,refs,pins,inputs,data,capture,history

def owned(state):
 receipt,refs,pins,inputs,data,capture,history=state;lease=read(LEASE);assert lease['resources']==inputs['canonicalResources']and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();ground=np.asarray(data['completeDrawnGround'],dtype='<f8');assert ground.ndim==3 and ground.shape[1:]==(3,3)and len(ground)and np.isfinite(ground).all();gsha=digest(ground.tobytes());assert gsha==data['completeDrawnGroundSHA256']
 cache={};rows=[]
 for mode in MODES:
  stream=data['completeWorldStreams'][mode];world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');wsha=digest(world.tobytes());assert world.shape==(15484,3,3)and np.isfinite(world).all()and wsha==stream['completeWorldTriangleSHA256']
  topology=census(world,list(range(15484)));zeros=set(topology['exactNonrenderingOriginalFaces']);normals=[normal(face)for face in world];steep={i for i,n in enumerate(normals)if i not in zeros and 16*n[1]*n[1]<=sum(x*x for x in n)}
  records=[]
  for i,face in enumerate(world):
   key=(digest(face.tobytes()),gsha)
   if key not in cache:cache[key]=finite(face,ground)
   records.append(dict(sourceFace=i,completeOriginalFacetSHA256=key[0],exactOrientationDiagnostic='zero-area'if i in zeros else('steep-wall'if i in steep else('upward-nonsteep'if normals[i][1]>0 else'downward-or-sloping-nonsteep')),currentDrawnGroundComparison=cache[key]))
   if i%2000==0:print(json.dumps(dict(arithmetic=mode,completeFiniteFaces=i)),flush=True)
  failed={i for i,r in enumerate(records)if not r['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']};eligible=sorted(set(range(15484))-zeros-(failed-steep))
  # Excluding failed non-walls/zeros is explicit path-only scope; EVERY original
  # face remains in the finite result and complete topology above.
  adapted=[dict(sourceFace=j,priorCoarseBoundProofVerbatim=dict(sourceFace=j,completeOriginal=records[i]['currentDrawnGroundComparison']['coarse']),pairedExactOriginalFiniteBound=records[i]['currentDrawnGroundComparison']['paired'],completeOriginalBoundProved=records[i]['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved'])for j,i in enumerate(eligible)]
  ctx=[];paths=None;method_failure=None;edge_rows=[]
  if eligible:
   try:
    tri=world[eligible];binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=gsha,completeFiniteFacetProofRowsSHA256=canonical(adapted));ctx=contexts(tri,ground,adapted,expected_binding=binding,current_binding=binding)
    binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([]));paths=cap_paths(tri,ctx,[],expected_binding=binding,current_binding=binding)
   except AssertionError:
    method_failure=dict(disposition='context-or-path-contract-negative-not-source-corruption',traceback=traceback.format_exc())
  if paths is not None:
   for path in paths['paths']:
    ids=[eligible[j]for j in path['originalPath']];interfaces=[]
    for a,b in zip(ids,ids[1:]):
     def edges(i):
      vertices=[tuple(v)for v in world[i]];return {tuple(sorted((u,v)))for u,v in zip(vertices,vertices[1:]+vertices[:1])if u!=v}
     shared=sorted(edges(a)&edges(b));assert shared,'Existing cap helper returned a non-shared-edge path'
     certificates=[]
     for edge in shared:
      segment=np.asarray([edge[0],edge[1],edge[1]],dtype='<f8');proof=finite(segment,ground)
      certificates.append(dict(exactWholeOriginalNonzeroSharedEdge=[list(v)for v in edge],completeFiniteExposureProof=proof,wholeSharedEdgeStrictlyExposed=strict(proof)))
     interfaces.append(dict(sourceFaces=[a,b],allExactSharedEdges=certificates,hasWholeStrictlyExposedOriginalEdge=any(r['wholeSharedEdgeStrictlyExposed']for r in certificates)))
    cap=ids[-1];edge_rows.append(dict(sourceFace=ids[0],completeSourceFacePath=ids,rawOriginalCapHelperPath=path,interfaces=interfaces,terminalCapWholeFiniteStrictlyClear=bool(path['hasExactOriginalStrictClearCapRoofPath']and strict(records[cap]['currentDrawnGroundComparison'])),allPathInterfacesHaveWholeExposedSharedEdge=all(r['hasWholeStrictlyExposedOriginalEdge']for r in interfaces),rawExposureFailurePreserved=not path['rawFaceExposurePositive'],rootCredit=False))
  grade_ids=sorted(failed&steep);grade=exact_finite_contacts(world,grade_ids,ground,list(range(len(ground))),maximum_pairs=len(grade_ids)*len(ground))if grade_ids else dict(contacts=[],allPairsExamined=True,sourceFacesOmitted=0,emptyAffectedSteepScope=True)
  if grade_ids:assert grade['allPairsExamined']and grade['sourceFacesOmitted']==0
  row=dict(arithmetic=mode,completeWorldSHA256=wsha,completeGroundSHA256=gsha,completeOriginalFaces=15484,completeOriginalTopology=topology,measuredNonzeroSharedEdgeComponentCount=len(topology['sharedEdgeConnectedComponents']),all15484FiniteRecords=records,allRawFailedFaces=sorted(failed),failedNonsteepFacesUncredited=sorted(failed-steep-zeros),allZeroFacesUncredited=sorted(zeros),eligibleOriginalFaceIds=eligible,completeEligibleFacetContexts=ctx,rawCapPathDiagnostic=paths,contextOrPathContractFailure=method_failure,wholeOriginalSharedEdgeAndCapExposure=edge_rows,completeFailedSteepGradeContactInventory=grade,gradeSourceFaceIds=grade_ids,allCurrentGroundFacetsRetained=len(ground),sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,foundationInterpretationAccepted=False)
  rows.append(row);save(LOCAL/('completed-'+mode+'.json.gz'),row);print(json.dumps(dict(arithmetic=mode,rawFailures=len(failed),nonzeroEdgeComponents=row['measuredNonzeroSharedEdgeComponentCount'],gradeContacts=len(grade['contacts']),pathContractNegative=method_failure is not None)),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE,rows=rows,completeCurrentManifestSHA256=MANIFEST,completeCurrentNativeCatalogueCount=6649,all18HistoricalActorSourceBindings=history['sourceActors'],sixPriorBasicRegressionsRetainedVerbatim=history['sixPriorBasicRegressions'],elevenPriorUnresolvedInterfacesRetainedVerbatim=history['unresolvedInterfaceUIDs'],all17PriorInterfaceRowsRetainedVerbatim=history['prior17InterfaceRowsVerbatim'],priorNegativeEvidencePinsVerbatim=history['additionalPriorNegativeEvidencePins'],noSupplierInterfaceReapproval=True,noHistoricalRuntimeProofTransfer=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for p,h in {**pins,**capture['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(DOC/'diagnostic.json.gz');refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 s=importlib.util.spec_from_file_location('ocean_grade_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=m.freeze(BATCH,'ocean-walk-complete-four-world-grade-exposed-original-edge-clear-cap-diagnostic-no-role-credit',refs,dict(uids=[UID],completeSourceFaces=15484,currentNativeCatalogueCount=6649,sixPriorBasicRegressionsRetained=True,elevenPriorInterfacesRetained=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();resources=state[3]['canonicalResources'];claim=reservations.claim('ocean-complete-current-grade-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
