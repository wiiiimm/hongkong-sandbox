"""Exact original Langham support, foundation, identity and browser review."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-source-review-v1-20261021';DOC=BASE/BATCH;UID='landsd/79318:0';SUPPORT='landsd/224399:0'
NAMES={k:'government-xl-langham-'+v+'-20261021'for k,v in dict(capture='assembly-capture-v1',foundation='assembly-foundations-v1',contacts='assembly-contacts-v2',paths='remaining-paths-v2',runtime='current-runtime-v1',browser='private-browser-v1').items()};NAMES['identity']='government-xl-next-twenty-original-identity-v6-20261021'
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
 selection=take('capture','selection.json.gz');rows={r['uid']:r for r in selection['rows']};source=rows[UID]['sourceSHA256'];supportsha=rows[SUPPORT]['sourceSHA256'];accounts=[]
 identitypath=BASE/'government-xl-next-twenty-original-identity-v3-20261021/79318:0/identity.json';bind('identity',identitypath);identity=read(identitypath);assert identity['passed']and not identity['reasons']and identity['sourceSHA256']==source
 cp=identitypath.with_name('context.json');bind('identity',cp);context=read(cp);assert not [r for r in context['identity']['intersectingForms']if not r['sameParent']and not r['sharedOsmReference']]
 for mode in ['original','literal','leftF32','balancedF32']:
  f=take('foundation',mode+'/79318:0/foundation.json');assert f['triangles']==f['completeTerrainTriangles']==18086 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
  proof=take('foundation',mode+'/79318:0/support.json.gz')['rows'][0]['proof'];c=take('contacts',mode+'/79318:0.json.gz');assert {tuple(x['position'])for x in proof['unresolved']}=={tuple(x['witness']['position'])for x in c['targets']}
  finite=sum(bool(x['positiveContacts'])for x in c['targets']);remaining=[x for x in c['targets']if not x['positiveContacts']];p=take('paths',mode+'/79318:0.json.gz')
  assert p['sourceWorldSHA256']==c['sourceWorldSHA256']and p['supportWorldSHA256']==c['podiumWorldSHA256'];assert {tuple(x['witness']['position'])for x in p['rows']}=={tuple(x['witness']['position'])for x in remaining}
  for x in p['rows']:
   v=x['verifiedPath'];assert v and v['maximumResidualM']<=.001 and v['withinEndpointHeight']and v['maximumPathHeightM']<=v['endpointHeightCeilingM']+1e-9
  assert finite+len(p['rows'])==len(proof['unresolved'])==4
  accounts.append(dict(mode=mode,wholeFoundationFaces=18086,strictContacts=proof['strictContacts'],samples=proof['samples'],rawUnresolved=4,finiteIncidentContacts=finite,endpointBoundedPaths=len(p['rows'])))
 runtime=take('runtime','metrics.json');r=runtime['rows'][0];assert len(runtime['rows'])==1 and r['uid']==UID and r['sourceSHA256']==source and r['sourcePreserved']and not r.get('error')and r['missingTerrain']==0 and r['maxSamplerDelta']<=.004
 for path,h in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 mp=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(mp.read_bytes());assert mh==selection['manifestSHA256'];refs.append(mp)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];refs.append(pointer)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,SUPPORT)).fetchone()==('installed-verified',supportsha)
 reports=[]
 for width in [1280,390]:
  report=take('browser',f'{width}/staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==2
  for v in views:assert v['uid']==v['pick']==v['collision']==UID and v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and v['sourceSHA256']==source
  own=report['retainedNativeOwnViews'];assert len(own)==2
  for v in own:assert v['uid']==SUPPORT and v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and v['sourceSHA256']==supportsha
  if width==390:assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}=={UID}
  reports.append(bind('browser',BASE/NAMES['browser']/str(width)/'staged-browser.json'))
 cfg=HERE/'local'/NAMES['browser']/'browser-config-390.json';bind('browser',cfg);assert read(cfg)['terrain']==[]
 images=[]
 for w,file in [(1280,'staged-landsd-79318-0-1280-1500.png'),(390,'staged-landsd-79318-0-390-2200.png'),(1280,'staged-local-joint-original-tower-podium-contact-1280.png'),(1280,'staged-retained-own-landsd-224399-0-1280-1500.png')]:images.append(bind('browser',BASE/NAMES['browser']/str(w)/file))
 review=dict(uids=[UID],sourceSHA256ByUid={UID:source},supportSourceSHA256ByUid={SUPPORT:supportsha},currentSnapshotId=snapshot,currentManifest=dict(path=str(mp.relative_to(ROOT)),sha256=mh),identityAccepted=True,completeFoundationAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,accounts=accounts,rawRuntimeMetrics=r,rawStrictFailuresRetained=True,imagesActuallyViewed=images,browserReports=reports,terrainChanges=0,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publication=False,reviewer='Codex ROOT',basis='The unchanged original has positive exact identity and no unrelated footprint intersections. All complete original faces clear the compound foundation in four representations. Four strict warnings remain recorded, each supported by exact finite incident contacts or continuous original-face paths bounded by endpoint height. Ground-only gaps are retained but are not used as direct-ground requirements for this podium-supported source. No terrain or existing model is replaced: the exact installed podium source is independently hash/ledger verified and loaded in staged desktop/mobile own-view checks. This is a faithful original source port, not a complete architectural reconstruction.',visualLimitations='Desktop overview shows the arched roof and upper source body among surrounding buildings. The local contact close-up is obscured by a foreground building and supplies no visual clearance evidence. The retained-podium overview shows the complete assembly among neighbours; exact numerical proofs supply unseen contact coverage. Night materials have no procedural windows. Foreground buildings and UI can obscure portions; full source numerical proofs supply coverage.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);module('langham_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'one-original-exact-existing-podium-acceptance-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
