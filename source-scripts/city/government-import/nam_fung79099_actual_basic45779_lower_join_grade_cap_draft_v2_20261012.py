"""UNEXECUTED bounded source/current BASIC geometry context; no acceptance.
Existing exact kernels only. Every lower source piece, interior flag and zero
record survives. Availability-only BASIC is not an original government support.
"""
import argparse,json,importlib.util,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,dimension
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment
from nam_fung79099_actual_basic45779_current_capture_draft_v2_20261012 import module,ref,state,native,MANIFEST_SHA,UIDS,PROTECTED
BATCH='government-xl-nam-fung79099-actual-basic45779-lower-join-grade-cap-v2-20261012';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
CAP=DOC.parent/'government-xl-nam-fung79099-actual-basic45779-current-capture-v2-20261012';CAPLOCAL=HERE/'local'/CAP.name
SOURCE='7ca5a8202c6903f0e765d4586bcbd7597a009b8a997528431c4ed3e2963362fb'

def inputs(expected_result_sha):
 receipt=read(CAP/'result.json');assert ref(CAP/'result.json')['sha256']==expected_result_sha
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 scope=read(CAP/'capture-scope.json');assert scope['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')and scope['currentManifest']['sha256']==MANIFEST_SHA
 for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 before=read(CAP/'protected-state-before.json');assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];rows=read(CAP/'selection.json.gz')['rows'];assert json.loads(json.dumps(native(rows),default=str))==read(CAP/'native-source-state-before.json')['rows']
 return receipt,scope,before,rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-capture-result-sha',required=True);p.add_argument('--owned',action='store_true');p.add_argument('--preflight-only',action='store_true');a=p.parse_args();inputs(a.expected_capture_result_sha)
 if a.preflight_only:print(json.dumps(dict(exactCompleteCaptureReferencesPassed=True,noWorker=True)));return
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('nam-fung-basic-join-'+str(uuid.uuid4()),['building:'+u for u in UIDS+[PROTECTED]],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));status=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned','--expected-capture-result-sha',a.expected_capture_result_sha],cwd=ROOT).returncode;assert status==0,status;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();receipt,scope,before,rows=inputs(a.expected_capture_result_sha)
 def fence():
  assert reservations.owns(lease);assert ref(CAP/'result.json')['sha256']==a.expected_capture_result_sha
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];assert json.loads(json.dumps(native(rows),default=str))==read(CAP/'native-source-state-before.json')['rows']
 actual=read(CAP/'actual-render-geometry.json.gz');owned=actual['rows'][0];assert owned['uid']==UIDS[0]and owned['sourceSHA256']==SOURCE
 raw=next(r for r in actual['basicContextRows']if r['uid']==PROTECTED);pos=np.asarray(raw['position'],dtype='<f8').reshape(-1,3);idx=np.asarray(raw['index'],dtype=np.int64).reshape(-1,3);basic=pos[idx];assert np.array_equal(pos,pos.astype('<f4').astype('<f8'))and np.isfinite(basic).all()
 ground=np.asarray(actual['completeTowerBasicDrawnGround'],dtype='<f8').reshape(-1,3,3);assert len(ground)==len(actual['groundFacetBindings'])and np.isfinite(ground).all();groundsha=digest(ground.tobytes());bc=census(basic,list(range(len(basic))))
 original=np.asarray(read(CAP/'original-full-source-root-context.json.gz')['rows'][0]['completeOriginalBinary64WorldTriangles'],dtype='<f8');assert original.shape==(13061,3,3)and digest(original.tobytes())=='5a3726aafe64e1410482327fd681f49ede03b47718d4180e0e24b5cd27078c38'
 sourcec=census(original,list(range(13061)));assert len(sourcec['sharedEdgeConnectedComponents'])==569 and len(sourcec['exactNonrenderingOriginalFaces'])==75;components={fi:n for n,ids in enumerate(sourcec['sharedEdgeConnectedComponents'])for fi in ids}
 normals=np.cross(basic[:,1]-basic[:,0],basic[:,2]-basic[:,0]);low,top=F(float(basic[:,:,1].min())),F(float(basic[:,:,1].max()));tops=[i for i in range(len(basic))if np.all(basic[i,:,1]==float(top))];caps=[i for i in tops if normals[i,1]>0];walls=[i for i in range(len(basic))if normals[i,1]==0 and dimension(rational_face(basic[i]))==2];assert caps
 clipper=module(HERE/'xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011.py','reviewed_exact_clip');role=module(HERE/'lippo_tower_current_basic_mainbody_join_role_v1_20261011.py','reviewed_prism_geometry_only')
 # Pure geometric helpers only; do not invoke Lippo's named verification/policy.
 planes={i:role.prism_planes(basic[i],low,top)for i in tops};basicfinite=[];strictcaps=set()
 for i in range(len(basic)):
  proof=finite(basic[i],ground);basicfinite.append(dict(face=i,proof=proof));
  if i in caps and proof['groundProjectionCovered']and F(proof['exactCertifiedLowerClearanceM'])>0:strictcaps.add(i)
  if i%32==0:fence();print(json.dumps(dict(stage='basic-finite',completed=i+1,total=len(basic))),flush=True)
 interfaces=exact_upper_ground_interfaces(basic,walls,ground);grade={r['sourceFace']for r in interfaces};edges=defaultdict(list)
 for i in bc['completeRenderableFaceIds']:
  q=rational_face(basic[i])
  for x,y in zip(q,q[1:]+q[:1]):
   if x!=y:edges[tuple(sorted((x,y)))].append(i)
 routes=[];edgecontext=[]
 for e,ids in sorted(edges.items()):
  for wall in sorted(set(ids)&grade):
   for cap in sorted(set(ids)&strictcaps):
    exposure=best_original_vertex_exposure(basic[wall],ground);cert=segment([[str(v)for v in q]for q in e],ground);qualified=F(exposure['exactExposureLowerBoundM'])>0 and cert['strictlyExposedWholePositiveInterface']
    rec=dict(wall=wall,cap=cap,edge=[[str(v)for v in q]for q in e],exposure=exposure,wholeEdge=cert,qualifiedContextOnly=qualified);edgecontext.append(rec)
    if qualified:routes.append(rec)
 streamidx=np.asarray(owned['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'original':original,'literal':np.asarray(owned['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[streamidx],'explicitLeftF32':np.asarray(owned['completeExplicitLeftAssociatedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[streamidx],'explicitBalancedF32':np.asarray(owned['completeExplicitBalancedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[streamidx]};records={};bindings={}
 for mode,world in worlds.items():
  key=digest(world.tobytes());bindings[mode]=dict(wholeWorldSHA256=key,completeFaces=13061)
  if key in records:continue
  assert world.shape==(13061,3,3)and np.isfinite(world).all();pieces=[];partition=[];tested=0
  for fi in range(13061):
   q=rational_face(world[fi]);lower=clipper.clip(q,lambda p:top-p[1]);remaining=[lower]if clipper.polygon_dimension(lower)>=0 else[];hits=[]
   for cap in tops:
    if any(world[fi,:,k].max()<basic[cap,:,k].min()or world[fi,:,k].min()>basic[cap,:,k].max()for k in [0,2]):continue
    tested+=1;assert tested<=1000000,'Explicit exact-prism pair resource cap';poly=q
    for fn in planes[cap]:poly=clipper.clip(poly,fn)
    if poly:hits.append(dict(cap=cap,dimension=clipper.polygon_dimension(poly),points=[[str(v)for v in p]for p in poly],maximumDepth=str(top-min(p[1]for p in poly))))
    following=[]
    for frag in remaining:
     inside=frag
     for fn in planes[cap]:
      outside=clipper.clip(inside,lambda p,fn=fn:-fn(p))
      if clipper.polygon_dimension(outside)>=0 and any(fn(p)<0 for p in inside):following.append(outside)
      inside=clipper.clip(inside,fn)
      if not inside:break
    remaining=following
   partition.append(dict(sourceFace=fi,originalBody=components.get(fi),originalZeroFace=fi in sourcec['exactNonrenderingOriginalFaces'],sourcePrimitiveDimension=dimension(q),belowTopFragment=[[str(v)for v in p]for p in lower],prismFragments=hits,exteriorBelowTopFragments=[[[str(v)for v in p]for p in frag]for frag in remaining]));pieces.extend(dict(sourceFace=fi,**h)for h in hits)
   if fi%256==0:
    fence();save(DOC/(mode+'-partition-progress.json.gz'),dict(completeSourceRows=partition,sourceWorldSHA256=key));print(json.dumps(dict(stage='source-prism',mode=mode,completed=fi+1,total=13061,tested=tested)),flush=True)
  contact=exact_finite_contacts(world,list(range(13061)),basic,list(range(len(basic))),maximum_pairs=1000000)
  records[key]=dict(completeFaces=13061,actualBodyCensus=census(world,list(range(13061))),originalBodyProvenance=sourcec,completeSourcePartition=partition,completeSourceBasicFiniteContacts=contact,allPrismFragments=pieces,exactPairsTested=tested);save(DOC/'progress.json.gz',dict(bindings=bindings,distinctProofs=records))
 fence();d=dict(uid=UIDS[0],sourceSHA256=SOURCE,currentManifest=scope['currentManifest'],actualBasicUID=PROTECTED,actualBasicWorldSHA256=digest(basic.tobytes()),completeBasicFaces=len(basic),completeGroundSHA256=groundsha,completeGroundFaces=len(ground),originalCensus=sourcec,basicCensus=bc,allActualBasicFiniteProofs=basicfinite,upwardTopCaps=caps,strictPositiveCaps=sorted(strictcaps),allUpperGradeInterfaces=interfaces,allGradeWallCapEdges=edgecontext,qualifiedGradeWallWholeEdgeCapRoutes=routes,fourWorldBindings=bindings,distinctSourcePrismContactProofs=records,originalGovernmentPodiumUsedAsSupport=False,wholeBasicReaccepted=False,sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,physicalAccepted=False,rootAccepted=False,installationApproved=False,qualification='Exact source/basic lower prism, exterior residues, finite contacts and separately bounded BASIC grade/strict-cap context. No scalar range rejection, named Lippo approval transfer, whole569body support, joint/function/ownership or collision exemption.')
 save(DOC/'diagnostic.json.gz',d);walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','reviewed_context_freezer');paths=set();walker.local_imports(Path(__file__),paths);paths.update(ROOT/e['path']for e in receipt['evidenceRefs']);paths.update([CAP/'result.json',HERE/'xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011.py',HERE/'lippo_tower_current_basic_mainbody_join_role_v1_20261011.py']);proposal=DOC.parent/'government-xl-nam-fung79099-actual-basic45779-carrier-route-proposal-v1-20261012';pins=read(proposal/'lower-join-v2-exact-draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for e in pins['boundDraftInputs']:assert ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(proposal/'lower-join-v2-exact-draft-pins.json');paths.update(q for q in DOC.rglob('*')if q.is_file());paths.update(q for q in LOCAL.rglob('*')if q.is_file());fence();result=walker.F.freeze(BATCH,'nam-source-actual-basic-lower-prism-grade-cap-context',sorted(paths),dict(uids=UIDS+[PROTECTED],completeOriginalFaces=13061,genuineOriginalBodies=569,zeroOriginalFaces=75,sourceOnly=True,physicalAccepted=False,rootAccepted=False,installationApproved=False,originalGovernmentPodiumUsedAsSupport=False))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),sourceOnly=True)))
if __name__=='__main__':main()
