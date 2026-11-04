"""Bind exact eight-original identity, physical, neighbour and runtime evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-source-review-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-manhattan-'+v+'-20261021'for k,v in dict(capture='assembly-capture-v1',identity='companion-identity-review-v1',physical='physical-review-v1',neighbours='neighbour-review-v1',browser='browser-consolidation-v1',joint='private-browser-v7',collision='foreign-collision-v1').items()}
NAMES['mainIdentity']='government-xl-next-twenty-original-identity-v6-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   p=BASE/n/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def bind(k,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key],key;refs.append(p);return dict(path=key,sha256=pins[k][key])
 def take(k,file):
  p=BASE/NAMES[k]/file;bind(k,p);return read(p)
 selection=take('capture','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==8
 physical=take('physical','ROOT-PHYSICAL-REVIEW.json');near=take('neighbours','ROOT-NEIGHBOUR-REVIEW.json');identity=take('identity','ROOT-IDENTITY-REVIEW.json');browser=take('browser','BROWSER-ACCOUNTING.json')
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert near['sourceSpecificNeighbourInterpretationAccepted']and not near['remainingNeighbourFailures']
 assert {r['uid']:r['sourceSHA256']for r in identity['rows']}=={u:s for u,s in sources.items()if u!='landsd/276331:0'}and all(r['sourceIdentityAccepted']for r in identity['rows'])
 main=BASE/'government-xl-next-twenty-original-identity-v3-20261021/276331:0/identity.json';bind('mainIdentity',main);m=read(main);assert m['passed']and not m['reasons']and m['sourceSHA256']==sources['landsd/276331:0']
 context=main.with_name('context.json');bind('mainIdentity',context);foreign=[r for r in read(context)['identity']['intersectingForms']if not r['sameParent']and not r['sharedOsmReference']];assert len(foreign)==1 and foreign[0]['uid']=='landsd/231708:0' and foreign[0]['intersectionAreaM2']<.208
 assert browser['sourceSHA256ByUid']==sources and browser['allCandidatesHaveDayNightDesktopMobileWitnesses']and browser['allCandidatesHaveFailedDownloadRecovery']
 reports=browser['reports'];images=[]
 for uid in sources:
  short=uid.split('/')[1].split(':')[0];day=3 if short in ['120103','266799','213072']else 4;night=3 if day==3 else 6 if short=='258271'else 5
  for v,w,t in [(day,1280,'1500'),(night,390,'2200')]:
   p=BASE/f'government-xl-manhattan-private-browser-v{v}-20261021'/str(w)/f'staged-landsd-{short}-0-{w}-{t}.png';images.append(bind('browser',p))
 for width in [1280,390]:
  r=take('joint',f'{width}/staged-browser.json');assert r['passed']and not r['errors']
  for v in r['jointViews']:
   assert {m['uid']for m in v['models']}=={'landsd/276331:0','landsd/266799:0','landsd/258271:0'}and all(m['active']and m['visible']for m in v['models'])
  views=[v for v in r['views']if 'time'in v];assert len(views)==2 and all(v['pick']==v['collision']=='landsd/258271:0'and v['collisionProbes'][-1]['uid']=='landsd/258271:0'for v in views)
  reports.append(bind('joint',BASE/NAMES['joint']/str(width)/'staged-browser.json'))
 collision=take('collision','summary.json');assert [r['positiveContactPairs']for r in collision['rows']]==[24,36,36,36]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256'];refs.append(manifest)
 # Browser-accounting report references retain whole-run errors; verify all exact bytes.
 for r in reports:
  p=ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'];refs.append(p)
 review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),reviewer='Codex ROOT',identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,foreignContactContextAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,foreignContactBasis='The main original has a 0.2072m2 plan intersection with KMB Headquarters231708. Complete rendered BASIC sources already have24 finite surface contact pairs; the unchanged original has36 in all three renderer coordinate representations. Exact source attribution passes. These source-authored contacts do not establish a displaced source or justify clipping original faces. No volumetric nonintersection or common ownership is claimed; the neighbour remains unchanged and complete neighbour checks pass. Shared-OSM assembly intersections retain both accepted existing originals and the seven separately checked new originals.',visualLimitations='Desktop daytime overviews inspected for all8; mobile night captures also inspected. Real foreground buildings obscure portions;307773 mobile night is fully occluded and is not used as visual shape evidence, its desktop original is visible. Source materials are deliberately dark at night without procedural windows. Some banners reflect intentional503 testing. Images do not establish unseen clearance; complete numerical and identity evidence provides full-source checks. V5 remains a failed whole run; only completed per-model witnesses are consumed, with258271 independently tested in V6 and with Tower6 explicitly active in V7.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('manhattan_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-final-review-bound-to-source-and-browser',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
