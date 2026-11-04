"""Bind the exact five-original Sol City evidence; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'; BATCH='government-xl-sol-city-source-review-v1-20261021'; DOC=BASE/BATCH
NAMES={k:'government-xl-sol-city-'+v+'-20261021' for k,v in dict(capture='complete-capture-v1',identity='identity-review-v1',physical='physical-review-v2',neighbours='five-neighbours-v1',browser='private-browser-v1',scope='regional-scope-v1',terrain='private-terrain-v5').items()}
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
 rows=[r for r in take('capture','selection.json.gz')['rows']if r['uid']not in {'landsd/65157:0','landsd/76890:0'}];sources={r['uid']:r['sourceSHA256']for r in rows};assert set(sources)=={'landsd/251569:0','landsd/260034:0','landsd/268424:0','landsd/273080:0','landsd/273271:0'}
 physical=take('physical','ROOT-PHYSICAL-REVIEW.json');identity=take('identity','ROOT-IDENTITY-REVIEW.json');near=take('neighbours','summary.json')
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert {r['uid']:r['sourceSHA256']for r in identity['rows']}==sources and all(r['sourceIdentityAccepted']for r in identity['rows'])
 assert near['ordinaryForms']==64 and not near['ordinaryFlagged'] and not near['requiredNativeUids']
 reports=[];images=[]
 for width in [1280,390]:
  p=BASE/NAMES['browser']/str(width)/'staged-browser.json';reports.append(bind('browser',p));r=read(p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==10
  for v in views:
   assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['sourceSHA256']==sources[v['uid']]and v['pick']==v['collision']==v['uid']
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(sources)
 for width,uid,time in [(1280,'251569','1500'),(1280,'273271','1500'),(390,'268424','1500'),(390,'260034','1500'),(390,'273080','1500'),(390,'273271','2200')]:
  images.append(bind('browser',BASE/NAMES['browser']/str(width)/f'staged-landsd-{uid}-0-{width}-{time}.png'))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 # Browser closure includes the exact current manifest and footprint-scope module.
 bind('browser',manifest);bind('browser',ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js')
 review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),reviewer='Codex ROOT',identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,basis='Five exact government originals with individually bound primary identity evidence. Complete foundations and source-specific attachment proofs account for all raw support warnings in four arithmetic modes. All64 neighbouring forms pass; no existing detailed actors touch the complete regional terrain scope. Browser tests preserve the five original meshes, picking, collision, and mobile failed-download recovery. Source geometry, scale and pose unchanged.',visualLimitations='ROOT inspected the exported desktop podium overview, desktop Tower1 facade, mobile Tower3/Tower5/Tower2 views and mobile podium night. The views show original facade and roof detail; surrounding towers and mobile UI obscure some surfaces. They do not establish unseen clearance; complete numerical geometry checks remain separately bound. Night podium view retains the staged failure-test context with other detailed sources still withheld; fallback recovery is verified per source in the report.')

 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('sol_city_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-five-original-final-source-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
