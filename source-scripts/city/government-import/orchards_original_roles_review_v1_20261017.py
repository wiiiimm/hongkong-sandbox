"""Bounded interpretation of immutable original grade faces and one podium corner."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-original-roles-review-v1-20261017';DOC=BASE/BATCH
T='landsd/254629:0';P='landsd/233002:0';C='landsd/256434:0';R='landsd/254621:0'
EXPECTED={T:'132aa978b271794e7cdde00a3a431e0585fc334af822e102b218335f52ff4b98',P:'26d2392b7510242922721dfbaef49f1fb0db447fa017317f7b4a2de37beabd2e',C:'7904c4759be630f393ba5aa51771e936327aa4adb45317f3672a7eafdb5502dd',R:'7da323731cb425039e534f404f30ea162fd38e49238e6739f22784622ff650f8'}
def folder(n):return BASE/('government-xl-orchards-'+n+'-v1-20261017')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 names=['assembly-terrain-candidate','assembly-neighbours','assembly-four-world','assembly-four-foundations','grade-face-context','podium-component-identity','named-connection-identity','original-podium-support','four-world-corner-boundary','four-world-capture']
 for name in names:
  d=folder(name);r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 phys=folder('assembly-terrain-candidate');rows=read(phys/'selection.json.gz')['rows'];assert {r['uid']:r['sourceSHA256']for r in rows}==EXPECTED
 assert read(phys/'construction.json')['strictTerrainValidatorPassed'];foundation=read(folder('assembly-four-foundations')/'summary.json');assert foundation['allModesPassed']and len(foundation['rows'])==16
 neighbours=read(folder('assembly-neighbours')/'summary.json');assert neighbours['forms']==49 and not neighbours['basicFlags']and neighbours['nativeResolved']==[R]and all(r['passed']for r in neighbours['nativeRows'])
 identities={P:read(folder('podium-component-identity')/'identity.json'),T:read(folder('named-connection-identity')/'identity.json'),C:read(folder('community-current-checks')/'identity-proofs.json')['rows'][0]}
 for u,p in identities.items():assert p['uid']==u and p['sourceSHA256']==EXPECTED[u]and p['passed']and not p['reasons']
 assert identities[P]['requiredCompanionUid']==C and identities[P]['requiredCompanionSHA256']==EXPECTED[C]
 worlds=read(folder('assembly-four-world')/'world-triangles.json.gz');previous=read(folder('four-world-capture')/'world-triangles.json.gz');modes={'original','literal','left','balanced'};assert set(worlds)==set(previous)==modes
 for mode in modes:
  for uid in [T,P]:assert np.array_equal(worlds[mode][uid],previous[mode][uid])
 contact=read(folder('original-podium-support')/'support-checks.json.gz')['rows'][0];raw=contact['interface'];assert contact['sourceSHA256']==EXPECTED[T]and contact['supportSHA256']==EXPECTED[P];assert not raw['passed']and raw['samples']==272 and raw['strictContacts']==271 and raw['wallIntersections']==0 and len(raw['unresolved'])==1
 edge=read(folder('four-world-corner-boundary')/'proofs.json.gz');assert edge['allModesComplete']and edge['fixedBandM']==.1 and len(edge['rows'])==8
 for mode in modes:
  mode_rows=[r for r in edge['rows']if r['mode']==mode];assert len(mode_rows)==2 and {r['sourceFace']for r in mode_rows}=={1032,1035}and all(r['complete']for r in mode_rows)
 grade_reviews={}
 for uid,n in [(P,177),(C,12)]:
  ids=None;entries=[]
  for mode in sorted(modes):
   d=read(folder('grade-face-context')/(uid.split('/')[1]+'-'+mode+'.json.gz'));assert d['sourceSHA256']==EXPECTED[uid]and d['completeWorldSHA256']==digest(np.asarray(worlds[mode][uid],dtype='<f8').tobytes());assert not d['uncoveredFaces']and not d['negativeUpwardFaceIds']and not d['negativeWithoutExposedWitness'];current=d['continuousNegativeFaceIds'];assert len(current)==n
   if ids is None:ids=current
   else:assert current==ids
   assert all(d['faces'][i]['maximumObservedGapM']>0 for i in current)
   normals=[d['faces'][i]['normalYRatio']for i in current]
   if uid==P:assert all(abs(x)<=.1 for x in normals)
   else:assert sum(x<-.99 for x in normals)==7 and all(abs(x)<=.1 or x<-.99 for x in normals)
   entries.append(dict(mode=mode,wholeSourceFaces=d['wholeSourceFaces'],completeWorldSHA256=d['completeWorldSHA256'],completeDrawnGroundSHA256=d['completeDrawnGroundSHA256'],minimumExposedWitnessM=min(d['faces'][i]['maximumObservedGapM']for i in current)))
  grade_reviews[uid]=dict(originalFaceIds=ids,modeEvidence=entries,role='Original near-vertical podium walls and column sides cross the existing slope, retaining exposed upper surfaces.'if uid==P else 'Original community lower-shell interface: five side faces and seven downward-facing underside faces intersect the slope while retaining exposed portions. No upward roof face is implicated.',acceptedForExactSource=True)
 metrics=read(phys/'metrics.json');policy=module('orchards_review_raw_policy',HERE/'acceptance-policy.py');raw_reasons={}
 for u in [T,P,C]:
  m=next(r for r in metrics['rows']if r['uid']==u);raw_reasons[u]=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=EXPECTED[u],identityProof=identities[u]['proof']),m,metrics['profiles']['mobile'])
 assert raw_reasons=={T:['ground-contact-unresolved'],P:['terrain-intersects-source-over-0.5m'],C:['terrain-intersects-source-over-0.5m']}
 images=folder('grade-role-views');exports=read(images/'exports.json')
 for p,h in exports['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 inspected=[]
 for p in [images/'233002:0-grade-context.png',images/'256434:0-grade-context.png',images/'tower2-corner-original.png']:
  inspected.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),inspectedByRoot=True));refs.append(p)
 decision=dict(sourceSHA256ByUid=EXPECTED,reviewer='Codex ROOT',sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,gradeRoles=grade_reviews,sourceSpecificGradeInterpretationAccepted=True,sourceSpecificBoundaryInterpretationAccepted=True,rawNumericReasons=raw_reasons,rawStrictSupportPassed=False,rawSupportUnresolved=raw['unresolved'],tower2BoundaryReview='One original cylindrical corner touches the authored podium ledge boundary. Both complete low source edges (faces1032/1035) lie within the fixed0.1m band of originally horizontal finite podium faces in all four captured modes. Other271 contacts pass canonically, wall intersections zero, complete compound foundation passes in all modes. Interpret this exact corner as the authored original interface; do not claim the canonical vertical-sample test passes.',retainedTower1Review='All current terrain-only contact values and complete terrain foundations pass; native before/after regression passes. The earlier17 faces flagged by treating the entire podium as terrain are retained source-to-source context, not a new requirement for Tower1 to root on the podium. No Tower1 support dependency is added.',inspectedImages=inspected,fullAcceptance=False,publicationApproved=False,remaining=['production candidate validator and raw diagnostic reconciliation','desktop/mobile day/night browser image inspection and failed-download fallback','guarded atomic installation and exact companion identity binding'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',decision);refs.extend([HERE/'acceptance-policy.py',*[p for p in images.rglob('*')if p.is_file()]]);out=module('orchards_roles_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-exact-original-grade-and-boundary-source-role-review-v1',list(set(refs)),dict(uids=[T,P,C,R],sourceSpecificGradeInterpretationAccepted=True,sourceSpecificBoundaryInterpretationAccepted=True,rawNumericReasons=raw_reasons,fullAcceptance=False,publicationApproved=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
