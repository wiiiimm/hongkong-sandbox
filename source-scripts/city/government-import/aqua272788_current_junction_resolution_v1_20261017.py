"""Bind the exact source-junction interpretation to current complete foundation failures."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-aqua272788-current-junction-resolution-v1-20261017';DOC=BASE/BATCH
NAMES=['current-physical-v3','original-junction-review-v1','four-world-capture-v1','four-world-junction-v1','private-browser-v1'];T='landsd/272788:0';P='landsd/193086:0'
def folder(n):return BASE/('government-xl-aqua272788-'+n+'-20261017')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];receipts={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);receipts[n]=r
   for e in r['evidenceRefs']:pins.setdefault(e['path'],set()).add(e['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 role=consume(folder('original-junction-review-v1')/'ROOT-SOURCE-REVIEW.json');assert role['sourceRoleInterpretationAccepted']and role['sourceSpecificFaces']==[32,1836]
 worlds=consume(folder('four-world-capture-v1')/'world-triangles.json.gz');junction=consume(folder('four-world-junction-v1')/'summary.json');assert junction['allFourModesVerified']
 current=folder('current-physical-v3');runtime=consume(HERE/'local'/current.name/'runtime-geometry.json.gz');ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);assert digest(ground.tobytes())==junction['groundSHA256']
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 helper=module('aqua_resolution_sample',HERE/'xl-final-script-pass.py');rows=[];cache={}
 for mode,w in worlds.items():
  t=np.array(w[T]);host=np.array(w[P]);key=(digest(t.tobytes()),digest(host.tobytes()))
  if key in cache:rows.append(dict(mode=mode,reusedMode=cache[key]['mode'],fullyBuriedFaces=cache[key]['fullyBuriedFaces']));continue
  combined=np.concatenate([ground,host]);polys=shapely.polygons(combined[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);heights=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),combined[valid],shapely.STRtree(polys[valid])).reshape(-1,4);gaps=points[:,:,1]-heights;failed=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1)).tolist();assert failed==[32,1836],(mode,failed)
  row=dict(mode=mode,sourceWorldSHA256=key[0],hostWorldSHA256=key[1],wholeSourceFaces=len(t),fullyBuriedFaces=failed,rawFailedSampleGaps=gaps[failed].tolist());rows.append(row);cache[key]=row
 raw=receipts['current-physical-v3']['reasons'];assert set(raw)=={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom','whole-source-foundation'}
 support=consume(current/'support-checks.json.gz')['rows'][0];assert support['interface']['passed']and support['interface']['strictContacts']==support['interface']['samples']==340 and not support['interface']['unresolved'];assert support['sourceSHA256']==role['sourceSHA256ByUid'][T]and support['supportSHA256']==role['sourceSHA256ByUid'][P]
 identity=consume(current/'identity-proofs.json')['rows'][0];assert identity['passed']
 neighbours=consume(current/'neighbour-checks.json');assert all(not row['reasons']for row in neighbours['rows']);native=consume(current/'native-neighbour-checks.json');assert not(set(native['blocked'])-set(native['resolved']))
 browser=folder('private-browser-v1');report=consume(browser/'staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==4
 for v in views:assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and v['pick']==v['collision']==T and v['sourceSHA256']==role['sourceSHA256ByUid'][T]and not v['fallbackFaces']
 assert any(v.get('phase')=='failed-download'and v['fallbackRetained']for v in report['views'])
 images=sorted(browser.glob('staged-*.png'));assert len(images)==4
 for p in images:assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p)
 resolution=dict(uid=T,sourceSHA256ByUid=role['sourceSHA256ByUid'],currentManifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),rawReasons=raw,remainingSourceSpecificReasons=[],rawStrictFoundationAccepted=False,sourceSpecificJunctionAccepted=True,fourWorldFailedFaceIdentities=rows,sourceRoleReview=dict(path=str((folder('original-junction-review-v1')/'ROOT-SOURCE-REVIEW.json').relative_to(ROOT)),sha256=digest((folder('original-junction-review-v1')/'ROOT-SOURCE-REVIEW.json').read_bytes())),strictOriginalSupportContacts=340,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,qualification='Only the exact two authored near-coincident podium side skins resolve the height-envelope foundation diagnostic. All other complete-source foundation faces remain under canonical checks in every world. Raw failure outputs preserved; no generic guard or numerical threshold changed. Installed original podium remains a mandatory dependency. Publication requires fresh qualification and guarded current-state checks.')
 save(DOC/'resolution.json',resolution);save(DOC/'ROOT-IMAGE-INSPECTION.json',dict(reviewer='Codex ROOT',sourceGeometryAppearanceAccepted=True,reviewedImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],notes='Four actual staged desktop/mobile day/night exports inspected. Original tower facade and roof detail remain solid, with plain government surfaces and no procedural windows. Existing adjacent towers naturally occlude some lower detail.'))
 refs.extend([HERE/'xl-final-script-pass.py',Path(helper.s.context.shared.__file__)])
 out=module('aqua_resolution_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-exact-current-source-junction-resolution-v1',refs,dict(uids=[T],sourceSpecificJunctionAccepted=True,remainingSourceSpecificReasons=[],publication=False,nextStep='Prepare qualified unchanged original catalogue with exact installed podium dependency, then guarded install and live browser verification.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
