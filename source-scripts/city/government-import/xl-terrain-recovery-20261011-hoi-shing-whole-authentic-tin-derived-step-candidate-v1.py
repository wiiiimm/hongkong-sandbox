"""DRAFT source-only derived TIN, NEVER execute before root method review.

Explicit altered terrain: duplicateXYZ corrections across entire177048-facet
authentic sheet, complete incident/seam/exterior certificate and all72 exact
source-facet replays. Gov source/TIN remain immutable. No current final proposal,
foreign acceptance, original-building geometry, root, staged or live change.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,time,uuid,sys
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_tin_shared_vertex_lowering_diagnostic_v1_20261011 import verify as incident,sha
from exact_original_paired_finite_clearance_v2_20261010 import verify as paired
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-whole-authentic-tin-derived-step-candidate-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1';FIT=BASE/'xl-terrain-recovery-20261011-hoi-shing-nine-upward-exact-terrain-feasibility-v2';PRIMARY=BASE/'government-xl-hoi-shing-exact-72-face-primary-step-association-v1-20261011';PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
SOURCES={'landsd/318801:0':('fc22e0aa4c2869e520e0336fb3e2ef1d6f1bb246529824af010465bb382e0e55',13841),'landsd/318830:0':('cb52942f086f38d8d95a346e83538003c90f9aaa772811ac13d3485e1ae27b7f',5533)}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert sys.argv[1:]==['--generate-source-only-derived-candidate'],'Explicit reviewed source-only generation is required';assert not DOC.exists()and not LOCAL.exists();refs=[ref(Path(__file__))];bound={}
 for folder in [TIN,FIT,PRIMARY]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert ref(folder/'diagnostic.json.gz')in r['evidenceRefs'];bound.update({p['path']:p for p in r['evidenceRefs']});refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 fit=read(FIT/'diagnostic.json.gz');assert fit['exactPostSolverConstraintFeasible']and not fit['terrainProposalAssetCreated']and fit['allNineOriginalFailureFaces']==[3261,3262,3263,3264,3265,3266,3267,3272,3273]
 gfile=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';g=read(gfile);assert ref(gfile)==bound[str(gfile.relative_to(ROOT))];refs.append(ref(gfile));decoder=module('hoi_whole_tin_source_decode','xl-second-pass.py');pieces=[]
 for entry in g['sourceTerrainReceipt']['terrainFiles']:
  matches=[ROOT/p['path']for p in read(TIN/'result.json')['evidenceRefs']if p['path'].endswith('/terrain/'+entry['name'])];assert len(matches)==1;path=matches[0];assert ref(path)==bound[str(path.relative_to(ROOT))];refs.append(ref(path))
  if entry['name'].endswith('.gltf'):pieces.append(decoder.terrain_triangles(path))
 old=np.concatenate(pieces);assert old.shape==(g['completeOriginalSheetFacets'],3,3)and len(old)==177048 and sha(old)==g['completeOriginalSheetFacetSHA256'];subset=np.asarray(g['sourceCoveringWholeFacetIds'],np.int64);oldselected=old[subset];assert np.array_equal(oldselected,np.asarray(g['completeSelectedFacets'],float))and sha(oldselected)==fit['completeImmutableAuthenticTINSelectedGroundSHA256'];derived=old.copy();changes=[]
 for correction in fit['hypotheticalVertexCorrections']:
  if F(correction['exactDownwardDeltaM'])==0:continue
  vertex=np.asarray(correction['originalWholeXYZ'],float);mask=np.all(old==vertex,axis=2);assert mask.any();derived[:,:,1][mask]=correction['hypotheticalFloat32Y'];assert int(mask.sum())>=correction['numberOfExactOriginalDuplicateVertexRecords'];changes.append(dict(originalXYZ=vertex.tolist(),hypotheticalY=correction['hypotheticalFloat32Y'],completeWholeSheetDuplicateRecords=int(mask.sum()),oldSelectedDuplicateRecords=correction['numberOfExactOriginalDuplicateVertexRecords']))
 binding=dict(completeOriginalGroundSHA256=sha(old),completeDerivedGroundSHA256=sha(derived),completeOriginalTerrainReceipt=ref(TIN/'result.json'),exactNominationReceipt=ref(FIT/'result.json'));certificate=incident(old,derived,expected_binding=binding,current_binding=binding);assert len(changes)==17
 # Recheck EVERY exact solver constraint against actual whole-sheet values.
 newselected=derived[subset];constraint_rows=[]
 for r in fit['allExactAffineConstraints']:
  gi=r['selectedGroundFace'];weights=[F(v)for v in r['exactColumnVertex']['exactGroundBarycentricWeights']];source_y=F(r['exactColumnVertex']['exactSourcePoint'][1]);ground_y=sum(w*F(float(newselected[gi,k,1]))for k,w in enumerate(weights));gap=source_y-ground_y;assert gap>=-F(.5);constraint_rows.append(dict(sourceFace=r['sourceFace'],selectedGroundFace=gi,wholeOriginalSheetFace=int(subset[gi]),exactDerivedGapM=str(gap),existingOrdinaryBoundProved=True))
 selected=read(PROBE/'selection.json.gz');assert {r['uid']for r in selected['rows']}==set(SOURCES);worlds={};oldproof=read(TIN/'diagnostic.json.gz')
 for row in selected['rows']:
  expected,count=SOURCES[row['uid']];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==expected;world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(count,3,3);prior=next(r for r in oldproof['rows']if r['uid']==row['uid']);assert prior['completeOriginalWorldSHA256']==sha(world)and len(prior['allFaces'])==count;worlds[row['uid']]=world;refs.append(ref(asset))
 primary=read(PRIMARY/'diagnostic.json.gz');world=worlds['landsd/318830:0'];ids=primary['completeOriginalPartFaceIds'];assert len(ids)==72 and len(set(ids))==72 and np.array_equal(world[ids],np.asarray(primary['completeOriginalPartTriangles'],float));refs.extend(ref(p)for p in [PROBE/'selection.json.gz',HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_tin_shared_vertex_lowering_diagnostic_v1_20261011.py',HERE/'test_exact_original_tin_shared_vertex_lowering_diagnostic_v1_20261011.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']);claim=reservations.claim('hoi-whole-derived-source-candidate-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 try:
  for fi in ids:
   proof=paired(world[fi],newselected);rows.append(dict(sourceFace=fi,completeOriginalFaceSHA256=sha(world[fi]),exactDerivedGroundFiniteProof=proof))
   if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(completeOriginal72FacesRefined=len(rows),total=72)),flush=True)
  assert all(r['exactDerivedGroundFiniteProof']['existingOrdinaryClearanceBoundProved']for r in rows if r['sourceFace']in fit['allNineOriginalFailureFaces']);assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/p['path'])==p for p in refs)
  # The ONLY new geometry output is an adjacent derived source-only terrain
  # artifact. No original glTF/BIN, catalogue, current patch or building changes.
  output=LOCAL/'whole-derived-authentic-sheet-triangles.json.gz';save(output,dict(triangles=derived.tolist(),completeOriginalFacets=len(old),originalGroundSHA256=sha(old),derivedGroundSHA256=sha(derived),explicitAlteredTerrain=True,originalTerrainReceipt=ref(TIN/'result.json'),sourceOnly=True,noCurrentOrDeployableTerrainProposal=True))
  out=dict(uids=sorted(SOURCES),completeOriginalBuildingFaces=19374,completeImmutableOriginalTINFacets=len(old),explicitDerivedTerrainArtifact=ref(output),fullOriginalTINIncidentExteriorAndSeamProof=certificate,completeWholeSheetDuplicateCorrectionInventory=changes,all949ConstraintPackedGroundReplays=constraint_rows,all72OriginalStepFeaturePairedProofs=rows,remaining72OrdinaryFailures=[r['sourceFace']for r in rows if not r['exactDerivedGroundFiniteProof']['existingOrdinaryClearanceBoundProved']],allOther19374ClearanceCanOnlyImproveByExactWholeFacetHeightLowering=True,oldWholePTProofAndRemainingFailuresPreserved=ref(TIN/'diagnostic.json.gz'),wholeCurrentPTForeignRuntimeRootAndActualRenderStillUntested=True,sourceOnly=True,buildingGeometryRootPoseChanges=0,originalGovernmentTINFilesChanged=False,derivedTerrainGeometryChanged=True,unchangedGovernmentTINCredit=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  freeze=module('freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'whole177048-authentic-tin-derived-step-terrain-candidate-source-only-v1',[ROOT/p['path']for p in refs]+[output,DOC/'diagnostic.json.gz'],dict(uids=sorted(SOURCES),derivedTerrainGeometryChanged=True,sourceOnly=True,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(derivedTerrainOnly=True,complete72=len(rows),remaining72=out['remaining72OrdinaryFailures'],wholeSheetOriginalFacets=len(old))),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
