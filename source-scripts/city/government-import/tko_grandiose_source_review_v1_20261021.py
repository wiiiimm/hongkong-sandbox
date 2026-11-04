"""Bind the exact eleven-original TKO Plaza / Grandiose evidence; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'; BATCH='government-xl-tko-grandiose-source-review-v1-20261021'; DOC=BASE/BATCH
NAMES={k:'government-xl-tko-grandiose-'+v+'-20261021' for k,v in dict(capture='joint-capture-v1',identity='identity-review-v1',physical='physical-review-v1',neighbours='neighbour-review-v1',browser='settled-browser-v3',recovery='private-browser-v1',scope='regional-scope-v1',terrain='joint-validation-v1',budget='runtime-budget-v1').items()}
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
 rows=take('capture','selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};assert len(sources)==11
 physical=take('physical','ROOT-PHYSICAL-REVIEW.json');identity=take('identity','ROOT-IDENTITY-REVIEW.json');near=take('neighbours','ROOT-NEIGHBOUR-REVIEW.json')
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert {r['uid']:r['sourceSHA256']for r in identity['rows']}==sources and all(r['sourceIdentityAccepted']for r in identity['rows'])
 assert near['ordinaryForms']==230 and near['sourceSpecificNeighbourInterpretationAccepted'] and not near['remainingNeighbourFailures'] and len(near['checkedNativeUids'])==12 and near['sourceSHA256ByUid']==sources
 assert near['foreignContactContextAccepted']
 budget=take('budget','budget.json');assert budget['originalModelResourceBudgetPassed'] and budget['sourceSHA256ByUid']==sources
 reports=[];images=[]
 for width in [1280,390]:
  p=BASE/NAMES['browser']/str(width)/'staged-browser.json';reports.append(bind('browser',p));r=read(p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==22
  joints=r.get('jointViews',[]);assert {v['selectedUid'] for v in joints}=={'landsd/265489:0','landsd/246824:0'}
  for joint in joints:
   assert {v['uid']:v['sourceSHA256'] for v in joint['models']}==sources
   assert all(v['active'] and v['visible'] and not v['fallbackFaces'] for v in joint['models'])
  for v in views:
   assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['sourceSHA256']==sources[v['uid']]and v['pick']==v['collision']==v['uid']
  if width==390:
   recovery=take('recovery','390/staged-browser.json');assert recovery['passed'] and not recovery['errors']
   assert {v['uid']for v in recovery['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(sources)
 for width,uid,time in [(1280,'265489','1500'),(1280,'246824','1500'),(1280,'29868','1500'),(1280,'29875','1500'),(390,'265489','1500'),(390,'246824','2200')]:
  images.append(bind('browser',BASE/NAMES['browser']/str(width)/f'staged-landsd-{uid}-0-{width}-{time}-canvas.png'))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 # Browser closure includes the exact current manifest and footprint-scope module.
 bind('browser',manifest);bind('capture',ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js')
 review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),reviewer='Codex ROOT',identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,foreignContactContextAccepted=True,foreignContactBasis=near['foreignContactBasis'],originalModelResourceBudgetPassed=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,basis='Eleven exact government originals with bound primary identity evidence, four-mode terrain foundations, finite support contacts and source-specific facade interpretation. The complete 230-form terrain scope and all12 retained originals pass with the full assembly. Unchanged authored Grandiose contact context is retained. Exact model assets fit current mobile and desktop model-cache budgets; this is not a device FPS certification. Both browser sizes verify original meshes, picking and collision; prior separately bound failure-test reports verify mobile recovery.',visualLimitations='Direct canvas exports are captured in the same browser evaluation as current source checks. ROOT inspected desktop podium overviews and two tower facades, plus mobile podium day/night exports. Neighbouring towers occlude some source surfaces; images do not establish unseen clearance. Complete numerical geometry evidence remains separately bound. No procedural windows are added to these original meshes.')

 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('sol_city_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-eleven-original-final-source-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
