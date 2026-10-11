"""DRAFT complete actual native footprints and bounded source-step JSON nomination."""
import json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded,encoded
from exact_faithful_source_step_junction_feasibility_v2_20261011 import project,native_footprints,native_query_inventory,whole_actual_source_edge,bounded_outer_corner_ray,vertical_junction
from exact_compute_transition_mesh_v1_20261011 import height,contains
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon
from exact_original_projection_coverage_v2_20261010 import signed_area
P='government-xl-mongkok-stadium240332-';B=ROOT/'docs/astra-city/government-import';ATTR=B/(P+'first-upper-boundary-discontinuity-attribution-v1-20261011');OLD=B/(P+'faithful-multisurface-transition-candidate-v2-20261011');ATOMS=B/(P+'complete-bounded-source3d-atoms-three-join-integration-v1-20261011');DOC=B/(P+'actual-f32-source-step-junction-feasibility-v2-20261011')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
VALIDATION=B/(P+'actual-f32-source-step-junction-feasibility-v2-20261011-validation')
VALIDATED_CODE_NAMES=['exact_faithful_source_step_junction_feasibility_v2_20261011.py', 'test_exact_faithful_source_step_junction_feasibility_v2_20261011.py', 'mongkok_stadium240332_actual_f32_source_step_junction_feasibility_v2_20261011.py', 'mongkok_stadium240332_freeze_actual_f32_source_step_junction_feasibility_v2_20261011.py']
def validation_gate():
 v=read(VALIDATION/'validation.json');assert v['testsRun']==15 and v['failures']==v['errors']==0 and v['exitCode']==0 and v['passed']is True
 assert v['testModule']=='test_exact_faithful_source_step_junction_feasibility_v2_20261011'
 assert v['log']==ref(VALIDATION/'tests.log');assert len(v['codeRefs'])==4 and v['codeRefs']==[ref(HERE/n)for n in VALIDATED_CODE_NAMES]
 log=(VALIDATION/'tests.log').read_text();assert 'Ran 15 tests' in log and log.rstrip().endswith('OK')
 return [ref(VALIDATION/'validation.json'),v['log']]+v['codeRefs']
def main():
 validation_refs=validation_gate();assert not DOC.exists();refs=list(validation_refs)+[ref(B/(P+'actual-f32-source-step-junction-feasibility-v1-20261011-validation')/'validation.json'),ref(B/(P+'actual-f32-source-step-junction-feasibility-v1-20261011-validation')/'tests.log')]
 for folder in [ATTR,OLD,ATOMS]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert all(ref(ROOT/e['path'])==e for e in r['evidenceRefs']);refs.extend(r['evidenceRefs']);refs.append(ref(folder/'result.json'))
 inputs=read(ATTR/'runtime-inputs.json.gz');runtime=read(ATTR/'runtime-result.json.gz');a=decoded(read(ATTR/'exact-attribution.json.gz'));atoms=decoded(read(ATOMS/'diagnostic.json.gz'));domain=decoded(read(OLD/'exact-source-bound-domain.json.gz'));ground=read(OLD/'complete-current-ground-and-parent-routing.json.gz');old=decoded(read(OLD/'diagnostic.json.gz'));manifest=runtime['currentManifest'];assert manifest==inputs['currentManifest']==old['currentManifest']==ground['currentManifest']==ref(ROOT/manifest['path']);assert all(ref(ROOT/p)['sha256']==h for p,h in runtime['inputHashes'].items());assert runtime['startEndAllInputsVerified']and runtime['completeOriginalAndJoinFacets']==14801
 raw=inputs['literalOriginalSourceAndThreeJoins'];literal=np.asarray(raw['position'],dtype='<f8').reshape(-1,3,3);assert literal.shape==(14801,3,3)and raw['index']==list(range(14801*3));native=native_footprints(literal);assert digest(native['actual'].astype('<f4').tobytes())==runtime['actualSourceFloat32PositionSHA256'];assert sum(native['indexed'])==runtime['actualSourceHeightIndexedFaces'];queries=[]
 for row in runtime['queries']:
  ideal=next(x for x in inputs['queries']if x['label']==row['label']);exact_point=decoded(ideal['exactPointXZ']);literal_closed=[i for i,t in enumerate(literal[:14798])if signed_area(project(t))and contains(polygon(project(t)),exact_point)];proof=native_query_inventory(native,row['xz']);
  for nomination in proof['completeActualFiniteNominations']:
   i=nomination['face'];nomination['originalSheetAndFacetOrGeneratedJoin']=atoms['completeOriginalSourceFacetBindings'][i]if i<14798 else ['compute-only-prior-join',i-14798]
  has=bool(proof['allIndexedFiniteOwners']);returned=row['sourceOriginalAndThreeJoinProductionMAXHeight']is not None;queries.append(dict(savedProductionQuery=row,idealExactOriginalQueryXZ=exact_point,allLiteralOriginalIdealClosedOwners=literal_closed,completeActualIndexedFootprint=proof,actualCoveredButSamplerNull=has and not returned,actualNoIndexedOwnerAndSamplerNull=not has and not returned,actualFootprintPresenceMatchesProduction=has==returned,pointOnlyNotWholeSeam=True))
 branches=[]
 for row in a['allPositiveLengthIncidentBoundaryIntervals']:
  i=row['upperOwner']['selectedSourceFace'];t=row['upperOwner']['exactOriginalTriangle'];ends=[(p[0],height(t,p),p[1])for p in row['exactXZEndpoints']];branches.append(dict(originalIncidentInterval=row,literal3DEndpoints=ends,actualWholeSourceEdge=whole_actual_source_edge(native,i,*ends)))
 fail=a['allFailingClosedEndpoints'][0];p=fail['exactPointXZ'];core=[polygon(project(t))for t in literal[:14798]if signed_area(project(t))];ray=bounded_outer_corner_ray(p,domain['completeOuterBoundarySegments'],core,domain['computeBandPolygons']);junction=None;outer=[];obstruction=None
 if ray.get('noBoundedWholeBandOnlyRay'):obstruction='No finite existing outer node within10m has complete band-only ray; bounded nomination only'
 else:
  q=ray['exactRetainedOuterPointXZ'];meshes=[m for m in ground['completeGlobalActualMeshes']if m['completeFacets']==16297 and m['actualPositionAttributeSHA256']=='4a318ade67bad09734b2a87c610d432dc81021530a0ce130e3c901de2c33df95'];assert len(meshes)==1;protected=meshes[0]['meshOrdinal'];rows=[r for r in ground['completeClosedDomainAABBActualGroundFacets']if r['meshOrdinal']!=protected];current=native_footprints(np.asarray([r['actualTriangle']for r in rows],dtype='<f8').reshape(-1,3,3));proof=native_query_inventory(current,q);outer=[dict(actualFacet=rows[i],exactHeight=height(current['tri'][i],q))for i in proof['allDrawnNonzeroProjectionOwners']];ys={r['exactHeight']for r in outer}
  if len(ys)!=1:obstruction='Retained outer node has absent or conflicting exact current-plane heights; no nomination'
  else:junction=vertical_junction(p,fail['exactMaxHeight'],fail['exactOwnerEndpointHeight'],(q[0],next(iter(ys)),q[1]))
 refs.extend([ref(Path(__file__))]+[ref(p)for p in [ATTR/'runtime-inputs.json.gz',ATTR/'runtime-result.json.gz',ATTR/'exact-attribution.json.gz',OLD/'exact-source-bound-domain.json.gz',OLD/'complete-current-ground-and-parent-routing.json.gz']]);out=dict(completeOriginalAndJoinFaces=14801,completeOriginalSourceFaces=14798,completeActualHeightIndexedFaces=sum(native['indexed']),allDrawnHeightIndexExclusionFaceIDs=[i for i,v in enumerate(native['indexed'])if not v],allProductionQueriesAndCompleteActualIndexedFootprints=queries,allPositiveLengthOriginalIncidentBranches=branches,boundedWholeBandOnlyRay=ray,allRetainedOuterActualPlaneOwners=outer,computeOnlyVerticalJunctionNomination=junction,boundedObstruction=obstruction,original91CrossingsRemainUnqualified=True,innerVerticalTerminationUnpaired=True,actualWholeBranchesUnqualifiedUnlessExplicitProof=True,currentManifest=manifest,evidenceRefs=refs,noCandidate=True,noMeshOutput=True,currentAcceptance=False,sourceOnly=True,sourceGeometryChanges=0,liveTerrainChanges=0,all6645WholeRoutingActorChecksStillRequired=True)
 assert ref(ROOT/manifest['path'])==manifest and all(ref(ROOT/e['path'])==e for e in refs);save(DOC/'diagnostic.json.gz',encoded(out));print(json.dumps(dict(queries=len(queries),coveredButNull=sum(q['actualCoveredButSamplerNull']for q in queries),junctionNominated=junction is not None,obstruction=obstruction,noCandidate=True)))
if __name__=='__main__':main()
