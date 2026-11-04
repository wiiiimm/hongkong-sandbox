"""UNEXECUTED saved-row provenance attribution. No finite/coverage/kernel replay."""
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import upton_v6_saved_actual_union_finite_regression_draft_v3_20261013 as prior
from run import ROOT,HERE,read,save,connect,reservations
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-v6-saved-main89-basic17-coverage-attribution-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
V3=prior.DOC;V6=prior.V6;CURRENT=prior.CURRENT
JOB='60d6359bb99e50906d158651b86827b029c0efcb6b630f0b8e7d9df4a3b3ef14'
ref,check=prior.ref,prior.check

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 receipt=read(V3/'result.json');assert receipt['jobId']==JOB
 output=read(V3/'complete-new-union-finite-regression.json.gz');assert output['completeNewDrawnFaces']==11603 and output['newGroundSHA256']==prior.GROUND_SHA
 nomination=read(V6/'complete-nominations-before-guards.json.gz');assert len(nomination['candidateFaceProvenance'])==len(nomination['candidateRawPositionTriplets'])==11575
 assert [r['candidateFace']for r in nomination['candidateFaceProvenance']]==list(range(11575))
 _,replay,ground,oldground,old,attrs,scope,actors=prior.inputs()
 main=next(r for r in output['actors']if r['uid']=='landsd/12728:0');assert len(main['worlds'])==4
 ids=main['worlds'][0]['findings']['candidateUncovered'];assert len(ids)==89 and all(w['findings']['candidateUncovered']==ids and w['findings']['candidateOrdinaryUnproved']==ids for w in main['worlds'])
 basic=next(r for r in output['completeBasicRows']if r['uid']=='landsd/79883:0');assert basic['findings']['worlds'][0]['findings']['currentClearCandidateUnproved']==[17]
 return pins,receipt,output,nomination,replay,ground,attrs,actors,main,basic

def schema_only():
 pins,r,o,n,replay,g,a,actors,main,basic=load()
 return dict(passed=True,caller=ref(Path(__file__)),mainFailedFacesPerWorld=89,completeWorlds=4,singleCurrentClearBasicRegression=dict(uid=basic['uid'],face=17),allRawFailuresRetained=True,noFiniteCoverageRendererDBLeaseOrAcceptance=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,output,nomination,replay,ground,attrs,actors,main,basic=load()
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md')]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 refs+=receipt['evidenceRefs']
 for q in refs:check(q);pulse()
 # Byte-defined association keeps ALL identical candidate origins; no arbitrary
 # permutation/nearest facet or unique-source claim when duplicates exist.
 patch=read(prior.HERE/'local'/prior.MAX.name/'private-upton-v6-geometry-bound-overlap-reviewed.json')
 drawn,transform=drawn_native_faces(patch['nativeMesh']);assert len(drawn)==11575
 actual_counts=Counter(t.tobytes()for t in ground);draw_counts=Counter(t.tobytes()for t in drawn)
 assert all(actual_counts[k]>=v for k,v in draw_counts.items())and len(ground)-len(drawn)==28
 origin=defaultdict(list)
 for i,t in enumerate(drawn):origin[t.tobytes()].append(i)
 native_xz=np.asarray(patch['nativeMesh']['position'],dtype=np.float32).reshape(-1,3);index=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3)
 assert replay['actualNativeHeightIndexProjectedDeterminantThreshold']==1e-10
 before_draw=np.asarray(replay['before']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);before_by_bytes=defaultdict(list)
 for j,t in enumerate(before_draw):before_by_bytes[t.tobytes()].append(j)
 admitted=[]
 for i,(a,b,c)in enumerate(index):
  ax,az=map(float,native_xz[a,[0,2]]);bx,bz=map(float,native_xz[b,[0,2]]);cx,cz=map(float,native_xz[c,[0,2]])
  determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz)
  admitted.append(dict(candidateFace=i,actualJSNumberProjectedDeterminant=determinant,heightIndexAdmitted=abs(determinant)>=1e-10,noCoverageClaimFromAdmission=True))
 worlds=next(r[1]for r in actors if r[0]==main['uid']);basic_row=next(r for r in attrs['basicContextRows']if r['uid']==basic['uid']);p=np.asarray(basic_row['position'],dtype='<f8').reshape(-1,3);bw=p[np.asarray(basic_row['index'],dtype=np.int64).reshape(-1,3)]
 records=[]
 for row,worlds_to_use in [(main,worlds),(basic['findings'],{'capturedConstructorFloat32World':bw})]:
  for w in row['worlds']:
   selected=set(w['findings']['candidateUncovered'])if row['uid']==main['uid']else{17}
   seen=set()
   for chunk in w['findings']['chunks']:
    check(chunk);refs.append(chunk)
    for q in read(check(chunk))['rows']:
     if q['face']not in selected:continue
     i=q['face'];face=np.asarray(worlds_to_use[w['mode']][i],dtype='<f8');assert prior.sha(face)==q['findings']['sourceFaceSHA256'];seen.add(i)
     ids=q['completeNewGroundSelection']['selectedOriginalGroundFaces'];assert prior.sha(ground[ids])==q['completeRelevantGroundSHA256'];assert q['findings']['completeGroundSHA256']==q['completeRelevantGroundSHA256']
     f=q['findings'];coarse=f['coarse'];paired=f['paired'];proof=paired or coarse;coverage=proof['completeOriginalProjectionCoverage']
     bound=F(f['exactLowerM'])if f['exactLowerM']is not None else None
     box=[face[:,[0,2]].min(0).tolist(),face[:,[0,2]].max(0).tolist()];d=prior.DOMAIN
     wholly_inside=all(F(float(t[0]))>=F(d[0])and F(float(t[0]))<=F(d[2])and F(float(t[2]))>=F(d[1])and F(float(t[2]))<=F(d[3])for t in face)
     grounds=[]
     for j in ids:
      matches=origin.get(ground[j].tobytes(),[])
      grounds.append(dict(actualDrawFace=j,actualDrawTriplet=ground[j].tolist(),actualDrawTripletSHA256=prior.sha(ground[j]),allExactCandidateFaceOrigins=[dict(provenance=nomination['candidateFaceProvenance'][k],indexAdmission=admitted[k])for k in matches],candidateOriginAmbiguous=len(matches)>1,exactBeforeCurrentDrawFaceIDs=before_by_bytes.get(ground[j].tobytes(),[]),unmatchedCandidateOriginRemainsExplicit=not matches))
     records.append(dict(uid=row['uid'],mode=w['mode'],sourceFace=i,unchangedSourceXYZ=face.tolist(),sourceFaceSHA256=prior.sha(face),wholeWorldSHA256=w['wholeWorldSHA256'],closedProjectedBounds=box,entireSourceProjectionInsideCapturedDomain=wholly_inside,potentialOutsideDomainExtractionLimit=not wholly_inside,completeNewGroundSelection=q['completeNewGroundSelection'],savedFiniteRecordVerbatim=f,savedCurrentBaselineVerbatim=q['currentBaselineVerbatim'],exactSavedCoverageVerbatim=coverage,coarseBoundAlreadyAtLeastOrdinary=bool(bound is not None and bound>=-F(1,2)),negativeCoarseBoundIsNotActualBurialProof=bool(bound is not None and bound<-F(1,2)),rawCoverageFailureRetained=not f['projectionCovered'],selectedGroundProvenance=grounds,noSourceRoleRootOrAcceptanceCredit=True))
    pulse()
   assert seen==selected
 assert len(records)==357
 DOC.mkdir(parents=True);save(DOC/'complete-main89-four-world-basic17-saved-attribution.json.gz',dict(rows=records,actualCandidateDrawPacking=transform,completeCandidateFacets=11575,completeActualDrawnGround=11603,completeInputObligationsUnchanged=ref(V3/'complete-new-union-finite-regression.json.gz'),allRawFailedIDsAndRecordsRetained=True,noFiniteCoverageProofReplayed=True,noGeometrySourcePoseOrThresholdChanges=True,physicalAccepted=False,installationApproved=False))
 refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT; pulse(True)
 prior.module(prior.FREEZER,'upton_saved_failure_attribution_freezer').freeze(BATCH,'saved-coverage-negative-extraction-and-provenance-attribution-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.OWNED+[prior.SECONDARY,prior.NATIVE],sourceOnly=True,completeMainFailedRows=356,completeBasicFailedRows=1,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--attribute-saved-failures-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.OWNED+[prior.SECONDARY,prior.NATIVE,prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-saved-negative-attribution-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
