"""Independent readback after live verification of both retained-basic originals."""
from pathlib import Path
import sys
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    installed=base/'government-xl-two-basic-supported-original-installed-v2-20261023'
    receipt,pins=authenticate(installed)
    assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=339,remaining=182)
    assert receipt['completeCurrentCatalogueModels']==6863
    refs=[Path(__file__),installed/'result.json'];verified=0
    for path,sha in pins.items():
        p=ROOT/path
        assert digest(p.read_bytes())==sha,path
        refs.append(p);verified+=1
    source=receipt['sourceSHA256ByUid']
    assert set(source)=={'landsd/312858:0','landsd/6801:0'}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);models=[b for url in m['officialModelCatalogues']for b in read(ROOT/'3d-viewer'/url)['models']]
    assert len(models)==len({b['uid']for b in models})==6863
    deps=receipt['retainedBasicSupportDependencies'];assert len(deps)==2
    by={b['uid']:b for b in models}
    for d in deps:
        model=by[d['uid']]
        assert model['sha256']==source[d['uid']]==d['sourceSHA256']
        assert all(model.get(k)is True for k in ['publicationApproved','placementReviewed','identityReviewApproved'])
        assert model['retainedBasicSupportDependencies']==[d]
        assert model['supportDependencies']==[dict(uid=d['supportUid'],state='surveyed-footprint-fallback')]
        assert d['supportUid']not in by
    guard=module('installed_retained_basic_guard',HERE.parent/'island-detail-integration/retained_basic_support.py')
    report={};guard.stage_retained_basic_support(ROOT,m,{},report,read)
    assert {(d['uid'],d['supportUid'])for d in report['retainedBasicSupportChecks']} >= {(d['uid'],d['supportUid'])for d in deps}
    exports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));browser=read(folder/'live-browser.json');assert browser['passed'] and not browser['errors']
        views=[v for v in browser['views']if 'time'in v];assert len(views)==4
        for v in views:
            support=next(d['supportUid']for d in deps if d['uid']==v['uid'])
            assert v['sourceSHA256']==source[v['uid']] and v['pick']==v['collision']==v['uid']
            assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces']
            assert set(v['retained'])=={support}
            r=v['retained'][support];assert r['loaded'] and not r['hidden'] and not r['detailedActive']
            path=folder/v['file'];assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
            exports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid,sha in source.items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    assert receipt['terrainEdits']is False and receipt['sourceGeometryChanges']==receipt['sourcePoseChanges']==0
    batch='government-xl-two-basic-supported-installed-root-readback-v2-20261023'
    output=dict(uids=sorted(source),passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=6863,verifiedEvidenceFiles=verified,liveExportsActuallyViewed=exports,retainedBasicSupportChecks=report['retainedBasicSupportChecks'],sourceGeometryChanges=0,terrainEdits=False,aiGeometryModelling=False)
    save(base/batch/'ROOT-READBACK.json',output)
    module('two_basic_installed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'installed-original-retained-basic-independent-readback',list(dict.fromkeys(refs)),output)


if __name__=='__main__':main()
