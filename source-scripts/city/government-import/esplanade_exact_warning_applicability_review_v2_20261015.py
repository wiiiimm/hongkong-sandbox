"""Record ROOT interpretation of exact unchanged source warnings; never publish."""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-esplanade-warning-applicability-review-v2-20261015';DOC=BASE/BATCH
SOURCES={'landsd/268828:0':'38a2e79ad1b90b7f800f1920b3a22a3890bd177cbc9258feccb32a9d7bd332f8','landsd/309385:0':'ab5f78c1349cfb01db2d60bb36af0122ec8d374abaa5c8b63eaac63f58cd097c'}
NAMES=['government-xl-esplanade-pair-current-physical-v3-20261015','government-xl-esplanade-exact-wall-exposure-v1-20261015','government-xl-esplanade-render-grade-roles-v2-20261015','government-xl-esplanade-exact-tower-podium-paths-v1-20261015','government-xl-esplanade-render-tower-podium-paths-v1-20261015','government-xl-esplanade-original-support-ground-v1-20261015']
def main():
 assert not DOC.exists();refs={};receipts={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);receipts[name]=r
   for q in r['evidenceRefs']:
    if q['path']in refs:assert refs[q['path']]==q['sha256']
    refs[q['path']]=q['sha256']
   refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h
 modes=[]
 for name,keys in [(NAMES[1],['original','literal']),(NAMES[2],['left','balanced'])]:
  for mode in keys:
   p=BASE/name/(mode+'.json.gz');d=read(p);c=d['capPaths'];assert c['completeOriginalFaces']==1476 and c['affectedOriginalWallFaces']==[510,516,518,1276]and c['allAffectedHavePaths']and not c['rawExposureFailures'];assert all(x['hasExactOriginalStrictClearCapRoofPath']and x['rawFaceExposurePositive']for x in c['paths']);assert len(d['gradeInterfaces'])==20 and sorted({r['sourceFace']for r in d['gradeInterfaces']})==[510,518,1276];modes.append(dict(mode=mode,capPaths=c['paths'],gradeContactFaces=[510,518,1276],gradeIntervals=20));refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 tower=[]
 for name,keys in [(NAMES[3],['original','literal']),(NAMES[4],['left','balanced'])]:
  for mode in keys:
   p=BASE/name/(mode+'.json.gz');d=read(p);assert d['completeTowerFaces']==23998 and d['completePodiumFaces']==1476 and len(d['failures'])==21 and all(x['exactSharedEdgePathsToPositivePodiumContact']for x in d['failures']);assert set(d['positiveContactRoots'])=={x['sourceFaceA']for x in d['rawExactContacts']['contacts']if x['dimension']>0};tower.append(dict(mode=mode,failures=d['failures'],positiveContactRoots=d['positiveContactRoots']));refs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 raw=read(BASE/NAMES[5]/'support-checks.json.gz')['rows'][0];assert len(raw['unresolved'])==21
 image=BASE/'government-xl-esplanade-residual-context-v1-20261015/residuals.png';refs[str(image.relative_to(ROOT))]=digest(image.read_bytes())
 browser=BASE/'government-xl-esplanade-private-browser-v2-20261015/ROOT-IMAGE-INSPECTION.json';refs[str(browser.relative_to(ROOT))]=digest(browser.read_bytes());assert len(read(browser)['images'])==8
 review=dict(reviewer='Codex ROOT',reviewUsedAI=True,aiGeometryModelling=False,sourceSHA256ByUid=SOURCES,sourceInterpretationAccepted=True,scope='Exact authored perimeter wall and tower lower-facade warning applicability only.',podiumInterpretation='Four partly terrain-crossing, exposed near-vertical perimeter wall facets remain connected to ordinary-clear caps. The exact original terrain also crosses these facets. This is authored wall/terrain context, not evidence of a misplaced upward walking surface. Face516 has connected wall/cap support evidence but no separately asserted direct grade contact.',towerInterpretation='The 21 flagged low-rim locations belong to source-connected lower tower perimeter details extending beside the stepped podium. Exact source edge paths connect every location to positive-dimensional original podium interfaces in all four representations. Pointwise vertical sampling at every perimeter decoration is not a separate structural-engineering test.',podiumModes=modes,towerModes=tower,rawInterfaceRetained=raw,rawOrdinaryReasonsResolved=False,strictContactCountersNotRewritten=True,notGenericWarningWaiver=True,notStructuralCertification=True,otherSourcesApproved=False,physicalAcceptance=False,installationApproved=False,remaining='Complete current parent-domain/native/BASIC terrain regression and compound-foundation qualification; exact source-specific staging decision and live publication checks remain independent.',evidenceRefs=[dict(path=p,sha256=h)for p,h in sorted(refs.items())])
 save(DOC/'ROOT-warning-applicability.json',review)
 spec=importlib.util.spec_from_file_location('esplanade_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'root-exact-source-warning-applicability-review-v1',[ROOT/p for p in refs]+[Path(__file__)],dict(uids=list(SOURCES),sourceInterpretationAccepted=True,reviewUsedAI=True,physicalAccepted=False,fullAcceptance=False));print('Exact source warning interpretation recorded; no publication')
if __name__=='__main__':main()
