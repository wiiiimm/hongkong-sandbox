"""Source-bound original acceptance review; preserves current guard thresholds."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho58849-source-review-v1-20261017';DOC=BASE/BATCH;UID='landsd/58849:0'
def folder(n):return BASE/('government-xl-yoho58849-'+n+'-20261017')
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'acceptance-policy.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in ['current-capture-v2','current-foundation-v1','current-identity-runtime-v2','private-browser-v1','private-browser-v2','neighbour-contacts-v1','baseline-contacts-v1']:
   d=folder(name);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 m=read(folder('current-capture-v2')/'metrics.json');row=read(folder('current-capture-v2')/'selection.json.gz')['rows'][0];v=read(folder('current-identity-runtime-v2')/'validation.json');assert v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0 and not v['concerns']
 failures=module('yoho_policy',HERE/'acceptance-policy.py').reasons(dict(row,state='runtime-validated-awaiting-acceptance'),m['rows'][0],m['profiles']['mobile']);assert failures==[]
 identity=read(folder('current-identity-runtime-v2')/'identity-context.json');assert identity['exactObjectAndCSUID'];assert read(folder('current-foundation-v1')/'foundation.json')['strictFoundationAccepted']
 baseline=read(folder('baseline-contacts-v1')/'summary.json');assert len(baseline['rows'])==5 and all(r['existingInterfacePresent']for r in baseline['rows'])
 for r in baseline['rows']:assert r['baselineHeightRange'][0]-.000001<=r['originalHeightRange'][0]and r['originalHeightRange'][1]<=r['baselineHeightRange'][1]+.000001
 for n in ['private-browser-v1','private-browser-v2']:
  b=read(folder(n)/'staged-browser.json');assert b['passed']and not b['errors']
 images=[folder('private-browser-v2')/('base-context-'+n+'.png')for n in ['east','west','north','south']]
 images += sorted(folder('private-browser-v1').glob('*.png'));assert len(images)==8
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 review=dict(uid=UID,sourceSHA256=row['sourceSHA256'],reviewer='Codex ROOT',policyReasons=failures,identityAccepted=True,placementAccepted=True,originalSourceReviewAccepted=True,inspectedImages=[ref(p)for p in images],observations=['Current exact ObjectId and CSUID match; production identity overlap0.997883 and centroid distance0.363108m pass without an exception.','All17433 current source triangles have drawn ground coverage, zero fully buried triangles; original low-rim gaps -0.012094..0.365m pass existing limits.','Five projected-overlap neighbours have pre-existing BASIC surface contacts. Original contacts are confined to their existing lower height bands. Counts are not volume or ownership proofs.','East/west/north close views show lower source walls meeting the retained podium and low structures; no conspicuous new detached or displaced source observed. South close view is occluded by an adjacent tower and provides no base-visibility evidence.','Current source contacts and unqualified component labels alone are not independent holds under the repository skill. No fallback suppression, new support dependency, terrain change or source geometry edit is needed for this placement.','Whole-source desktop/mobile day/night and failed-download fallback checks pass.'],limitations=['This is original-model acceptance, not optimisation variant approval or universal device-performance certification.','No claim of structural engineering certification, identical before/after intersection volumes, or legal ownership.'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,publication=False,newlyInstalled=0,nextStep='Prepare exact guarded no-terrain stage; install under publication lock with current-source fences, live browser verification and Neon installed ledger; commit and push on success.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs.extend([*[ROOT/p for p in pins],*images,folder('private-browser-v1')/'ROOT-IMAGE-INSPECTION.json'])
 result=module('yoho_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'yoho58849-original-source-acceptance-review-v1',refs,dict(uids=[UID],originalSourceReviewAccepted=True,policyReasons=failures,publication=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
