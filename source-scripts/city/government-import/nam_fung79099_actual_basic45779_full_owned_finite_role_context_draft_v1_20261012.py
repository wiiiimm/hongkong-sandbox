"""DRAFT complete Nam finite ground and source-bound role obligations, no approval.
No contact/prism/grade replay. Existing coarse+paired finite kernels only.
"""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from nam_fung79099_actual_basic45779_lower_join_grade_cap_draft_v2_20261012 import inputs as capture_inputs,CAP,UIDS,PROTECTED,MANIFEST_SHA,ref,module,state,native,SOURCE
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nam-fung79099-actual-basic45779-full-owned-finite-role-context-v1-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
JOIN=B/'government-xl-nam-fung79099-actual-basic45779-lower-join-grade-cap-v2-20261012'
PROPOSAL=B/'government-xl-nam-fung79099-actual-basic45779-full-owned-finite-role-proposal-v1-20261012'
CAP_SHA='498c1512d084c0ed488993f2243523a14ba9589e05f396913bab83aeb1cd4c65';JOIN_SHA='d3bdc58e7cfb9eafa617ee9fc25ec979b91b79c85ad3d6adf974749e14383933'
CHUNK=256

def checked_pins():
 p=read(PROPOSAL/'executable-pins.json');assert p['caller']==ref(Path(__file__))
 for e in p['boundInputs']:assert ref(ROOT/e['path'])==e,e
 return [ref(PROPOSAL/'executable-pins.json'),p['caller']]+p['boundInputs']

def inputs():
 pins=checked_pins();capture,scope,before,selections=capture_inputs(CAP_SHA);join=read(JOIN/'result.json');assert ref(JOIN/'result.json')['sha256']==JOIN_SHA and join['batch']==JOIN.name
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(join['jobId'],)).fetchone()==('complete',join)
 for e in join['evidenceRefs']:assert ref(ROOT/e['path'])==e,e
 d=read(JOIN/'diagnostic.json.gz');assert d['uid']==UIDS[0]and d['actualBasicUID']==PROTECTED and d['sourceSHA256']==SOURCE and d['completeBasicFaces']==432 and d['completeGroundFaces']==818
 assert d['currentManifest']==scope['currentManifest']and scope['expectedNativeCount']==6649
 for key in ['wholeBasicReaccepted','originalGovernmentPodiumUsedAsSupport','identityAccepted','physicalAccepted','rootAccepted','installationApproved']:assert d[key]is False
 assert len(d['originalCensus']['sharedEdgeConnectedComponents'])==569 and len(d['originalCensus']['exactNonrenderingOriginalFaces'])==75
 return pins,capture,join,scope,before,selections,d

def face_proof(face,ground,i,body,original_zero,actual_zero):
 p=finite(face,ground);lower=F(p['exactCertifiedLowerClearanceM']);pairs=[];minimum=maximum=None
 if lower<=0:
  for j in p['allProjectedBoundingCandidateOriginalGroundFacets']:
   q=column(face,ground[j]);v=[F(x['exactGapM'])for x in q['allExactBasicFeasibleColumnVertices']];record=dict(originalGroundFace=int(j),proof=q,exactMaximumFiniteColumnGapM=str(max(v))if v else None)
   if v:minimum=min(v)if minimum is None else min(minimum,min(v));maximum=max(v)if maximum is None else max(maximum,max(v))
   pairs.append(record)
  if p['groundProjectionCovered']:assert minimum is not None,'Covered finite column has no exact witnesses; preserve failed run'
  if minimum is not None:lower=minimum
 return dict(face=i,originalBody=body,originalZeroFace=original_zero,actualWorldZeroFace=actual_zero,completeFiniteProjectionProof=p,allRefinedFiniteColumnPairs=pairs,exactLowerM=str(lower),exactMinimumFiniteColumnGapM=str(minimum)if minimum is not None else None,exactMaximumFiniteColumnGapM=str(maximum)if maximum is not None else None,completeProjectionCovered=p['groundProjectionCovered'],ordinaryFiniteProved=bool(p['groundProjectionCovered']and lower>=-F(1,2)),strictPositiveFiniteProved=bool(p['groundProjectionCovered']and lower>0),gradeRootCredit=False)

def body_context(d,world_sha,rows):
 proof=d['distinctSourcePrismContactProofs'][world_sha];byface={r['face']:r for r in rows};partition=proof['completeSourcePartition'];assert [r['sourceFace']for r in partition]==list(range(13061))
 contacts=proof['completeSourceBasicFiniteContacts']['contacts'];out=[]
 for body,ids in enumerate(d['originalCensus']['sharedEdgeConnectedComponents']):
  s=set(ids);hits=[c for c in contacts if c['sourceFaceA']in s]
  out.append(dict(originalBody=body,completeOriginalFaceIds=ids,ordinaryFailingFaces=[i for i in ids if not byface[i]['ordinaryFiniteProved']],coverageFailingFaces=[i for i in ids if not byface[i]['completeProjectionCovered']],strictUncertifiedFaces=[i for i in ids if not byface[i]['strictPositiveFiniteProved']],savedPrismSourceFaceIds=[r['sourceFace']for r in partition if r['sourceFace']in s and r['prismFragments']],savedSourceBasicFiniteContactRecordIndices=[i for i,c in enumerate(contacts)if c['sourceFaceA']in s],savedContactDimensions={str(n):sum(c['dimension']==n for c in hits)for n in [0,1,2]},roleStatus='mainbody-lower-interface-source-interpretation-pending'if body==0 else'original-body-structural-or-terminal-role-unqualified',ordinaryClearDoesNotImplyRoot=True,structuralSupportQualified=False,terminalVisualRoleQualified=False,rootQualified=False))
 assert len(out)==569 and sum(len(r['completeOriginalFaceIds'])for r in out)+75==13061
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();pins,capture,join,scope,before,selections,d=inputs()
 if a.preflight_only:print(json.dumps(dict(currentPinsPassed=True,completedCaptureAndJoinAllRefsPassed=True,noWorker=True)));return
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('nam-full-owned-finite-'+str(uuid.uuid4()),['building:'+u for u in UIDS+[PROTECTED]],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not(DOC/'diagnostic.json.gz').exists();walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','nam_full_finite_closure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(HERE/'nam_fung79099_freeze_actual_basic45779_full_owned_finite_role_context_draft_v1_20261012.py',paths);codes=[ref(q)for q in sorted(paths)];receiptpins=[ref(CAP/'result.json'),ref(JOIN/'result.json')]
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
  for e in pins+codes+receiptpins:assert ref(ROOT/e['path'])==e,e
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selections),default=str))==read(CAP/'native-source-state-before.json')['rows']
 fence();attrs=read(CAP/'actual-render-geometry.json.gz');owned=attrs['rows'][0];index=np.asarray(owned['completeOriginalIndex'],dtype=int).reshape(-1,3);assert index.shape==(13061,3)
 original=np.asarray(read(CAP/'original-full-source-root-context.json.gz')['rows'][0]['completeOriginalBinary64WorldTriangles'],dtype='<f8');ground=np.asarray(attrs['completeTowerBasicDrawnGround'],dtype='<f8').reshape(-1,3,3);assert ground.shape==(818,3,3)and digest(ground.tobytes())==d['completeGroundSHA256']
 labels={i:b for b,ids in enumerate(d['originalCensus']['sharedEdgeConnectedComponents'])for i in ids};zeros=set(d['originalCensus']['exactNonrenderingOriginalFaces']);assert len(labels)+len(zeros)==13061 and not set(labels)&zeros
 worlds={'original':original};positions={}
 for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  v=np.asarray(owned[key],dtype='<f8').reshape(-1,3);assert np.isfinite(v).all();positions[name]=dict(completeUnusedPOSITIONVertices=len(v),wholeUnusedPOSITIONWorldSHA256=digest(v.tobytes()),bounds=[v.min(0).tolist(),v.max(0).tolist()],noUnusedPositionOmission=True);worlds[name]=v[index]
 bindings={};proofs={};chunkrefs=[]
 for mode,world in worlds.items():
  sh=digest(world.tobytes());assert world.shape==(13061,3,3)and np.isfinite(world).all()and sh==d['fourWorldBindings'][mode]['wholeWorldSHA256'];bindings[mode]=dict(wholeWorldSHA256=sh,groundSHA256=d['completeGroundSHA256'],completeFaces=13061,proofTupleSHA256=digest((sh+d['completeGroundSHA256']).encode()))
  if sh in proofs:continue
  az=set(d['distinctSourcePrismContactProofs'][sh]['actualBodyCensus']['exactNonrenderingOriginalFaces']);rows=[]
  for start in range(0,13061,CHUNK):
   stop=min(start+CHUNK,13061);path=LOCAL/'chunks'/sh/f'{start:05d}-{stop:05d}.json.gz';contract=dict(firstFace=start,exclusiveLastFace=stop,worldSHA256=sh,groundSHA256=d['completeGroundSHA256'],codeRefs=codes,ordinaryThresholdM='-1/2',originalBodyCensusSHA256=digest(json.dumps(d['originalCensus'],sort_keys=True,separators=(',',':')).encode()))
   fence()
   if path.exists():chunk=read(path);assert chunk['contract']==contract
   else:
    chunk=dict(contract=contract,rows=[face_proof(world[i],ground,i,labels.get(i),i in zeros,i in az)for i in range(start,stop)]);temp=path.with_name(path.name+'.pending.json.gz');save(temp,chunk);assert read(temp)==chunk;temp.replace(path)
   assert [r['face']for r in chunk['rows']]==list(range(start,stop));rows.extend(chunk['rows']);chunkrefs.append(ref(path));assert reservations.heartbeat(lease)['ok'];fence();print(json.dumps(dict(mode=mode,completed=stop,total=13061)),flush=True)
  assert len(rows)==13061;proofs[sh]=dict(completeFaces=13061,allWholeFacetProofs=rows,ordinaryFailingFaces=[r['face']for r in rows if not r['ordinaryFiniteProved']],coverageFailingFaces=[r['face']for r in rows if not r['completeProjectionCovered']],strictUncertifiedFaces=[r['face']for r in rows if not r['strictPositiveFiniteProved']],bodyObligations=body_context(d,sh,rows))
 fence();result=dict(uid=UIDS[0],sourceSHA256=SOURCE,currentManifest=scope['currentManifest'],currentNativeCount=6649,completeFaces=13061,genuineOriginalBodyObligations=569,zeroOriginalFaceObligations=75,ordinaryThresholdM='-1/2',originalBodyCensus=d['originalCensus'],allFourStreamBindings=bindings,distinctCompleteFiniteProofs=proofs,completeUnusedPOSITIONBindings=positions,completeGroundFaces=818,completeGroundSHA256=d['completeGroundSHA256'],savedBASICCarrierGradeCapContext=dict(diagnostic=ref(JOIN/'diagnostic.json.gz'),completeBasicFaces=432,rawCoarseOrdinaryUnprovedFaceIds=[r['face']for r in d['allActualBasicFiniteProofs']if not r['proof']['existingOrdinaryClearanceBoundProved']],strictUpwardCapIds=d['strictPositiveCaps'],qualifiedGradeWholeEdgeCapRouteCount=len(d['qualifiedGradeWallWholeEdgeCapRoutes']),availabilityOnly=True,wholeBasicReaccepted=False),sourceOnly=True,identityAccepted=False,physicalAccepted=False,rootAccepted=False,installationApproved=False,all569RolesQualified=False,foreignHoldsDischarged=False,currentAll6649NativeClearanceProved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceInterpretationPending=True,evidenceRefs=pins+codes+[ref(CAP/'result.json'),ref(JOIN/'result.json'),ref(CAP/'review.json'),ref(CAP/'actual-render-geometry.json.gz'),ref(CAP/'original-full-source-root-context.json.gz'),ref(JOIN/'diagnostic.json.gz')]+chunkrefs)
 save(DOC/'diagnostic.json.gz',result);subprocess.run([sys.executable,str(HERE/'nam_fung79099_freeze_actual_basic45779_full_owned_finite_role_context_draft_v1_20261012.py'),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
