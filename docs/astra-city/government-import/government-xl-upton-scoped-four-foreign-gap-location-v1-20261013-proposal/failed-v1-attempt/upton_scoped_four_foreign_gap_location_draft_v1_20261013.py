"""UNEXECUTED location-only replay for thirteen saved rows/four foreign facets."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import sys,json,time,uuid,subprocess
import numpy as np
import upton_scoped_subdivision_saved_actual_union_delta_draft_v1_20261013 as prior
from exact_original_projection_coverage_20261009 import point,signed_area,subtract
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
from upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013 import segment_parameter,serial
from run import ROOT,HERE,read,save,connect,reservations
ref,check=prior.ref,prior.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-scoped-four-foreign-gap-location-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PACKET=BASE/'government-xl-upton-scoped-subdivision-four-foreign-coverage-regressions-v1-20261013-proposal/saved-four-foreign-full-facet-regression-rows.json.gz'
JOB='d5ede71c98345b8d3e767d6ac428c29480e20e61b664b8ca01ca8a65577c1e6a'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 packet=read(PACKET);assert len(packet['rows'])==13 and packet['uniqueForeignFacets']==4
 for q in packet['evidenceRefs']:check(q)
 replay=read(prior.capture.DOC/'actual-production-replay.json.gz');ground=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3)
 assert ground.shape==(11604,3,3)and prior.sha(ground)==prior.GROUND_SHA and packet['newGroundSHA256']==prior.GROUND_SHA
 nomination=read(prior.capture.nomination.DOC/'private-source-family-subdivision-nomination.json.gz');pv=nomination['candidateFaceProvenance'];raw=np.asarray(nomination['candidateRawPositionTriplets'],dtype='<f8')
 assert raw.shape==(11576,3,3)and [p['candidateFace']for p in pv]==list(range(11576))
 patch=read(prior.capture.DOC/'private-native-terrain-candidate.json.gz');drawn,_=drawn_native_faces(patch['nativeMesh']);assert len(drawn)==11576
 original_nomination=read(check(nomination['originalNomination']));source=np.asarray(read(check(original_nomination['allSourceOriginalTriplets']))['allOriginalTriplets'],dtype='<f8')
 current=np.asarray(read(check(original_nomination['allCurrentTriplets']))['rows'][0]['completeActualDrawnTriplets'],dtype='<f8').reshape(-1,3,3)
 assert source.shape==(122721,3,3)and current.shape==(9214,3,3)
 assert len(nomination['protectedWholeCurrentTripletsUnchanged'])==68
 for q in nomination['protectedWholeCurrentTripletsUnchanged']:assert prior.sha(raw[q['newCandidate']])==q['rawTripletSHA256']
 for r in packet['rows']:
  f=np.asarray(r['sourceTriangleXYZ'],dtype='<f8');assert f.shape==(3,3)and f.tobytes().hex()==r['sourceTriangleBinary64Hex']and prior.sha(f)==r['sourceFaceSHA256']
  row=r['completeSavedDeltaRowVerbatim'];binding=row['completeNewGroundSelection'];ids=binding['selectedOriginalGroundFaces']
  assert binding['completeGroundSHA256']==prior.GROUND_SHA and prior.sha(ground[ids])==row['completeRelevantGroundSHA256']
  assert r['exactSavedAreaCoverage']['method']=='closed-facet-area-union'and not r['exactSavedAreaCoverage']['exactProjectionCovered']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.baseline.CURRENT
 return pins,packet,ground,nomination,pv,raw,drawn,source,current
def schema_only():
 pins,p,g,n,pv,raw,d,s,c=load();return dict(passed=True,savedRows=13,uniqueForeignFacets=4,actualGroundFaces=len(g),sourceFacets=len(s),currentFacets=len(c),completeNativeFacets=len(d),noCoverageOrLeaseOrDBReplay=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>15:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,packet,ground,nomination,pv,raw,drawn,source,current=load()
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']+packet['evidenceRefs']
 receipt=read(prior.DOC/'result.json');assert receipt['jobId']==JOB
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 refs+=[ref(prior.DOC/'result.json')]+receipt['evidenceRefs']
 for q in refs:check(q);pulse()
 origins=defaultdict(list)
 for i,t in enumerate(drawn):origins[t.tobytes()].append(dict(kind='candidateNative',candidateFace=i,provenanceVerbatim=pv[i]))
 for i,t in enumerate(current):origins[t.tobytes()].append(dict(kind='capturedCurrentDraw',originalFace=i,originalTripletSHA256=prior.sha(t)))
 cache={};rows=[]
 for r in packet['rows']:
  saved=r['completeSavedDeltaRowVerbatim'];ids=saved['completeNewGroundSelection']['selectedOriginalGroundFaces'];selected=ground[ids];key=(r['sourceFaceSHA256'],saved['completeRelevantGroundSHA256'],tuple(ids))
  if key not in cache:
   face=np.asarray(r['sourceTriangleXYZ'],dtype='<f8');poly=[point(p)for p in face[:,[0,2]]];remaining=[poly]
   for t in selected:
    triangle=[point(p)for p in t[:,[0,2]]]
    if signed_area(triangle):
     if signed_area(triangle)<0:triangle.reverse()
     remaining=[part for piece in remaining for part in subtract(piece,triangle)]
    pulse()
    if not remaining:break
   area=sum(abs(signed_area(p))for p in remaining);coverage=r['exactSavedAreaCoverage']
   assert str(area)==coverage['exactUncoveredAreaM2']and len(remaining)==coverage['remainingPositiveAreaPieces']and area>0
   selected_origins=[]
   for j in ids:
    found=origins[ground[j].tobytes()];assert found # No fallback/current face may disappear from provenance.
    ancestors=[]
    for o in found:
     if o['kind']=='capturedCurrentDraw':ancestors.append(dict(kind='capturedCurrentDraw',originalFace=o['originalFace'],originalTripletSHA256=o['originalTripletSHA256'],wholeAncestorXYZ=current[o['originalFace']].tolist()));continue
     p=o['provenanceVerbatim']
     if p['kind']in ['originalTIN','capturedCurrentRing']:
      a=source if p['kind']=='originalTIN'else current;k=p['originalFace'];ancestors.append(dict(kind=p['kind'],originalFace=k,wholeAncestorXYZ=a[k].tolist(),originalTripletSHA256=prior.sha(a[k])))
     else:
      k=p['currentSurfaceFace'];ancestors.append(dict(kind='currentSurfaceForRuledJoin',originalFace=k,wholeAncestorXYZ=current[k].tolist(),originalTripletSHA256=prior.sha(current[k])))
      for o2 in p['origins']:
       k=o2['originalSourceFace'];ancestors.append(dict(kind='sourceForRuledJoin',originalFace=k,wholeAncestorXYZ=source[k].tolist(),originalTripletSHA256=prior.sha(source[k]),cutOriginVerbatim=o2))
    selected_origins.append(dict(actualDrawFace=int(j),wholeActualDrawXYZ=ground[j].tolist(),allByteExactOrigins=found,completeAncestorTriplets=ancestors))
   boundary=[]
   for pi,p in enumerate(remaining):
    for ei,(u,v)in enumerate(zip(p,p[1:]+p[:1])):
     incidents=[]
     for q in selected_origins:
      for k in range(3):
       t=q['wholeActualDrawXYZ'];a,b=point([t[k][0],t[k][2]]),point([t[(k+1)%3][0],t[(k+1)%3][2]])
       lo,hi=segment_parameter(u,a,b),segment_parameter(v,a,b)
       if lo is not None or hi is not None:incidents.append(dict(actualDrawFace=q['actualDrawFace'],edge=k,startParameter=lo,endParameter=hi,projectedOnlyNoHeightMateOrWholeEdgeCredit=True))
     boundary.append(dict(piece=pi,edge=ei,exactGapEdgeXZ=[u,v],selectedDrawEndpointIncidents=incidents))
   cache[key]=dict(exactRemainingPolygonsXZ=remaining,exactUncoveredAreaM2=area,remainingPositiveAreaPieces=len(remaining),savedAggregateReproducedExactly=True,completeSelectedGroundOrigins=selected_origins,completeGapBoundary=boundary,noRepairOrCoverageCredit=True)
  rows.append(dict(savedSourceRowVerbatim=r,locationOnlyProof=cache[key],fourLabelsRetained=True));pulse()
 DOC.mkdir(parents=True);save(DOC/'complete-four-foreign-gap-locations-and-ancestors.json.gz',serial(dict(rows=rows,completeSavedRows=13,uniqueForeignFacets=4,allRawNegativesRetained=True,noConstructorFullActorFiniteRayOrAcceptance=True)))
 refs +=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.baseline.CURRENT
 prior.baseline.module(prior.baseline.FREEZER,'upton_four_gap_location_freezer').freeze(BATCH,'four-foreign-full-facet-location-only-source-ancestor-diagnostic',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.baseline.OWNED+[prior.baseline.SECONDARY,prior.baseline.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--locate-saved-four-foreign-gaps-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.baseline.OWNED+[prior.baseline.SECONDARY,prior.baseline.NATIVE,prior.baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-four-gap-location-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
