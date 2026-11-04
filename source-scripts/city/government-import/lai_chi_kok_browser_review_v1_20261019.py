"""Bind actually inspected desktop/mobile exports and exact current renderer."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from lai_chi_kok_renderer_revision_20261019 import resolve
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-browser-review-v1-20261019';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__),HERE/'lai_chi_kok_renderer_revision_20261019.py'];folders=[BASE/('government-xl-lai-chi-kok-browser-'+v+'-v10-20261019')for v in ['1280-joint','390-joint','390-retry']];integration=BASE/'government-xl-lai-chi-kok-renderer-depth-verification-v2-20261019'
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for d in [*folders,integration]:
  r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');refs.extend(resolve(e['path'],e['sha256'])for e in r['evidenceRefs'])
ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
previous=HERE/'local'/folders[0].name;cat=read(previous/'catalogue.json');sources={e['uid']:e['sha256']for e in cat['models']};assert len(sources)==8
report=dict(passed=True,errors=[],views=[],jointViews=[],retainedNativeOwnViews=[],sourceReports=[]);images=[]
for i,d in enumerate(folders):
 r=read(d/'staged-browser.json');assert r['passed']and not r['errors'];assert (d/'tested-world.js').read_bytes()==(ROOT/'3d-viewer/city/world.js').read_bytes()
 views=[v for v in r['views']if 'time'in v];assert len(views)==16
 for v in views:assert v['fullyFramed']and v['solidAppearance']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]and v['active']and v['visible']and not v['fallbackFaces']and not v['overflow']
 if i<2:
  assert len(r['jointViews'])==8 and len(r['retainedNativeOwnViews'])==6
  for joint in r['jointViews']:
   assert {m['uid']:m['sourceSHA256']for m in joint['models']}==sources
   for m in joint['models']:
    if m['active']:assert m['visible']and not m['fallbackFaces']and all(m['meshVisibility'])and not any(m['wireframeFlags'])
    else:assert not m['wanted']and m['fallbackFaces']>0
  for v in r['retainedNativeOwnViews']:assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']
  for v in views+r['retainedNativeOwnViews']:images.append(ref(d/v['file']))
 else:
  fails=[v for v in r['views']if v.get('phase')=='failed-download'];assert len(fails)==8 and {v['uid']for v in fails}==set(sources)and all(v['fallbackRetained']for v in fails)
 for key in ['views','jointViews','retainedNativeOwnViews']:
  report[key].extend([{**v,**({'file':str((d/v['file']).relative_to(ROOT))}if 'file'in v else{})}for v in r.get(key,[])])
 report['sourceReports'].append(ref(d/'staged-browser.json'))
assert len(images)==44;save(DOC/'staged-browser.json',report)
save(DOC/'ROOT-IMAGE-REVIEW.json',dict(reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,stagedBrowser=ref(DOC/'staged-browser.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),sourceCatalogue=ref(previous/'catalogue.json'),currentRenderer=ref(ROOT/'3d-viewer/city/world.js'),depthHelper=ref(ROOT/'3d-viewer/city/native-terrain-depth.js'),rendererEquivalence=ref(integration/'equivalence.json'),observations=['All22desktop and22mobile day/night exports inspected through contact sheets; all eight selected originals and three retained native own views visible.','The earlier broad terrain-over-platform artefact is absent. Source structures retain their complete original forms and disabled procedural windows.','Current renderer bytes exactly equal those privately injected in all three passed preview runs. Retiring original meshes remain valid visible geometry during asynchronous fallback replacement.','Existing background buildings retain their current night lighting. No architectural redesign or additional source identity claim is inferred from these images.'],installationApproved=False,liveVerificationRequired=True))
refs.extend([previous/'catalogue.json',ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/native-terrain-depth.js',ROOT/'3d-viewer/city/data/manifest.json']);refs.extend(ROOT/q['path']for q in images)
module('lai_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-eight-original-visual-and-private-browser-acceptance',list(dict.fromkeys(refs)),dict(uids=sorted(sources),visualAcceptance=True,installationApproved=False))
