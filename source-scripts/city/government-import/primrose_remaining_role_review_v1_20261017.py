"""Bind ROOT's exact-source role interpretation; no global clearance waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import BASE,PODIUM,module
BATCH='government-xl-primrose-remaining-role-review-v1-20261017';DOC=BASE/BATCH
NAMES=['government-xl-primrose-remaining-face-views-v1-20261017','government-xl-primrose-podium-remaining-roles-v1-20261015','government-xl-primrose-podium-current-finite-v2-20261015','government-xl-primrose-podium-source-role-review-v1-20261015']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipts=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);receipts.append((p,r))
 # Only source/face/world-ground evidence consumed here, not historical manifest approval.
 consumed=[BASE/NAMES[0]/n for n in ['source.png','ground.png','context.json']]+[BASE/NAMES[1]/(m+'.json.gz')for m in ['original','literal','left','balanced']]+[BASE/NAMES[2]/'summary.json',BASE/'government-xl-primrose-podium-buried-face-context-v1-20261015/ROOT-SOURCE-REVIEW.json']
 pins={}
 for _,r in receipts:
  for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 for p in consumed:assert ref(p)['sha256']in pins[ref(p)['path']]
 context=read(BASE/NAMES[0]/'context.json');old=read(consumed[-1]);assert old['sourceInterpretationAccepted'] and old['sourceSHA256']==context['sourceSHA256']
 walls=context['wallFaces'];undersides=context['undersideFaces'];assert len(walls)==15 and len(undersides)==7
 finite=read(BASE/NAMES[2]/'summary.json');worlds=[]
 for mode in ['original','literal','left','balanced']:
  r=read(BASE/NAMES[1]/(mode+'.json.gz'));f=next(x for x in finite['rows']if x['mode']==mode)
  assert r['sourceSHA256']==context['sourceSHA256'] and sorted(r['rawUnprovedFaces'])==sorted(walls+undersides)==f['unproved'] and not f['uncovered']
  assert sorted(x['sourceFace']for x in r['wallPaths'])==sorted(walls) and all(x['pathToStrictClearUpwardFace'][0]==x['sourceFace']for x in r['wallPaths'])
  assert sorted(x['sourceFace']for x in r['undersidePaths'])==sorted(undersides) and all(x['pathToPreviouslyReviewedUnderside999'][0]==x['sourceFace']and x['pathToPreviouslyReviewedUnderside999'][-1]==999 for x in r['undersidePaths'])
  assert set(walls)<=set(x['sourceFace']for x in r['exactGradeInterfaces'])
  worlds.append(dict(mode=mode,worldSHA256=r['worldSHA256'],groundSHA256=r['groundSHA256']))
 review=dict(reviewer='Codex ROOT',uid=PODIUM,sourceSHA256=context['sourceSHA256'],sourceRoleInterpretationAccepted=True,wallFaces=walls,lowerClosureFaces=undersides,worldBindings=worlds,imagesActuallyViewed=[ref(BASE/NAMES[0]/n)for n in ['source.png','ground.png']],basis='Two opposite oblique source-only and corrected-ground views inspected. Fifteen original wall faces intersect sloping ground and have exact shared-edge paths to strictly clear upward source faces in all four worlds. Seven coplanar downward faces connect through exact whole edges to previously reviewed lower closure999. These are source-authored wall/ground interfaces and lower closure surfaces, not occupied upward decks requiring exposure. Raw finite findings remain unchanged.',qualification='Source-specific visual/geometry-role interpretation only, bound to exact source and saved ground/world hashes. No engineering claim or generic wall/underside exemption. Requires current whole-assembly support, identity, neighbours, runtime, browser and publisher acceptance independently.',rawStrictFiniteAccepted=False,rawUnprovedFaces=sorted(walls+undersides),fullAcceptance=False,publicationApproved=False,installationApproved=False,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True)
 DOC.mkdir();save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 out=module('primrose_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-wall-ground-and-lower-closure-role-review-v1',[Path(__file__),*consumed,*[p for p,_ in receipts]],dict(uids=[PODIUM],sourceRoleInterpretationAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
