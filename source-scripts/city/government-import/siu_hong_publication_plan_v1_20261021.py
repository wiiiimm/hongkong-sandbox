"""Stage two unchanged Siu Hong sources and exact terrain/scope additions."""
from pathlib import Path
import copy,json
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-qualified-publication-plan-v1-20261021';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
NAMES={k:'government-xl-siu-hong-'+v+'-20261021'for k,v in dict(review='source-review-v1',browser='private-browser-v3',terrain='private-terrain-v4',scope='regional-scope-v1').items()}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   p=BASE/n/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(k,p):
  assert ref(p)['sha256']==pins[k][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rp=BASE/NAMES['review']/'ROOT-SOURCE-REVIEW.json';review=take('review',rp)
 assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
 for q in review['imagesActuallyViewed']+review['browserReports']:assert ref(ROOT/q['path'])==q;refs.append(ROOT/q['path'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];before=read(manifest);after=copy.deepcopy(before);refs.append(manifest)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.append(pointer)
 old=[]
 for url in before['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p);old.extend(read(p)['models'])
 sources=review['sourceSHA256ByUid'];assert len(old)==len({m['uid']for m in old})==6800 and not(set(sources)&{m['uid']for m in old})
 OLD=HERE/'local'/NAMES['browser'];cat=take('browser',OLD/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources
 qualification={**review,'originalSourceReviewAccepted':True,'sourceReview':ref(rp)};save(DOC/'ROOT-SOURCE-REVIEW.json',qualification)
 for m in cat['models']:
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,sourceIdentityReview=ref(rp),sourceFunctionalApplicability=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Immutable original at fixed1x/source pose. Exact primary identity and two-form scope; all four-mode actual-terrain foundation and contact witnesses reviewed;17 neighbours and staged desktop/mobile recovery pass. Raw warnings retained.')
  for dep in m['supportDependencies']:assert dep['uid']=='landsd/233417:0'and dep['sha256']==sources[dep['uid']];dep['state']='installed'
  raw=(OLD/m['asset']).read_bytes();assert digest(raw)==m['sha256'];refs.append(OLD/m['asset']);p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',take('browser',OLD/'source-forms.json'))
 cfg=take('browser',OLD/'browser-config-390.json');assert len(cfg['terrain'])==1;t=cfg['terrain'][0];assert not t.get('replaces')and not t.get('replacesMany');patchpath=ROOT/t['source'];patch=take('terrain',patchpath);assert ref(patchpath)['sha256']==t['sha256']
 terrainurl='city/data/government-native-siu-hong-original-v1-20261021.json';assert terrainurl not in {p['url']for p in before['terrainPatches']}
 after['terrainPatches'].append(dict(area='Siu Hong Shopping Centre original assembly',url=terrainurl,resolution=t['resolution'],bytes=patchpath.stat().st_size,sha256=t['sha256'],source=patch['meta']))
 scope=review['conditionalScope'];modulepath=ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js';refs.append(modulepath);raw=modulepath.read_text();prefix='export const directOsmGroupScopes = ';start=raw.index(prefix)+len(prefix);end=raw.index(';',start);data=json.loads(raw[start:end]);assert scope['key']not in data
 definition=copy.deepcopy(scope['definition']);definition['forms']=[{k:b[k]for k in ['uid','objectId','buildingCSUID','parent','osmRefs','rings']}for b in definition['forms']];assert definition==scope['definition'];data[scope['key']]=definition
 stagedmodule=STAGE/'official-model-direct-osm-group-data.js';stagedmodule.write_text(raw[:start]+json.dumps(data,separators=(',',':'),ensure_ascii=False)+raw[end:])
 url='city/data/official-models/'+BATCH+'/catalogue.json';after['officialModelCatalogues'].append(url);save(STAGE/'manifest.json',after)
 edits=[dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')),dict(destination='3d-viewer/'+terrainurl,beforeSHA256=None,source=ref(patchpath)),dict(destination=str(modulepath.relative_to(ROOT)),beforeSHA256=digest(modulepath.read_bytes()),source=ref(stagedmodule)),dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=digest(manifest.read_bytes()),source=ref(STAGE/'manifest.json'))]
 assets=[dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+m['asset'],source=ref(STAGE/m['asset']))for m in cat['models']]
 previous=BASE/'government-xl-langham-original-installed-v1-20261021/full-xl-current-count.json';delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['expectedFixedXLDelta']==1 and delta['previousInstalled']==296;refs.append(previous)
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url);cfg['terrain'][0]['destination']=terrainurl;save(STAGE/'live-browser-config.json',cfg)
 for e in edits+assets:
  p=ROOT/e['destination'];assert(digest(p.read_bytes())if p.exists()else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 plan=dict(edits=edits,assets=assets,sourceSHA256ByUid=sources,newModels=sorted(sources),newVisibleModels=2,newRuntimeCount=6802,existingModelReverification=[],delta=delta,previousXLCount=ref(previous),terrainChanges=1,terrainReplacement=None,terrainDestination=terrainurl,currentManifest=ref(manifest),currentPointer=ref(pointer),sourceReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),publication=False)
 save(DOC/'publication-plan.json',plan);refs.extend([HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('siu_hong_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-qualified-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),qualifiedForLiveVerification=True,newVisibleModels=2,delta=delta,publication=False))
if __name__=='__main__':main()
