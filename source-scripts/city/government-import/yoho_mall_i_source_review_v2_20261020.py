"""Bind final unchanged-source identity, physical, neighbour and inspected visual evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-source-review-v2-20261020';DOC=BASE/BATCH
NAMES=dict(capture='assembly-capture-v1',physical='physical-review-v1',neighbours='neighbour-review-v3',identity='identity-review-v1',towerIdentity='tower-identity-v1',tower10Identity='tower10-complete-projection-v2',tower8Identity='tower8-complete-projection-v2',collision='foreign-collision-v1',browser1='private-browser-v1',browser2='private-browser-v2',browser3='private-browser-v3',browser4='private-browser-v4')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   d=BASE/('government-xl-yoho-mall-i-'+n+'-20261020');r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def path(k,f):return BASE/('government-xl-yoho-mall-i-'+NAMES[k]+'-20261020')/f
 def bind(k,f):
  p=path(k,f);key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key];refs.append(p);used[key]=pins[k][key];return dict(path=key,sha256=pins[k][key])
 def take(k,f):bind(k,f);return read(path(k,f))
 rows=take('capture','selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};uids=set(sources);assert len(uids)==8
 physical=take('physical','ROOT-PHYSICAL-REVIEW.json');near=take('neighbours','ROOT-NEIGHBOUR-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources;assert near['sourceSpecificNeighbourInterpretationAccepted']and not near['remainingNeighbourFailures']
 identity=take('identity','ROOT-IDENTITY-REVIEW.json');assert identity['sourceIdentityAccepted']
 for r in rows:
  uid=r['uid']
  if uid=='landsd/189427:0':continue
  p=take('tower8Identity','identity.json')if uid=='landsd/294858:0'else take('tower10Identity','identity.json')if uid=='landsd/294857:0'else take('towerIdentity',uid.split('/')[1]+'/identity.json');assert p['passed']and p['sourceSHA256']==sources[uid]
 reports=[]
 for k,widths in [('browser1',[1280,390]),('browser2',[1280]),('browser3',[1280,390]),('browser4',[390])]:
  for width in widths:
   r=take(k,str(width)+'/staged-browser.json');assert r['passed']and not r['errors'];reports.append(bind(k,str(width)+'/staged-browser.json'))
   for v in r['views']:
    if 'time' not in v:continue
    assert v['fullyFramed']and v['active']and v['visible']and v['solidAppearance']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]and not v['fallbackFaces']
 fallback=take('browser1','390/staged-browser.json');assert {v['uid']for v in fallback['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==uids
 images=[]
 for uid in sorted(uids):
  short=uid.split('/')[1].split(':')[0];k='browser3'if short in ['189427','294811','294810']else'browser1'
  images.append(bind(k,f'1280/staged-landsd-{short}-0-1280-1500.png'))
  images.append(bind('browser4',f'390/staged-landsd-{short}-0-390-2200.png'))
 for name in ['tower8-lower-body','mall-low-rim','foreign-overlap']:images.append(bind('browser2','1280/staged-local-joint-'+name+'-1280.png'))
 collision=take('collision','summary.json');assert len(collision['rows'])==4 and collision['rows'][0]['positiveContactPairs']==32 and all(r['positiveContactPairs']==85 for r in collision['rows'][1:])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);mh=digest(manifest.read_bytes());assert mh==take('capture','selection.json.gz')['manifestSHA256']
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 review=dict(uids=sorted(uids),sourceSHA256ByUid=sources,reviewer='Codex ROOT',currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,foreignContactContextAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,foreignContactBasis='The one unrelated recorded-form overlap is the retained northern BASIC way949541091. Its before-BASIC mall already has finite surface intersections. Unchanged government geometry has different detailed face contacts at this adjoining edge; exact source identity is independently verified. The inspected north-facing overview shows the original mall alongside the retained BASIC wing, without a displaced tower or separate stray mass. Original authored intersections alone are not additional rejection criteria. No common ownership or volumetric nonintersection is claimed; no neighbouring form is removed, clipped, suppressed or relabelled. Runtime picking/collision tests still pass.',visualLimitations='Daytime desktop overviews and settled mobile nighttime views are reviewed for each candidate, plus three focused desktop joins. Not every facade is visible from one camera; real foreground occlusion remains. Original material is dark at night because procedural windows are deliberately disabled. Failed-download banners in browser1 are intentional tests; settled browser4 uses no injected failures. Full numerical geometry and source identity checks provide the complete-source coverage, not screenshots alone.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);module('yoho_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-source-final-review-bound-to-browser-evidence',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
