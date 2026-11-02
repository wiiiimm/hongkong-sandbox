"""Preserve completed desktop evidence and explicit mobile failure, no acceptance.

Rebind the private fixture to authenticated original/terrain/runtime inputs and
current public bytes before reusing desktop checks. No failed mobile check is
removed or promoted, and no visual qualification or publication is granted.
"""
import argparse,copy,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from original_coordinated_retained_contract_v1_20261027 import verify_metadata
from june_garden_publisher_hooks_v1_20261103 import SOURCES,SUPPORTS,P,SMALL

BASE=ROOT/'docs/astra-city/government-import'
OLD='government-xl-tower3-june-garden-six-original-full-browser-v4-20261103'
ATOMIC='government-xl-tower3-june-garden-six-original-private-atomic-browser-v3-20261102'
SCOPE='government-xl-tower3-227380-chain-current-checks-v1-20261102-scope'
BATCH='government-xl-june-garden-desktop-complete-mobile-held-v2-20261103'
PLAN=BASE/'government-xl-tower3-june-garden-six-originals-current-v1-20261102-plan.json'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';resources=read(PLAN)['resources']
    if not a.owned:
        assert not out.exists() and not local.exists()
        c=reservations.claim('june-desktop-rebind-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==set(resources)
    refs=[Path(__file__),PLAN];pins={}
    def checked(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return path
    def take(batch,path):return read(checked(batch,path))
    atomic=take(ATOMIC,BASE/ATOMIC/'summary.json');assert atomic['passed'] and atomic['cases']==7 and atomic['sourceSHA256ByUid']==SOURCES
    originals=take(ATOMIC,BASE/ATOMIC/'complete-unapproved-source-entries.json')
    acfg=take(ATOMIC,HERE/'local'/ATOMIC/'config.json')
    scope=take(SCOPE,BASE/SCOPE/'scope.json');retained=set(scope['touchingNativeUids']);assert len(retained)==69
    assert {'building:'+u for u in retained|set(SOURCES)}<=set(resources)
    take(ATOMIC,PLAN)
    prior=HERE/'local'/OLD;catalogue=read(prior/'catalogue.json')
    verify_metadata(catalogue['models'],SOURCES,SUPPORTS,originals,{P:None,SMALL:None})
    expected=copy.deepcopy(acfg)
    expected.update(stage=str(prior.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+OLD+'/catalogue.json',
        doc=str((BASE/OLD).relative_to(ROOT))+'/',additionalRetainedUids=sorted(retained),failureTestUids=[],
        catalogueReplacements=[],fitBox=True,captureDirectionByModel={u:[-1,2.6,-1] for u in sorted(SOURCES)})
    assert read(prior/'config.json')==expected
    assert read(prior/'source-forms.json')==take(ATOMIC,HERE/'local'/ATOMIC/'source-forms.json')
    for name in ['catalogue.json','config.json','source-forms.json']:refs.append(prior/name)
    for m in catalogue['models']:
        path=prior/m['asset'];assert digest(path.read_bytes())==m['sha256']==SOURCES[m['uid']];refs.append(path)
    for t in expected['terrain']:
        path=ROOT/t['source'];assert digest(path.read_bytes())==t['sha256'];refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';current=take(ATOMIC,manifest);entries={};assets=0
    for url in current['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for m in take(ATOMIC,path)['models']:
            assert m['uid'] not in entries;entries[m['uid']]=m
            asset=path.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256'];refs.append(asset);assets+=1
    assert len(entries)==assets==7095 and not set(SOURCES)&set(entries)
    for name in ['app.js','official-models.js','streaming.js','model-group-lifecycle.js','model-activation-groups.js','model-support.js','official-model-assets.js','tile-cache.js','model-variants.js','model-byte-cache.js']:
        checked(ATOMIC,ROOT/'3d-viewer/city'/name)
    desktop=BASE/OLD/'1280/staged-browser.json';mobile=BASE/OLD/'390/staged-browser.json'
    d,m=read(desktop),read(mobile);assert d['passed'] and not d['errors'] and m['errors'] and not m.get('passed')
    assert len(d['views'])==12 and {(r['uid'],r['time']) for r in d['views']}=={(u,t) for u in SOURCES for t in ['15:00','22:00']}
    assert len(d['retainedNativeOwnViews'])==138 and {(r['uid'],r['time']) for r in d['retainedNativeOwnViews']}=={(u,t) for u in retained for t in ['15:00','22:00']}
    for row in [*d['views'],*d['retainedNativeOwnViews']]:
        assert row['active'] and row['visible'] and row['fallbackFaces']==0
        assert row['sourceSHA256']==(SOURCES if row['uid'] in SOURCES else {u:entries[u]['sha256'] for u in retained})[row['uid']]
        assert row['originalTriangles']==(next(x for x in catalogue['models'] if x['uid']==row['uid']) if row['uid'] in SOURCES else entries[row['uid']])['triangles']
        refs.append(desktop.parent/row['file'])
    refs.extend([desktop,mobile,BASE/OLD/'browser.log',BASE/OLD/'complete-unapproved-source-entries.json',BASE/OLD/'source-tile-provenance.json'])
    assert read(BASE/OLD/'complete-unapproved-source-entries.json')==originals
    for width in [1280,390]:refs.append(prior/f'config-{width}.json')
    refs.extend((BASE/OLD/'390').glob('*.png'))
    bound={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs}
    assert reservations.owns(lease)
    summary=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,sourceBrowserBatch=OLD,
        desktopDiagnosticsPassed=True,mobileDiagnosticsPassed=False,mobileFailure=m['errors'],
        desktopReport=dict(path=str(desktop.relative_to(ROOT)),sha256=digest(desktop.read_bytes())),
        currentManifestSHA256=digest(manifest.read_bytes()),currentNativeActors=7095,retainedUids=sorted(retained),
        previousAssetsVerified=assets,allReboundInputs=bound,sourceGeometryChanges=0,sourcePoseChanges=0,
        visualAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
    save(out/'summary.json',summary)
    module('june_desktop_current_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-desktop-exact-current-inputs-mobile-failure-preserved',refs,summary)


if __name__=='__main__':main()
