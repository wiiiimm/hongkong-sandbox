"""Fresh preserved-candidate grade and exposed-cap diagnostic, no typed root acceptance.

The four complete original bodies account for all129 real-facet negatives.
All22 raw descriptive downward labels stay verbatim. Exact arithmetic separates
20 actual horizontal lower caps (no bridge) and two actual steep walls3854/3855. The three collapsed negatives also provide no bridge.
"""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from fractions import Fraction as F
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import source_proposal_pin_path
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_bound_facet_wall_context_20261010 import canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011';PHYSICAL=BASE/'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011';COMPARE=BASE/'government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011';GRAPH=BASE/'government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011'
PREVIOUS_GRADE=BASE/'government-xl-evangel-college-91306-current-four-body-grade-paths-v3-20261011'
BATCH='government-xl-evangel-college-91306-current-four-body-grade-paths-v4-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,PHYSICAL,COMPARE,GRAPH,PREVIOUS_GRADE]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for pin in receipt['evidenceRefs']:
    p=source_proposal_pin_path(pin)if folder in [INPUT,GRAPH]else ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');comparison=read(COMPARE/'diagnostic.json.gz');graph=read(GRAPH/'diagnostic.json.gz');runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path);assert len(runtime['rows'])==1 and runtime['rows'][0]['uid']==UID;ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert digest(ground.tobytes())==comparison['completeGrounds']['currentDrawn']['completeWorldSHA256']and data['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==runtime['inputHashes']['3d-viewer/city/data/manifest.json'];assert read(PHYSICAL/'diagnostic.json.gz')['all17CurrentActorGuardsRetained']
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs.append(runtime_path)
 prior_grade=read(PREVIOUS_GRADE/'diagnostic.json.gz');assert prior_grade['completeActualCandidateGroundSHA256']==digest(ground.tobytes())
 rows=[];cache={}
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');sha=digest(world.tobytes());assert sha==stream['completeWorldTriangleSHA256'];g=next(r for r in graph['rows']if r['arithmetic']==mode);previous=next(r for r in comparison['rows']if r['arithmetic']==mode);assert g['completeWorldSHA256']==previous['completeWholeWorldSHA256']==sha
  topology=g['completeOriginalTopology'];parts=topology['sharedEdgeConnectedComponents'];ids=sorted(i for c in [13,68,69,223]for i in parts[c]);assert len(ids)==5297 and len(set(ids))==5297
  failed=set(previous['failedFacesByGround']['currentDrawn']);zeros=set(topology['exactNonrenderingOriginalFaces']);assert len(failed)==132 and len(failed&zeros)==3 and failed-zeros<=set(ids)
  records=previous['complete13960FaceComparisons'];raw_downward=sorted(i for i in ids if i in failed and records[i]['orientationDiagnostic']=='downward');assert len(raw_downward)==22
  exact_steep=set()
  for i in failed-zeros:
   v=[[F(float(x))for x in p]for p in world[i]];a=[v[1][k]-v[0][k]for k in range(3)];b=[v[2][k]-v[0][k]for k in range(3)];n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
   if any(n)and 16*n[1]*n[1]<=sum(x*x for x in n):exact_steep.add(i)
  assert len(exact_steep)==109 and sorted(exact_steep-set(i for i in failed if records[i]['orientationDiagnostic']=='steep-wall'))==[3854,3855]
  downward=sorted((failed-zeros)-exact_steep);assert downward==list(range(5137,5147))+list(range(5181,5191))
  assert all(len(set(world[i,:,1]))==1 for i in downward)
  eligible=sorted(set(ids)-set(downward));assert len(eligible)==5277
  if sha not in cache:
   adapted=[dict(sourceFace=j,priorCoarseBoundProofVerbatim=dict(sourceFace=j,completeOriginal=records[i]['groundComparisons']['currentDrawn']['coarse']),pairedExactOriginalFiniteBound=records[i]['groundComparisons']['currentDrawn']['paired'],completeOriginalBoundProved=records[i]['groundComparisons']['currentDrawn']['completeFiniteOrdinaryBoundProved'])for j,i in enumerate(eligible)]
   t=world[eligible];binding=dict(completeOriginalWorldTrianglesSHA256=digest(t.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical(adapted));ctx=contexts(t,ground,adapted,expected_binding=binding,current_binding=binding)
   mapping={i:j for j,i in enumerate(eligible)};pairs=set()
   for pair in g['everyNominatedPairPrimitiveInventory']:
    for contact in pair['completePrimitiveContactInventory']['contacts']:
     a,b=contact['sourceFaceA'],contact['sourceFaceB']
     if a in mapping and b in mapping and contact['dimension']>0 and contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2:pairs.add(tuple(sorted((mapping[a],mapping[b]))))
   pairs=[list(p)for p in sorted(pairs)];path_binding=dict(completeOriginalWorldTrianglesSHA256=digest(t.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical(pairs));proof=cap_paths(t,ctx,pairs,expected_binding=path_binding,current_binding=path_binding)
   prior_row=next(r for r in prior_grade['rows']if r['arithmetic']==mode);assert prior_row['completeWorldSHA256']==sha and prior_row['completeFourOriginalBodyFaces']==ids
   complete_grade=prior_row['complete5297CurrentGradeContactInventory'];assert complete_grade['allPairsExamined']and complete_grade['sourceFacesOmitted']==0
   wall_ids={eligible[p['sourceFace']]for p in proof['paths']};assert wall_ids==exact_steep and len(wall_ids)==109
   cache[sha]=dict(completeFourOriginalBodyFaces=ids,all5297RawCurrentFiniteRecords=[records[i]for i in ids],rawDescriptive22DownwardLabelsRetainedVerbatim=raw_downward,exact20HorizontalLowerClosureFacesRetainedWithoutPathCredit=downward,rawZeroFailureFacesRetainedAsUncredited=sorted(failed&zeros),eligibleWallCapPathFaceToSourceFace=eligible,complete5277EligibleFacetContexts=ctx,exactPositiveInterfacePairs=pairs,strictCapPathDiagnostic=proof,complete5297CurrentGradeContactInventory=complete_grade,all129RealFaceNegativesAccounted=True,noExactLowerClosureOrZeroFacetProvidesPath=True,exactSteepPredicateUsedWithoutThresholdChange=True,sourceGeometryChanges=0,currentGradeDiagnosticDoesNotGrantTypedGroundRoot=True,foundationInterpretationAccepted=False,currentAcceptance=False)
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha,**cache[sha]));save(LOCAL/('completed-'+mode+'.json.gz'),dict(row=rows[-1],sourceOnly=True,currentAcceptance=False));print(json.dumps(dict(arithmetic=mode,all109ExactSteepWallsHaveCapPaths=rows[-1]['strictCapPathDiagnostic']['allAffectedHavePaths'],rawExposureFailures=len(rows[-1]['strictCapPathDiagnostic']['rawExposureFailures']),gradeContacts=len(rows[-1]['complete5297CurrentGradeContactInventory']['contacts']))),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeActualCandidateGroundSHA256=digest(ground.tobytes()),all132RawFiniteFailuresRetained=True,completeCurrentManifestSHA256=digest(before),historicalSourceWorldsOnlyExactCurrentTupleBound=True,terrainReplacementProposed=True,terrainProposalNotInstalled=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['evangel_college_original_wing_extension_identity_20261011.py','evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py']);failure_archive=BASE/'government-xl-evangel-college-91306-current-grade-v2-failure-archive-20261011';refs.extend(p for p in failure_archive.rglob('*')if p.is_file());refs.append(HERE/'xl-evangel-college-91306-current-four-body-grade-paths-v2-20261011.py');refs.append(DOC/'diagnostic.json.gz');refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 s=importlib.util.spec_from_file_location('evangel_authentic_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'four-original-body-exact109-steep-wall-paths-and20-lower-cap-closure-diagnostic-no-typed-root-credit',refs,dict(uids=[UID],all132RawFailuresRetained=True,currentAcceptance=False,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 # Full manifest routing/schema prerequisites before claiming or mathematics.
 for folder in [INPUT,PHYSICAL,COMPARE,GRAPH,PREVIOUS_GRADE]:
  for pin in read(folder/'result.json')['evidenceRefs']:
   p=source_proposal_pin_path(pin)if folder in [INPUT,GRAPH]else ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256']
 f=read(COMPARE/'diagnostic.json.gz');assert len(f['rows'])==4 and all('currentDrawn'in r['failedFacesByGround']and len(r['complete13960FaceComparisons'])==13960 for r in f['rows'])
 assert read(PHYSICAL/'diagnostic.json.gz')['all17CurrentActorGuardsRetained']
 claim=reservations.claim('evangel-current-candidate-grade-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
