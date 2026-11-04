"""Bind the exact two-original Siu Hong evidence; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'; BATCH='government-xl-siu-hong-source-review-v1-20261021'; DOC=BASE/BATCH
NAMES={k:'government-xl-siu-hong-'+v+'-20261021' for k,v in dict(capture='private-capture-v2',identity='identity-review-v1',physical='physical-review-v1',neighbours='proposed-neighbours-v4',browser='private-browser-v3',scope='regional-scope-v1',terrain='private-terrain-v4').items()}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   p=BASE/n/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def bind(k,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key],key;refs.append(p);return dict(path=key,sha256=pins[k][key])
 def take(k,file):
  p=BASE/NAMES[k]/file;bind(k,p);return read(p)
 rows=take('capture','selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};assert set(sources)=={'landsd/190963:0','landsd/233417:0'}
 physical=take('physical','ROOT-PHYSICAL-REVIEW.json');identity=take('identity','ROOT-IDENTITY-REVIEW.json');near=take('neighbours','summary.json')
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert {r['uid']:r['sourceSHA256']for r in identity['rows']}==sources and all(r['sourceIdentityAccepted']for r in identity['rows'])
 assert near['ordinaryForms']==17 and not near['ordinaryFlagged'] and not near['requiredNativeUids']
 reports=[];images=[]
 for width in [1280,390]:
  p=BASE/NAMES['browser']/str(width)/'staged-browser.json';reports.append(bind('browser',p));r=read(p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==4
  for v in views:
   assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['sourceSHA256']==sources[v['uid']]and v['pick']==v['collision']==v['uid']
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(sources)
 for width,uid,time in [(1280,'190963','1500'),(1280,'233417','1500'),(390,'190963','1500'),(390,'190963','2200')]:
  images.append(bind('browser',BASE/NAMES['browser']/str(width)/f'staged-landsd-{uid}-0-{width}-{time}.png'))
 scope=take('capture','input.json.gz')['conditionalScope'];assert {f['uid']for f in scope['definition']['forms']}==set(sources)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 # Browser closure includes the exact current manifest and footprint-scope module.
 bind('browser',manifest);bind('browser',ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js')
 review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),conditionalScope=scope,reviewer='Codex ROOT',identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,basis='Exact named government originals and primary identities reviewed separately from physical support. Complete foundations and exact source contacts/path witnesses cover all raw support exceptions against actual drawn terrain. All17 neighbouring forms pass; no existing detailed actors touch the regional terrain scope. Browser tests preserve both original meshes, picking, collision, and mobile failed-download recovery. The conditional footprint scope contains only190963 and233417, excludes separate198433, and makes no shared-parent-wide claim.',visualLimitations='Overhead daytime views actually inspected on desktop and mobile show the shopping centre roof and surrounding source geometry. Mobile night also inspected; original surfaces remain dark with procedural windows disabled. Overhead images do not establish unseen facade clearance; full numerical source checks remain bound. Prior V2 occluded screenshots are not used as shape evidence.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('siu_hong_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-two-original-final-source-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
