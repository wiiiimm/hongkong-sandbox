"""DRAFT Nam-specific saved mainbody/BASIC join and exact assembly paths.
Existing finite contact/closed-AABB kernels; no contact/grade/prism replay.
No engineering, whole-BASIC, physical or installation approval.
"""
import argparse,json,subprocess,sys,uuid,itertools
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from nam_fung79099_actual_basic45779_full_owned_finite_role_context_draft_v1_20261012 import inputs as prior_inputs,CAP,JOIN,UIDS,PROTECTED,MANIFEST_SHA,SOURCE,ref,module,state,native
from west_wing26195_complete_cross_body_candidates_draft_v1_20261012 import candidates
from west_wing26195_remaining_bodies_conditional_typed_graph_draft_v2_20261012 import conditional_paths
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points,dimension
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nam-fung79099-source-bound-basic-mainbody-interbody-role-v1-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
FINITE=B/'government-xl-nam-fung79099-actual-basic45779-full-owned-finite-role-context-v1-20261012';FINITE_SHA='e9078f53a1eb50fdc6fda5282934bd5ed7e9fcb712a737931c833cdd425ad73a'
PROPOSAL=B/'government-xl-nam-fung79099-source-bound-basic-mainbody-interbody-role-proposal-v1-20261012';FREEZER=HERE/'nam_fung79099_freeze_source_bound_basic_mainbody_interbody_role_draft_v1_20261012.py';MAX_PAIRS=1000000;CHUNK=2048

def pins():
 p=read(PROPOSAL/'executable-pins.json');assert p['caller']==ref(Path(__file__))
 for e in p['boundInputs']:assert ref(ROOT/e['path'])==e,e
 return [ref(PROPOSAL/'executable-pins.json'),p['caller']]+p['boundInputs']

def inputs():
 bound=pins();_,capture,join,scope,before,selections,prior=prior_inputs();receipt=read(FINITE/'result.json');assert ref(FINITE/'result.json')['sha256']==FINITE_SHA
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e,e
 f=read(FINITE/'diagnostic.json.gz');assert f['uid']==UIDS[0]and f['sourceSHA256']==SOURCE and f['completeFaces']==13061 and f['genuineOriginalBodyObligations']==569 and f['zeroOriginalFaceObligations']==75 and f['originalBodyCensus']==prior['originalCensus']and f['currentManifest']==scope['currentManifest']and f['currentNativeCount']==6649
 assert set(f['allFourStreamBindings'])=={'original','literal','explicitLeftF32','explicitBalancedF32'}
 for sh,p in f['distinctCompleteFiniteProofs'].items():assert len(p['allWholeFacetProofs'])==13061 and p['ordinaryFailingFaces']==p['coverageFailingFaces']==[]
 return bound,capture,join,receipt,scope,before,selections,prior,f

def mainbody_saved_facts(prior,finite):
 assert prior['uid']==finite['uid']==UIDS[0]and prior['sourceSHA256']==finite['sourceSHA256']==SOURCE
 bodies=prior['originalCensus']['sharedEdgeConnectedComponents'];main=bodies[0];assert len(bodies)==569 and len(main)==1601
 strict=set(prior['strictPositiveCaps']);routes=prior['qualifiedGradeWallWholeEdgeCapRoutes'];qualified={r['cap']for r in routes};assert len(routes)==109 and len(qualified)==62 and qualified<=strict
 rows={}
 for sh,fp in finite['distinctCompleteFiniteProofs'].items():
  saved=prior['distinctSourcePrismContactProofs'][sh];assert saved['actualBodyCensus']['sharedEdgeConnectedComponents'].count(main)==1 and saved['actualBodyCensus']['completeWorldTrianglesSHA256']==sh
  proofs=fp['allWholeFacetProofs'];assert all(proofs[i]['ordinaryFiniteProved']for i in main)
  indices=[j for j,c in enumerate(saved['completeSourceBasicFiniteContacts']['contacts'])if c['sourceFaceA']in main and c['sourceFaceB']in qualified and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
  assert len(indices)==41
  rows[sh]=dict(completeMainbodySourceFaces=main,genuineActualNonzeroSharedEdgeComponentBound=True,positiveMainbodyQualifiedCapContactRecordIndices=indices,allQualifiedCapOriginalGradeRouteRecordIndices=[j for j,r in enumerate(routes)if r['cap']in {saved['completeSourceBasicFiniteContacts']['contacts'][i]['sourceFaceB']for i in indices}],mainbodyBelowTopSourceFaceIds=[r['sourceFace']for r in saved['completeSourcePartition']if r['originalBody']==0 and r['belowTopFragment']],mainbodyExteriorBelowTopResidueSourceFaceIds=[r['sourceFace']for r in saved['completeSourcePartition']if r['originalBody']==0 and r['exteriorBelowTopFragments']],everyMainbodyOrdinaryClear=True,strictWarnings=[i for i in main if not proofs[i]['strictPositiveFiniteProved']],mainbodyGeometricCarrierCandidateReady=True,sourceSpecificInterpretationProposedNotAccepted=True,actualIndependentRootAccepted=False)
 return dict(uid=UIDS[0],sourceSHA256=SOURCE,carrierUID=PROTECTED,availabilityOnly=True,wholeBASICReaccepted=False,governmentOriginalPodiumUsed=False,originalBody=0,completeMainbodyFaces=1601,qualifiedMainbodyFactsByExactWorld=rows,sourceInterpretation=read(PROPOSAL/'source-bound-mainbody-interpretation-proposal.json'),rootAccepted=False,physicalAccepted=False)

def record(world,i,j,labels,original_zero,actual_zero,cache):
 for k in [i,j]:
  if k not in cache:cache[k]=rational_face(world[k])
 a,b=cache[i],cache[j];pts=sorted(finite_intersection_points(a,b))
 if not pts:return None
 da,db=dimension(a),dimension(b);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));cop=da==db==2 and not any(cross(na,nb))and all(dot(na,sub(p,a[0]))==0 for p in b);measure=contact_measure(pts);mid=tuple(sum(p[k]for p in pts)/len(pts)for k in range(3));inside=da==db==2 and not cop and measure['dimension']>0 and relative_interior(a,mid)and relative_interior(b,mid)
 return dict(sourceFaces=[i,j],originalBodyLabels=[int(labels[i])if labels[i]<569 else None,int(labels[j])if labels[j]<569 else None],originalNonrenderingSourceFlags=[i in original_zero,j in original_zero],actualNonrenderingSourceFlags=[i in actual_zero,j in actual_zero],actualFinitePrimitiveDimensions=[da,db],coplanar=cop,bothRelativeInteriorSurfaceCrossing=inside,**measure)

def typed_graph(records,body_count=569,terminal_bodies=()):
 usable=[];indices=[];rejected=[]
 for i,r in enumerate(records):
  reason='authored-zero-source-no-bridge'if any(r['originalNonrenderingSourceFlags'])else'actual-nonrendering-no-bridge'if any(r['actualNonrenderingSourceFlags'])else'point-only-no-bridge'if r['dimension']==0 else None
  if reason:rejected.append(dict(savedContactIndex=i,reason=reason));continue
  usable.append(r);indices.append(i)
 result=conditional_paths(usable,body_count=body_count,conditional_root=0,visual_only=terminal_bodies)
 return dict(conditionalGraph=json.loads(json.dumps(result,allow_nan=False)),rawContactIndicesForFilteredGraph=indices,rejectedRawContacts=rejected,allProperInteriorContactIndicesRetained=[i for i,r in enumerate(records)if r['bothRelativeInteriorSurfaceCrossing']],categoricalInteriorExclusion=False,terminalBodiesNonbridging=list(terminal_bodies),root0IsExactCarrierCandidateNotAcceptedRoot=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');p.add_argument('--preflight-only',action='store_true');a=p.parse_args();bound,capture,join,receipt,scope,before,selections,prior,finite=inputs();mainbody=mainbody_saved_facts(prior,finite)
 if a.preflight_only:print(json.dumps(dict(savedMainbody41InterfacesRebound=True,allCompletedPriorReferencesAndCurrentPinsPassed=True,noWorker=True)));return
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('nam-source-mainbody-assembly-'+str(uuid.uuid4()),['building:'+u for u in UIDS+[PROTECTED]],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not(DOC/'diagnostic.json.gz').exists();walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','nam_assembly_closure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)];receiptpins=[ref(CAP/'result.json'),ref(JOIN/'result.json'),ref(FINITE/'result.json')]
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
  for e in codes+bound+receiptpins:assert ref(ROOT/e['path'])==e,e
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selections),default=str))==read(CAP/'native-source-state-before.json')['rows']
 fence();attrs=read(CAP/'actual-render-geometry.json.gz')['rows'][0];index=np.asarray(attrs['completeOriginalIndex']).reshape(-1,3);original=np.asarray(read(CAP/'original-full-source-root-context.json.gz')['rows'][0]['completeOriginalBinary64WorldTriangles'],dtype='<f8');worlds={'original':original}
 for mode,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attrs[key],dtype='<f8').reshape(-1,3)[index]
 bodies=prior['originalCensus']['sharedEdgeConnectedComponents'];zero=prior['originalCensus']['exactNonrenderingOriginalFaces'];partition=bodies+[[i]for i in zero];assert sorted(i for ids in partition for i in ids)==list(range(13061));results={};chunkrefs=[]
 for mode,world in worlds.items():
  sh=digest(world.tobytes());assert sh==finite['allFourStreamBindings'][mode]['wholeWorldSHA256']
  if sh in results:continue
  pairs,labels=candidates(world,partition);assert len(pairs)<=MAX_PAIRS,'Explicit actual closed-AABB pair resource bound';pairsha=digest(json.dumps(pairs,separators=(',',':')).encode());actualzero=set(prior['distinctSourcePrismContactProofs'][sh]['actualBodyCensus']['exactNonrenderingOriginalFaces']);cache={};contacts=[]
  for start in range(0,len(pairs),CHUNK):
   stop=min(start+CHUNK,len(pairs));path=LOCAL/'chunks'/sh/f'{start:07d}-{stop:07d}.json.gz';contract=dict(worldSHA256=sh,completeSourceFaces=13061,originalBodies=569,originalZeros=75,candidatePairs=len(pairs),candidatePairListSHA256=pairsha,firstPair=start,exclusiveLastPair=stop,codeRefs=codes,proposalRefs=bound);fence()
   if path.exists():chunk=read(path);assert chunk['contract']==contract
   else:
    rows=[r for i,j in pairs[start:stop]if(r:=record(world,i,j,labels,set(zero),actualzero,cache))is not None];chunk=dict(contract=contract,pairs=[list(x)for x in pairs[start:stop]],contacts=rows);temp=path.with_name(path.name+'.pending.json.gz');save(temp,chunk);assert read(temp)==chunk;temp.replace(path)
   assert chunk['pairs']==[list(x)for x in pairs[start:stop]];contacts+=chunk['contacts'];chunkrefs.append(ref(path));fence();assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(mode=mode,completedPairs=stop,totalPairs=len(pairs),contacts=len(contacts))),flush=True)
  assert len({tuple(r['sourceFaces'])for r in contacts})==len(contacts);counts=Counter(tuple(sorted(r['originalBodyLabels']))for r in contacts if None not in r['originalBodyLabels']);graph=typed_graph(contacts);roles=[];paths_by_body=graph['conditionalGraph']['conditionalPositiveDimensionalContactPaths']
  for body,ids in enumerate(bodies):
   path=paths_by_body.get(str(body));roles.append(dict(originalBody=body,completeOriginalFaceIds=ids,roleCandidate='source-bound-mainbody-basic-join'if body==0 else'source-assembly-positive-dimensional-path'if path else'authored-disconnected-detail-source-context-and-mount-evidence-needed',conditionalSourcePath=path,structuralVersusTerminalInterpretation='not-engineering; terminal classification requires body-specific original evidence',terminalRoleAccepted=False,structuralSupportAccepted=False,independentGroundRootRequiredForEveryDetail=False))
  results[sh]=dict(worldSHA256=sh,completeClosed3DAABBCandidatePairs=len(pairs),candidatePairListSHA256=pairsha,allExactCrossBodyContacts=contacts,allOriginalBodyPairCount=161596,bodyPairContactCounts=[dict(originalBodies=[i,j],contactCount=counts.get((i,j),0))for i,j in itertools.combinations(range(569),2)],typedGraph=graph,all569BodyRoleCandidates=roles,all75AuthoredZeroFacesNoRootOrBridge=zero,actualWorldZeroFaceIds=sorted(actualzero),terminalBodySourceBindingsNotInvented=True);save(LOCAL/('completed-'+mode+'.json.gz'),results[sh])
 fence();save(DOC/'diagnostic.json.gz',dict(uid=UIDS[0],sourceSHA256=SOURCE,carrierUID=PROTECTED,currentManifest=scope['currentManifest'],currentNativeCount=6649,completeFaces=13061,completeOriginalBodies=569,originalZeroFaces=75,allFourStreamBindings=finite['allFourStreamBindings'],mainbodySavedCarrierFacts=mainbody,distinctInterbodyRoleContexts=results,sourceOnly=True,finiteContactPrismGradeArithmeticReplayed=False,sourceGeometryChanges=0,terrainGeometryChanges=0,wholeBASICReaccepted=False,originalGovernmentPodiumUsed=False,rootAccepted=False,bodySupportAccepted=False,physicalAccepted=False,installationApproved=False,fullIdentityForeignNativeFoundationRuntimeGatesStillIndependent=True,evidenceRefs=bound+codes+receiptpins+[ref(JOIN/'diagnostic.json.gz'),ref(FINITE/'diagnostic.json.gz')]+chunkrefs));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
