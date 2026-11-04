"""Source-only affine feasibility for nine genuine mapped-step TIN failures.

Keeps gov source/root/pose and original TIN immutable. Solver numbers are an
explicit hypothetical ALTERED TERRAIN experiment, not unchanged-TIN acceptance.
Every finite column-polytope vertex is independently exact-rechecked. No mesh,
proposal asset, live terrain, mounting, root or installation is generated.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,time,uuid,math
import numpy as np
import scipy
from scipy.optimize import linprog
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as column
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-nine-upward-exact-terrain-feasibility-v2';DOC=BASE/BATCH
TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1';REFINE=BASE/'xl-terrain-recovery-20261011-hoi-shing-podium-authentic-tin-upward-refinement-v1';PRIMARY=BASE/'government-xl-hoi-shing-exact-72-face-primary-step-association-v1-20261011';PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
UID='landsd/318830:0';SOURCE='cb52942f086f38d8d95a346e83538003c90f9aaa772811ac13d3485e1ae27b7f';FACES=[3261,3262,3263,3264,3265,3266,3267,3272,3273]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);failure=DOC/'failed-v1-missing-solver-import.log';failure.write_bytes(Path('/tmp/hoi-shing-nine-upward-exact-terrain-feasibility-v1-20261011.log').read_bytes());refs=[ref(Path(__file__)),ref(HERE/'xl-terrain-recovery-20261011-hoi-shing-nine-upward-exact-terrain-feasibility-v1.py'),ref(failure)];bound={}
 for folder in [TIN,REFINE,PRIMARY]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  bound.update({p['path']:p for p in r['evidenceRefs']});assert ref(folder/'diagnostic.json.gz')in r['evidenceRefs'];refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 primary=read(PRIMARY/'diagnostic.json.gz');refined=read(REFINE/'diagnostic.json.gz');assert primary['sourceSHA256']==refined['sourceSHA256']==SOURCE and primary['allNineUpwardFailureFaceIds']==refined['remainingTrueUpwardClearanceFailures']==FACES
 row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==SOURCE;world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(5533,3,3)and digest(world.tobytes())==primary['completeOriginalWorldSHA256']==refined['completeOriginalWorldSHA256']
 groundfile=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';g=read(groundfile);ground=np.asarray(g['completeSelectedFacets'],float);assert digest(ground.tobytes())==g['completeSelectedFacetSHA256']==refined['completeOriginalTINSelectedGroundSHA256'];assert ref(groundfile)==bound[str(groundfile.relative_to(ROOT))]
 refs.extend(ref(p)for p in [asset,groundfile,PROBE/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('hoi-nine-immutable-affine-feasibility-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();pairs=[];constraints=[];variables={}
 try:
  for fi in FACES:
   source=world[fi];normal=np.cross(source[1]-source[0],source[2]-source[0]);assert normal[1]>0
   candidate=np.flatnonzero((ground[:,:,0].max(1)>=source[:,0].min())&(ground[:,:,0].min(1)<=source[:,0].max())&(ground[:,:,2].max(1)>=source[:,2].min())&(ground[:,:,2].min(1)<=source[:,2].max()));records=[]
   for gi in candidate:
    proof=column(source,ground[gi]);records.append(dict(selectedGroundFace=int(gi),wholeOriginalSheetFace=g['sourceCoveringWholeFacetIds'][gi],exactFinitePair=proof))
    for v in proof['allExactBasicFeasibleColumnVertices']:
     weights=[F(x)for x in v['exactGroundBarycentricWeights']];terms={}
     for k,w in enumerate(weights):
      if not w:continue
      key=tuple(float(x)for x in ground[gi,k]);index=variables.setdefault(key,len(variables));terms[index]=terms.get(index,F(0))+w
     assert sum(terms.values())==1;constraints.append(dict(sourceFace=fi,selectedGroundFace=int(gi),exactWeightsByVertex={str(k):str(w)for k,w in terms.items()},originalExactGapM=v['exactGapM'],requiredWeightedDownwardCorrectionM=str(-F(.5)-F(v['exactGapM'])),exactColumnVertex=v))
    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(sourceFace=fi,finitePairs=len(records),constraints=len(constraints))),flush=True)
   pairs.append(dict(sourceFace=fi,allClosedAABBCandidateGroundFaces=candidate.tolist(),everyCandidateAccounted=True,finitePairs=records))
  assert variables and constraints
  # Float solver only nominates values. Exact Fraction replay decides feasibility.
  a=np.zeros((len(constraints),len(variables)));rhs=[]
  for i,r in enumerate(constraints):
   for k,w in r['exactWeightsByVertex'].items():a[i,int(k)]=-float(F(w))
   rhs.append(-float(F(r['requiredWeightedDownwardCorrectionM'])))
  cap=F(.65);fit=linprog(np.ones(len(variables)),A_ub=a,b_ub=np.asarray(rhs),bounds=[(0,float(cap))]*len(variables),method='highs');certificate=[];deltas={};violations=[]
  if fit.success:
   byindex={i:p for p,i in variables.items()}
   for i,value in enumerate(fit.x):
    assert math.isfinite(value)
    q=F(math.ceil(max(0,float(value))*65536),65536);p=byindex[i];old=F(p[1]);target=old-q
    if q:
     packed=np.float32(float(target))
     if F(float(packed))>target:packed=np.nextafter(packed,np.float32(-np.inf),dtype=np.float32)
     new=F(float(packed))
    else:new=old
    delta=old-new;deltas[i]=delta;certificate.append(dict(variable=i,originalWholeXYZ=list(p),hypotheticalFloat32Y=float(new),exactDownwardDeltaM=str(delta),withinHypotheticalCap=0<=delta<=cap,numberOfExactOriginalDuplicateVertexRecords=int(np.all(ground==np.asarray(p),axis=2).sum())))
   for r in constraints:
    value=sum(F(w)*deltas[int(i)]for i,w in r['exactWeightsByVertex'].items());valid=value>=F(r['requiredWeightedDownwardCorrectionM']);r['exactReplayedWeightedDeltaM']=str(value);r['exactConstraintSatisfied']=valid
    if not valid:violations.append(r)
  certified=bool(fit.success and not violations and all(r['withinHypotheticalCap']for r in certificate));assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/p['path'])==p for p in refs)
  out=dict(uid=UID,sourceSHA256=SOURCE,allNineOriginalFailureFaces=FACES,completeMapped72FaceInventory=ref(PRIMARY/'diagnostic.json.gz'),complete5533OriginalWorldSHA256=digest(world.tobytes()),completeImmutableAuthenticTINSelectedGroundSHA256=digest(ground.tobytes()),allNineCompleteFinitePairInventories=pairs,allExactAffineConstraints=constraints,solver=dict(success=bool(fit.success),status=int(fit.status),message=fit.message,nominationOnly=True,scipyVersion=scipy.__version__,numpyVersion=np.__version__),hypotheticalVertexCorrections=certificate,maximumHypotheticalCorrectionM=str(max(deltas.values(),default=F(0))),fixedExistingOrdinaryClearanceM=-.5,explicitHypotheticalCorrectionCapM=str(cap),exactPostSolverConstraintFeasible=certified,exactConstraintViolations=violations,hypotheticalAlteredTerrainNotUnchangedGovernmentTIN=True,originalSourceGeometryRootPoseChanges=0,originalTINFilesChanged=False,terrainProposalAssetCreated=False,allOtherTINVerticesRemainUnchangedInExperiment=True,currentForeignSeamsRuntimeWholeSourcesStillUntested=True,physicalAccepted=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'hoi-nine-original-mapped-step-affine-altered-terrain-feasibility-only-v2',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],allNineTrueFailuresPreserved=True,exactHypotheticalConstraintFeasible=certified,maximumHypotheticalCorrectionM=out['maximumHypotheticalCorrectionM'],terrainProposalAssetCreated=False,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(feasible=certified,variables=len(variables),constraints=len(constraints),maximumHypotheticalDeltaM=out['maximumHypotheticalCorrectionM'])),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
