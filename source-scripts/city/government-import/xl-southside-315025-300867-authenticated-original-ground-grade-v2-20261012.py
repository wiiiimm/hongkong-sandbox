"""UNEXECUTED authentic-original-ground residual grade/shared-edge/cap diagnostic.
Unchanged existing kernels; raw non-wall, uncovered, exposure and edge failures
remain explicit. No role/foundation/support/current acceptance or terrain change.
"""
import importlib.util,json,subprocess,sys,uuid,traceback,types
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from southside_authenticated_original_grade_scope_v1_20261012 import prepare,account_path
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_bound_facet_wall_context_20261010 import canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
FINITE=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012'
CURRENT_GRADE=BASE/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012'
DRAFT=BASE/'government-xl-southside-authenticated-original-ground-grade-draft-v1-20261012'
BATCH='government-xl-southside-315025-300867-authenticated-original-ground-grade-v2-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
INVENTORY=INPUT/'historical-obligations-verbatim.json'
UIDS=['landsd/315025:0','landsd/300867:0'];COUNTS={UIDS[0]:11699,UIDS[1]:1191};SOURCES={UIDS[0]:'85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c',UIDS[1]:'2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1'};MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
HELPERS=['southside_authenticated_original_grade_scope_v1_20261012.py','test_southside_authenticated_original_grade_scope_v2_20261012.py','run.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_projection_coverage_20261009.py','exact_original_projection_coverage_v2_20261010.py','exact_original_closed_projection_intersection_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','original_bound_facet_wall_context_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_v3_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
def finite(face,ground):
 a=coarse(face,ground);b=None if a['existingOrdinaryClearanceBoundProved']else paired(face,ground)
 return dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
def strict(proof):
 p=proof['coarse']if proof['coarse']['existingOrdinaryClearanceBoundProved']else proof['paired']
 return bool(p and p['groundProjectionCovered']and F(p['exactCertifiedLowerClearanceM'])>0)
def imported_local_files(*extras):
 queue=list(sys.modules.values())+list(extras);seen=set();files=set()
 while queue:
  m=queue.pop()
  if not isinstance(m,types.ModuleType)or id(m)in seen:continue
  seen.add(id(m));name=getattr(m,'__file__',None)
  if not name:continue
  p=Path(name).resolve()
  if ROOT not in p.parents or not p.is_file():continue
  files.add(p);queue.extend(v for v in vars(m).values()if isinstance(v,types.ModuleType))
 return sorted(files)


def preflight():
 assert not DOC.exists();refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'current-grade-to-authenticated-grade-caller.diff',DRAFT/'no-worker-schema-validation-v2.json',DRAFT/'preserved-code-preparation-v1.py',DRAFT/'code-preparation-v1-failure.json',DRAFT/'preserved-preflight-ground-routing-draft-v1.py',HERE/'xl-southside-315025-300867-authenticated-original-ground-grade-v1-20261012.py',HERE/'test_southside_authenticated_original_grade_scope_v1_20261012.py',DRAFT/'immutable-test-validation-v1/tests.log',DRAFT/'immutable-test-validation-v1/validation.json',DRAFT/'fixture-v1-to-v2.diff',DRAFT/'caller-v1-to-v2.diff',DRAFT/'caller-import-preflight-v1/import.log',DRAFT/'caller-import-preflight-v1/preflight.log',DRAFT/'caller-import-preflight-v1/validation.json',DRAFT/'caller-import-preflight-v1/adverse-fixture-cause.json',INVENTORY]+[HERE/n for n in HELPERS]+[HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']]
 receipts=[read(folder/'result.json')for folder in [INPUT,FINITE,CURRENT_GRADE]]
 assert [q['jobId']for q in receipts]==['3aa11a60f740759f78677d151fa2f9c34f494d935b7a208958164e23273f84d9','a3b5b315b784f978ab22d511b638106abb15ec334dc1aeabf428e80ccf83675c','7269234ae78ade5d10223502841ee35aba9e9d844d72c59d186ae56ee45cda71']
 for folder,receipt in zip([INPUT,FINITE,CURRENT_GRADE],receipts):
  refs.append(folder/'result.json');assert receipt['currentAcceptance']is False
  for pin in receipt['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 inputs=read(INPUT/'capture-inputs.json.gz');assert inputs['manifestSHA256']==MANIFEST
 forms=inputs['completeCurrentForms'];assert len(forms)==46 and len({f['uid']for f in forms})==46
 expected=sorted(set(['building:'+u for u in UIDS]+[('building:'+f['uid'])if f['uid'].startswith('landsd/')else('source-form:'+f['uid'])for f in forms]+['terrain-patch:'+u for u in UIDS]));assert inputs['canonicalResources']==expected and len(expected)==48
 data=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];assert set(data)==set(UIDS)
 saved=read(FINITE/'diagnostic.json.gz');rows={(q['uid'],q['arithmetic']):q for q in saved['rows']};assert len(rows)==8 and set(rows)=={(u,m)for u in UIDS for m in MODES}
 prior=read(CURRENT_GRADE/'diagnostic.json.gz');prior_rows={(q['uid'],q['arithmetic']):q for q in prior['rows']};assert set(prior_rows)==set(rows)
 selected=read(FINITE/'complete-unfiltered-authenticated-source-ground.json.gz');assert selected['completeAllOriginalSheetFacets']==774477 and selected['sourceCoordinateTransformsUnchanged']is True and selected['currentRendererGround']is False and selected['terrainGeometryChanges']==0
 grounds={q['uid']:q for q in selected['actorConservativeGrounds']};assert set(grounds)==set(UIDS)
 binding_file=DRAFT/'actual-saved-mode-bindings.json';bindings=read(binding_file);refs.append(binding_file);assert digest(binding_file.read_bytes())=='ae459858b2e99f68046745b174cc2600b9b680864d5c9a75d138c07383d4b78d'
 assert bindings['currentGradeDiagnosticSHA256']==digest((CURRENT_GRADE/'diagnostic.json.gz').read_bytes())and bindings['authenticatedComparisonDiagnosticSHA256']==digest((FINITE/'diagnostic.json.gz').read_bytes())
 assert sum(len(q['completeOriginalFaceComparisons'])for q in rows.values())==51560
 for uid in UIDS:
  item=data[uid];assert item['sourceSHA256']==SOURCES[uid] and set(item['completeWorldStreams'])==set(MODES)
  g=grounds[uid];ground=np.asarray(g['completeSelectedFacets'],dtype='<f8');assert digest(ground.tobytes())==g['completeSelectedFacetSHA256']and g['closedAABBWholeFacetSelection']is True and g['allSlopesVerticalAndCollapsedProjectionFacetsRetained']is True and g['noHeightAreaOrSlopeFilter']is True
  current_ground=np.asarray(item['completeDrawnGround'],dtype='<f8');assert current_ground.shape[1:]==(3,3)and np.isfinite(current_ground).all()and digest(current_ground.tobytes())==item['completeDrawnGroundSHA256']
  for mode in MODES:
   world=np.asarray(item['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');assert np.isfinite(world).all()and np.isfinite(ground).all();assert digest(world.tobytes())==item['completeWorldStreams'][mode]['completeWorldTriangleSHA256']
   p=prior_rows[uid,mode];assert p['completeGroundSHA256']==item['completeDrawnGroundSHA256']
   prepared=prepare(world,ground,p,rows[uid,mode],bindings['boundModes'][uid+'|'+mode])
   assert len(prepared['failed'])==(300 if uid==UIDS[0]else 163)and len(prepared['nonsteep'])==(12 if uid==UIDS[0]else 0)
 history=read(INVENTORY);assert history['historicalOnly'] and not history['currentApprovalTransferred'] and history['obligations']['unresolvedOriginalComponents']==19
 spec=importlib.util.spec_from_file_location('southside_grade_freezer_preflight',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer);refs.extend(imported_local_files(freezer))
 validation=read(DRAFT/'no-worker-schema-validation-v2.json');assert validation['callerSHA256']==digest(Path(__file__).read_bytes())and validation['methodSHA256']==digest((DRAFT/'METHOD.md').read_bytes())and validation['diffSHA256']==digest((DRAFT/'current-grade-to-authenticated-grade-caller.diff').read_bytes())
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 return receipts,refs,pins,inputs,data,rows,history,prior_rows,grounds,bindings

def owned(state):
 test_validation=read(DRAFT/'immutable-test-validation-v2/validation.json');assert test_validation['testsRun']==26 and test_validation['exitCode']==0 and test_validation['result']=='OK'
 expected_codes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in [Path(__file__),*[HERE/n for n in HELPERS]]};assert test_validation['codePins']==expected_codes
 for path,h in test_validation['codePins'].items():assert digest((ROOT/path).read_bytes())==h
 receipts,refs,pins,inputs,data,saved_rows,history,prior_rows,grounds,bindings=state;lease=read(LEASE);assert lease['resources']==inputs['canonicalResources']and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();rows=[]
 for n in ['validation.json','tests.log']:
  q=DRAFT/'immutable-test-validation-v2'/n;refs.append(q);pins[str(q.relative_to(ROOT))]=digest(q.read_bytes())
 assert digest((DRAFT/'immutable-test-validation-v2/tests.log').read_bytes())==test_validation['testLogSHA256']
 for uid in UIDS:
  item=data[uid];nfaces=COUNTS[uid];ground=np.asarray(grounds[uid]['completeSelectedFacets'],dtype='<f8');gsha=digest(ground.tobytes())
  for mode in MODES:
   stream=item['completeWorldStreams'][mode];world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');wsha=digest(world.tobytes());assert world.shape==(nfaces,3,3)and np.isfinite(world).all()and wsha==stream['completeWorldTriangleSHA256']
   prior=saved_rows[uid,mode];prepared=prepare(world,ground,prior_rows[uid,mode],prior,bindings['boundModes'][uid+'|'+mode]);topology=prepared['topology'];zeros=prepared['zeros'];steep=prepared['steep'];records=prepared['records'];failed=prepared['failed'];eligible=prepared['eligible']
   # Excluding failed non-walls/zeros is explicit path-only scope; EVERY original
   # face remains in the finite result and complete topology above.
   adapted=[dict(sourceFace=j,priorCoarseBoundProofVerbatim=dict(sourceFace=j,completeOriginal=records[i]['authenticatedOriginalGroundComparison']['coarse']),pairedExactOriginalFiniteBound=records[i]['authenticatedOriginalGroundComparison']['paired'],completeOriginalBoundProved=records[i]['authenticatedOriginalGroundComparison']['completeFiniteOrdinaryBoundProved'])for j,i in enumerate(eligible)]
   ctx=[];paths=None;method_failure=None;edge_rows=[]
   if eligible:
    try:
     tri=world[eligible];binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=gsha,completeFiniteFacetProofRowsSHA256=canonical(adapted));ctx=contexts(tri,ground,adapted,expected_binding=binding,current_binding=binding)
     binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([]));paths=cap_paths(tri,ctx,[],expected_binding=binding,current_binding=binding)
    except AssertionError:
     method_failure=dict(disposition='context-or-path-contract-negative-not-source-corruption',traceback=traceback.format_exc())
   grade_ids=sorted(failed&steep);grade=exact_finite_contacts(world,grade_ids,ground,list(range(len(ground))),maximum_pairs=len(grade_ids)*len(ground))if grade_ids else dict(contacts=[],allPairsExamined=True,sourceFacesOmitted=0,emptyAffectedSteepScope=True)
   if grade_ids:assert grade['allPairsExamined']and grade['sourceFacesOmitted']==0
   positive_grade_ids={q['sourceFaceA']for q in grade['contacts']if q['dimension']>0}
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
     cap=ids[-1];account=account_path(ids,eligible=eligible,component_map=prepared['componentMap'],positive_grade_ids=positive_grade_ids,terminal_cap_strict=strict(records[cap]['authenticatedOriginalGroundComparison']),interfaces=interfaces,raw_helper_path=path);nonempty_wall_path=account['nonemptyOriginalWallPath'];edge_rows.append(dict(sourceFace=ids[0],nonemptyOriginalWallPath=nonempty_wall_path,sourceFaceHasGenuinePositiveDimensionalGradeContact=ids[0]in positive_grade_ids,diagnosticGradeToWholeClearCapAndExposedEdges=bool(nonempty_wall_path and ids[0]in positive_grade_ids and path['hasExactOriginalStrictClearCapRoofPath']and strict(records[cap]['authenticatedOriginalGroundComparison'])and all(q['hasWholeStrictlyExposedOriginalEdge']for q in interfaces)),completeSourceFacePath=ids,rawOriginalCapHelperPath=path,interfaces=interfaces,terminalCapWholeFiniteStrictlyClear=bool(path['hasExactOriginalStrictClearCapRoofPath']and strict(records[cap]['authenticatedOriginalGroundComparison'])),allPathInterfacesHaveWholeExposedSharedEdge=all(r['hasWholeStrictlyExposedOriginalEdge']for r in interfaces),rawExposureFailurePreserved=not path['rawFaceExposurePositive'],rootCredit=False,fullBodyRootProved=False,sourceOriginalComponent=prepared['componentMap'][ids[0]],diagnosticAccountVerbatim=account))
   body_accounts=[]
   for component,face_ids in enumerate(topology['sharedEdgeConnectedComponents']):
    points=world[face_ids].reshape(-1,3);body_accounts.append(dict(originalComponent=component,completeOriginalFaceIds=face_ids,completeOriginalBounds=[points.min(0).tolist(),points.max(0).tolist()],authenticatedResidualIds=sorted(set(face_ids)&failed),excludedNonsteepResidualIds=sorted(set(face_ids)&prepared['nonsteep']),genuineDiagnosticGradeCapStarts=[q['sourceFace']for q in edge_rows if q['sourceOriginalComponent']==component and q['diagnosticAccountVerbatim']['diagnosticGradeToWholeClearCapAndExposedEdges']],rootCredit=False,fullBodyRootProved=False,sourceRoleUninterpreted=True))
   row=dict(completeBodyObligationAccount=body_accounts,uid=uid,sourceSHA256=SOURCES[uid],arithmetic=mode,completeWorldSHA256=wsha,completeGroundSHA256=gsha,completeOriginalFaces=nfaces,completeOriginalTopology=topology,measuredNonzeroSharedEdgeComponentCount=len(topology['sharedEdgeConnectedComponents']),allCompleteOriginalFiniteRecords=records,allRawFailedFaces=sorted(failed),failedNonsteepFacesUncredited=sorted(failed-steep-zeros),allZeroFacesUncredited=sorted(zeros),eligibleOriginalFaceIds=eligible,completeEligibleFacetContexts=ctx,rawCapPathDiagnostic=paths,contextOrPathContractFailure=method_failure,wholeOriginalSharedEdgeAndCapExposure=edge_rows,completeFailedSteepGradeContactInventory=grade,gradeSourceFaceIds=grade_ids,allAuthenticatedOriginalGroundFacetsRetained=len(ground),currentDrawnGroundSHA256Retained=item['completeDrawnGroundSHA256'],currentRawFailureIdsRetained=prior['allCurrentFailuresRetainedVerbatim'],completeResidualFaceIdsAccounted=sorted(failed),pairResidualFaceCount=463,perActorResidualFaceCount=len(failed),authenticatedGroundGlobalOriginalFacetIds=grounds[uid]['selectedGlobalOriginalFacetIds'],authenticGroundIsRenderer=False,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,foundationInterpretationAccepted=False)
   rows.append(row);save(LOCAL/('completed-'+uid.split('/')[1].replace(':','-')+'-'+mode+'.json.gz'),row);print(json.dumps(dict(uid=uid,arithmetic=mode,rawFailures=len(failed),nonzeroEdgeComponents=row['measuredNonzeroSharedEdgeComponentCount'],gradeContacts=len(grade['contacts']),pathContractNegative=method_failure is not None)),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,rows=rows,currentCaptureReceipt=receipts[0]['jobId'],completeAuthenticFiniteReceiptReusedExactly=receipts[1]['jobId'],priorCurrentGradeReceiptRetained=receipts[2]['jobId'],completeSourceSlots=51560,authenticSourceGroundNotRenderer=True,allHistoricalObligationsVerbatim=history,allCompleteCurrentForeignFormsRetainedVerbatim=inputs['completeCurrentForms'],completeCurrentManifestSHA256=MANIFEST,completeCurrentNativeCatalogueCount=6649,noWholeFaceFiniteRecomputation=True,noSupplierInterfaceOrIdentityReapproval=True,noEmptyPathOrPointContactRootCredit=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(DOC/'diagnostic.json.gz');refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 s=importlib.util.spec_from_file_location('southside_grade_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=m.freeze(BATCH,'southside-authenticated-original-ground-residual-grade-edge-cap-diagnostic-no-root-role-credit',refs,dict(uids=UIDS,completeSourceFaces=COUNTS,currentNativeCatalogueCount=6649,all19HistoricalSourceObligationsRetained=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)

def main():
 state=preflight()
 if '--preflight-only'in sys.argv:
  print(json.dumps(dict(noWorker=True,noDB=True,noLease=True,noGradeOrTopologyPredicatesRun=True,completeModes=MODES,sourceFaces=COUNTS,completeFiniteRows=len(state[5]),resources=state[3]['canonicalResources'],historicalUnresolvedComponents=19,currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();resources=state[3]['canonicalResources'];claim=reservations.claim('southside-authenticated-original-grade-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
