"""Complete original upper opening loops versus original host undersides.

Source-only fixed-band proximity diagnosis. Prior zero contacts and both roof
loop failures stay negative. No cap, function, load path, role or root credit.
Historical sampled host reachability is explicitly not host qualification.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-hoi-shing-eleven-open-wall-upper-underside-band-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
RIM=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1'
PRIOR=BASE/'xl-terrain-recovery-20261011-hoi-shing-eleven-open-wall-roof-loops-context-v1'
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
UID='landsd/318830:0';BODIES=[78,125,129,133,136,137,138,139,141,142,144]

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [GRAPH,RIM,PRIOR,PROBE]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');rim=bound(RIM,RIM/'diagnostic.json.gz');old=bound(PRIOR,PRIOR/'diagnostic.json.gz')
 selected=bound(PROBE,PROBE/'selection.json.gz');sources=[]
 assert [r['uid']for r in selected['rows']]==['landsd/318801:0',UID]
 for row in selected['rows']:
  p=ROOT/row['candidate']['path'];assert ref(p)['sha256']==row['sourceSHA256'];sources.append(decode_original_world_triangles(p.read_bytes()));refs.append(ref(p))
 world=np.concatenate(sources)
 assert world.shape==(19374,3,3)and digest(world.tobytes())==graph['binding']['completeOriginalWorldSHA256']==old['complete19374OriginalWorldSHA256']
 hosts=[b for b in rim['sourceOnlyDerivedGroundReachedBodies']if graph['components'][b]['actorUID']==UID]
 assert hosts==old['conditionalSourceOnlyHostBodies']and not set(hosts)&set(BODIES)
 hostfaces=sorted(fi for b in hosts for fi in graph['components'][b]['globalOriginalFaces'])
 normals=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);undersides=[fi for fi in hostfaces if normals[fi,1]<0]
 assert undersides and len(undersides)==len(set(undersides))
 surface=world[undersides]
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('hoi-upper-underside-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  for body in BODIES:
   prior=next(r for r in old['rows']if r['originalBody']==body);ids=graph['components'][body]['globalOriginalFaces'];tri=world[ids]
   assert ids==prior['completeOriginalGlobalFaces']and len(ids)==8 and digest(tri.tobytes())==prior['completeBodySHA256']
   assert all(normals[fi,1]==0 for fi in ids)
   loop=next(r for r in prior['bothCompleteOriginalOpeningLoops']if r['name']=='entire-original-upper-opening')
   assert len(loop['allFourOriginalOpeningEdges'])==4 and not loop['conditionalEntireOriginalLoopWithinExistingBand']
   proofs=[]
   for edge in loop['allFourOriginalOpeningEdges']:
    proof=verify(np.asarray(edge,float),surface)
    proofs.append(dict(completeOriginalUpperEdge=edge,completeAllOrientationFiniteDistanceProof=proof));pulse()
   rows.append(dict(originalBody=body,completeOriginalGlobalFaces=ids,completeBodySHA256=digest(tri.tobytes()),entireOriginalUpperOpeningEdges=loop['allFourOriginalOpeningEdges'],allFourCompleteFiniteEdgeProofs=proofs,conditionalWholeUpperLoopWithinExistingUndersideBand=all(p['completeAllOrientationFiniteDistanceProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in proofs),previousRoofLoopResultVerbatim=prior['bothCompleteOriginalOpeningLoops'],allOriginalZeroContactNegativesPreserved=True,hostQualification=False,roleAssigned=False,structuralRootOrBridgeCredit=False))
   print(dict(body=body,upperUndersideBand=rows[-1]['conditionalWholeUpperLoopWithinExistingUndersideBand']),flush=True)
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[r['uid']for r in selected['rows']],rows=rows,complete19374OriginalWorldSHA256=digest(world.tobytes()),completeConditionalHistoricalHostBodies=hosts,completeOriginalHostFaces=hostfaces,completeOriginalDownwardHostFaceInventory=undersides,completeDownwardHostWorldSHA256=digest(surface.tobytes()),sourceOnly=True,historicalHostSampledReachabilityIsNotQualification=True,explicitDerivedGroundUndeployed=True,allElevenOriginal88WallFacesPreserved=True,strictBandM=.1,sourceGeometryChanges=0,generatedCaps=0,roleAssigned=False,currentAcceptance=False,hostQualification=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze_hoi_upper_underside',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'eleven-complete-original-upper-loops-finite-underside-band-source-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,hostQualification=False,roleAssigned=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
