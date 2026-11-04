"""Bind unchanged-source acceptance to exact runtime, neighbour and viewed browser evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kadoorie-source-review-v1-20261021';DOC=BASE/BATCH;UID='landsd/115799:0'
NAMES=dict(runtime='government-xl-kadoorie-private-runtime-v3-20261021',foundation='government-xl-kadoorie-runtime-foundation-v1-20261021',terrain='government-xl-kadoorie-private-terrain-v3-20261021',neighbours='government-xl-kadoorie-neighbours-v3-20261021',identity='government-xl-next-twenty-original-identity-v6-20261021',browser='government-xl-kadoorie-private-browser-v1-20261021')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,name in NAMES.items():
   p=BASE/name/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);pins[key]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(key,file):
  p=BASE/NAMES[key]/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[key][k],k;refs.append(p);return read(p)
 def image(key,file):
  p=BASE/NAMES[key]/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[key][k];refs.append(p);return dict(path=k,sha256=pins[key][k])
 row=take('runtime','selection.json.gz')['rows'][0];assert row['uid']==UID
 metrics=take('runtime','metrics.json');metric=metrics['rows'][0];source=row['sourceSHA256'];assert metric['sourceSHA256']==source
 policy=module('kadoorie_policy',HERE/'acceptance-policy.py');reasons=policy.reasons({**row,'state':'runtime-validated-awaiting-acceptance'},metric,metrics['profiles']['mobile']);assert not reasons,reasons
 identity=next(r for r in take('identity','summary.json')['rows'] if r['uid']==UID);assert identity['status']=='identity-passed' and not identity['reasons']
 foundation=take('foundation','115799:0.json');f=foundation['foundation'];assert f['triangles']==f['completeTerrainTriangles']==row['triangles']==17805
 assert f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0 and f['fullyBuriedAreaFraction']==0
 assert take('terrain','summary.json')['terrainValidationPassed']
 ordinary=take('neighbours','neighbour-checks.json');assert len(ordinary['rows'])==49 and not any(r['reasons'] for r in ordinary['rows'])
 native=take('neighbours','native-neighbour-checks.json');assert {r['uid'] for r in native['rows']}=={'landsd/270867:0'} and all(r['passed'] for r in native['rows'])
 loader=take('browser','validation.json');assert loader['loaderAccepted']==1 and not loader['exceptions']
 resolution=module('kadoorie_bottom_warning',HERE/'terrain_diagnostic_resolution.py').resolve_global_bottom_warning(loader['results'][0],metric,{**foundation,'strictFoundationAccepted':True});assert not resolution['remaining'],resolution
 reports=[];images=[]
 for width in [390,1280]:
  report=take('browser',f'{width}/staged-browser.json');assert report['passed'] and not report['errors']
  views=[v for v in report['views'] if 'time' in v];assert len(views)==2
  for v in views:
   assert v['uid']==UID and v['sourceSHA256']==source and v['fullyFramed'] and v['active'] and v['visible'] and v['solidAppearance'] and not v['fallbackFaces'] and v['pick']==v['collision']==UID
  if width==390:assert any(v.get('phase')=='failed-download' and v['fallbackRetained'] for v in report['views'])
  retained=report['retainedNativeOwnViews'];assert len(retained)==2 and all(v['uid']=='landsd/270867:0' and v['active'] and v['visible'] and not v['fallbackFaces'] for v in retained)
  for time in ['1500','2200']:images.append(image('browser',f'{width}/staged-landsd-115799-0-{width}-{time}.png'))
  images.append(image('browser',f'{width}/staged-retained-own-landsd-270867-0-{width}-1500.png'))
  p=BASE/NAMES['browser']/str(width)/'staged-browser.json';reports.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==take('runtime','selection.json.gz')['manifestSHA256'];refs.append(manifest)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==source;refs.append(asset)
 review=dict(uids=[UID],sourceSHA256ByUid={UID:source},identityAccepted=True,completeFoundationAccepted=True,runtimePolicyReasons=reasons,loaderWarningResolution=resolution,completeNeighbourInterpretationAccepted=True,checkedNativeUids=['landsd/270867:0'],ordinaryNeighbourCount=49,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reviewer='Codex ROOT',installationApproved=False,publication=False,basis='Exact original bytes and fixed source placement. Complete actual rendered foundation and strict runtime ground contact pass. All affected ordinary and detailed neighbours pass unchanged regression checks. Private terrain has validated coverage, overlaps and budget. Desktop/mobile day-night source appearance, picking, collision and mobile failed-download fallback verified.',visualLimitations='Original has unlit government material at night, with procedural windows disabled. Nearby buildings occlude portions of the retained neighbour; full numerical neighbour checks cover its complete source. No engineering or globally watertight interpretation asserted.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs.extend(HERE/n for n in ['acceptance-policy.py','terrain_diagnostic_resolution.py'])
 module('kadoorie_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-source-runtime-neighbour-and-visual-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
