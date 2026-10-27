"""Revalidate both exact reviewed provider units; retain every raw identity failure."""
import argparse
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from west_kowloon_pair_original_identity_review_v1_20261027 import EXPECTED

def unchanged_bounded_facts(old,new):
    assert set(old)==set(new)
    changed={k for k in old if old[k]!=new[k]}
    assert changed<={'exactRouteManifestSHA256','exactRouteTileHashes'},changed
    assert new['originalOwnership']['sourceGraphVerified'] and new['exactCurrentComponentRoute']['qualified']
    assert new['freshCurrentIdentity']['exactObjectAndCSUID']
    return sorted(changed)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--runtime',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-') and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[HERE/'revalidate_west_kowloon_pair_identity_v1_20261027.py']
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    oldprefix='government-xl-west-kowloon-north-pair-';fresh=oldprefix+'after-ocean-identity-v1-20261027'
    review=take(oldprefix+'identity-review-v1-20261027','summary.json');assert review['identityOnlyApproved'] and review['identityAccepted']
    selected=take(a.runtime,'selection.json.gz');assert {r['uid']for r in selected['rows']}==set(EXPECTED)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());refs.append(manifest);rows=[]
    for row in selected['rows']:
        uid=row['uid'];expected=EXPECTED[uid];filename=uid.split('/')[1]+'/identity.json'
        old=take(oldprefix+'identity-v1-20261027',filename);new=take(fresh,filename);changes=unchanged_bounded_facts(old,new)
        prior=next(r for r in review['rows']if r['uid']==uid);assert prior['identityAccepted'] and prior['identityOnlyApproved']
        assert row['sourceSHA256']==expected['sha256']==prior['sourceSHA256']==new['sourceSHA256']
        assert row['modelId']==expected['modelId']==prior['modelId']
        form=row['source']['building'];assert form['buildingCSUID']==expected['csuid']==prior['buildingCSUID'] and form['buildingId']==expected['buildingID']
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==form;refs.append(tile)
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==expected['sha256'];refs.append(asset)
        triangles=decode_original_world_triangles(raw);assert len(triangles)==expected['faces'] and digest(triangles.astype('<f8').tobytes())==prior['sourceWorldSHA256']==new['worldTrianglesSHA256']
        assert selected['manifestSHA256']==new['exactRouteManifestSHA256']==msha
        result=dict(prior,identityReviewApproved=True,changedRoutingFields=changes,rawIdentityVerbatim=new,currentManifestSHA256=msha,
                    physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False)
        save(out/uid.split('/')[1]/'ROOT-IDENTITY-REVIEW.json',result);rows.append(result)
    result=dict(uids=list(EXPECTED),rows=rows,sourceSHA256ByUid=review['sourceSHA256ByUid'],identityAccepted=True,identityOnlyApproved=True,
                sourceGeometryChanges=0,aiGeometryModelling=False,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Exact prior bounded provider-unit identity interpretation only. Complete old/fresh identity objects differ solely in permitted routing hashes; raw whole-cell, footprint and extent failures remain unchanged. Exact current immutable source bytes, world triangles, stable identifiers, base form and manifest are rechecked. No physical, visual or installation approval transfers.')
    save(out/'summary.json',result);refs.extend([HERE/'west_kowloon_pair_original_identity_review_v1_20261027.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('west_kowloon_pair_identity_revalidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-unchanged-bounded-provider-unit-identity-revalidation',refs,result)

if __name__=='__main__':main()
