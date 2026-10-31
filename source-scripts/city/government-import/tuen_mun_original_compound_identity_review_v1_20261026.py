"""Seal the exact twelve-source hospital compound identity review, separately from placement."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from tuen_mun_original_identity_contract_v1_20261026 import verify,OWNER,SOURCES


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-after-pok-oi-tuen-mun-'
    batch=prefix+'closed-compound-identity-review-v1-20261026';out=base/batch;assert not out.exists()
    refs=[Path(__file__),HERE/'tuen_mun_original_identity_contract_v1_20261026.py',HERE/'test_tuen_mun_original_identity_contract_v1_20261026.py']
    pins={};manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes())
    def take(name,file):
        folder=base/(prefix+name+'-20261026')
        if name not in pins:
            _,pins[name]=authenticate(folder);refs.append(folder/'result.json')
        path=folder/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take('twelve-runtime-evidence-v1','selection.json.gz');assert selection['manifestSHA256']==manifest_sha
    identities={}
    for n in ['eight-identity-v1','four-neighbour-identity-v1']:
        summary=take(n,'summary.json')
        for r in summary['rows']:
            identities[r['uid']]=take(n,r['uid'].split('/')[1]+'/identity.json')
    for r in selection['rows']:
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[r['uid']]['sourceSHA256'];refs.append(asset)
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256']
        assert next(f for f in read(tile)['buildings']if f['uid']==r['uid'])==r['source']['building'];refs.append(tile)
    owner={}
    for name,folder in [('official-site-plan-20150518.pdf','government-xl-tuen-mun-official-site-plan-20261009'),('official-hospital-about.html','government-xl-tuen-mun-hospital-owner-context-20261009')]:
        path=base/folder/name;owner[name]=digest(path.read_bytes());assert owner[name]==OWNER[name];refs.append(path)
    site=base/'government-xl-tuen-mun-official-site-plan-20261009';_,sitepins=authenticate(site)
    assert sitepins[str((site/'official-site-plan-20150518.pdf').relative_to(ROOT))]==OWNER['official-site-plan-20150518.pdf'];refs.append(site/'result.json')
    reviewed=[site/'official-site-plan-page-6.png',base/'government-xl-tuen-mun-hospital-owner-context-20261009/official-hospital-map.jpg']
    for n in ['336667','280350']:
        folder=base/(prefix+n+'-whole-identity-views-v1-20261026');_,bound=authenticate(folder);refs.append(folder/'result.json')
        for file in ['whole-source-plan.png','whole-source-perspectives.png']:
            path=folder/file;assert digest(path.read_bytes())==bound[str(path.relative_to(ROOT))];reviewed.append(path)
    refs.extend(reviewed)
    spatial=take('twelve-family-spatial-v1','summary.json');cell=take('main-cell-companion-d-v1','summary.json');dependency=take('proposed-dependency-coverage-v1','summary.json')
    assert spatial['currentManifestSHA256']==dependency['currentManifestSHA256']==manifest_sha
    result=verify(selection['rows'],identities,spatial,cell,dependency,owner)
    result.update(currentManifestSHA256=manifest_sha,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
                  sourceEvidenceInterpretationUsedAI=True,scriptExternalAICalls=0,
                  reviewedPreviouslyOpenedSourceAndOwnerImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in reviewed],
                  ownerContextLimitations='2015 not-to-scale site plan and schematic owner map corroborate the hospital campus/component context only; exact placement/identity metadata come from the government source IDs, current component routes and complete original geometry. No survey precision or current geometry inferred from the schematic.')
    refs.append(manifest);assert digest(manifest.read_bytes())==manifest_sha
    save(out/'ROOT-COMPOUND-IDENTITY-REVIEW.json',result)
    module('tuen_mun_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-twelve-exact-original-hospital-compound-identity-review',list(dict.fromkeys(refs)),result)
    print(dict(identityAccepted=result['identityAccepted'],sources=len(SOURCES),physicalAcceptance=False,installationApproved=False),flush=True)


if __name__=='__main__':main()
