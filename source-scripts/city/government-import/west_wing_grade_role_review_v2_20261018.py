"""Exact original lower-wall/column interpretation; no general policy waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-grade-role-review-v2-20261018';DOC=BASE/BATCH
NAMES=['government-xl-west-wing-grade-face-context-v1-20261018','government-xl-west-wing-grade-views-v1-20261018','government-xl-west-wing-runtime-wall-paths-v1-20261018','government-xl-west-wing-runtime-support-v2-20261018','government-xl-west-wing-runtime-foundations-v2-20261018','government-xl-west-wing-runtime-checks-v3-20261018','government-xl-west-wing-sloped-grade-views-v1-20261018','government-xl-west-wing-grade-role-exceptions-v1-20261018']
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 expected={'landsd/26195:0':13,'landsd/322270:0':7,'landsd/315069:0':174,'landsd/319534:0':0};grade=[];ids={}
 for uid,count in expected.items():
  for mode in ['original','literal','left','balanced']:
   d=read(BASE/NAMES[0]/(uid.split('/')[1]+'-'+mode+'.json.gz'));negative=d['continuousNegativeFaceIds'];assert len(negative)==count and not d['negativeUpwardFaceIds']and not d['negativeWithoutExposedWitness']and not d['uncoveredFaces']
   if uid in ids:assert ids[uid]==negative
   else:ids[uid]=negative
   sloped=[i for i in negative if abs(d['faces'][i]['normalYRatio'])>=.005]
   assert sloped=={'landsd/26195:0':[42722,42723,42809],'landsd/315069:0':[492,901,904,905]}.get(uid,[])
   assert all(d['faces'][i]['maximumObservedGapM']>0 for i in negative)
   grade.append(dict(uid=uid,mode=mode,sourceSHA256=d['sourceSHA256'],completeWorldSHA256=d['completeWorldSHA256'],completeDrawnGroundSHA256=d['completeDrawnGroundSHA256'],sourceFaceIds=negative))
 paths=read(BASE/NAMES[2]/'paths.json');assert paths['samples']==paths['covered']==100
 assert all(r['wholePathCoveredWithinNumericalTolerance'] and r['originalFailure']['reason']=='support-above-rim' for r in paths['rows'])
 support=read(BASE/NAMES[3]/'checks.json.gz')['rows'];assert len(support)==16
 for r in support:
  if r['uid']in ['landsd/322270:0','landsd/319534:0']:assert r['interface']['passed']and not r['unresolved']
  else:
   matching=[x for x in paths['rows']if x['uid']==r['uid']and x['mode']==r['mode']]
   assert len(matching)==len(r['unresolved']) and [x['originalFailure']for x in matching]==r['unresolved']
 assert read(BASE/NAMES[4]/'summary.json')['allAfterPassed']
 metrics=read(BASE/NAMES[5]/'metrics.json')['rows'];assert all(not r.get('error')and not r['missingTerrain']and r['maxSamplerDelta']<=.004 for r in metrics)
 images=[BASE/NAMES[1]/(u.split('/')[1].replace(':','-')+'.png')for u in list(expected)[:3]]+[BASE/NAMES[6]/(u.split('/')[1].replace(':','-')+'.png')for u in ['landsd/26195:0','landsd/315069:0']]
 views=read(BASE/NAMES[6]/'views.json')['rows'];worlds=read(BASE/'government-xl-west-wing-group-four-world-v1-20261018/worlds.json.gz')['original']
 for v in views:assert [worlds[v['uid']][i]for i in v['originalFaceIds']]==v['exactSourceTriangles']
 review=dict(reviewedBy='Codex ROOT',gradeSourceRoleAccepted=True,installationApproved=False,physicalAccepted=False,sourceSpecificOnly=True,gradeEvidence=grade,embeddedRimPaths=100,rawContactFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,usesAISourceInterpretation=True,aiGeometryModelling=False,inspectedImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],observations=['West Wing red original faces form vertical lower walls along the curved landscaped approach, retaining exposed upper wall portions.','CGO red original faces are vertical lower walls with triangular wall profiles. They meet the original restored ground; all six canonical rim samples now pass in every mode.','LegCo red original faces form vertical column sides and lower perimeter walls. Their lower endpoints continue below terrain while exposed upper portions remain visible.','The seven explicitly inspected sloped faces are West Wing lower wall facets42722/42723/42809 and LegCo column-side facets492/901/904/905. The .005 normal cutoff came from another source review and is not a general renderer acceptance threshold. Their exact original triangles are bound to the inspected close views, with complete exposed-face and terrain-coverage evidence; no general slope exception is introduced.','All affected source faces are near vertical, have exposed witnesses, and retain complete terrain coverage in all four coordinate modes. All 100 unresolved West Wing/LegCo rim samples have complete vertical paths within incident original wall faces to actual rendered ground.'],limitations=['This interprets only the exact listed original grade faces and embedded rim contacts; no generic threshold changes.','Complete scene visual validation, remaining identity/placement/collision checks and guarded publication are still required. No optimisation approval.'])
 save(DOC/'ROOT-GRADE-REVIEW.json',review);refs.extend(ROOT/p for p in pins)
 out=module('west_grade_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-exact-original-grade-role-review-v2',list(dict.fromkeys(refs)),dict(uids=list(expected),gradeSourceRoleAccepted=True,installationApproved=False,physicalAccepted=False,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
