"""Revalidate unchanged exact identity facts under fresh routing; no physical approval."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def identical_identity_facts(old,new):
    assert set(old)==set(new)
    changed={k for k in old if old[k]!=new[k]}
    assert changed<={'exactRouteManifestSHA256','exactRouteTileHashes'},changed
    assert old['sourceSHA256']==new['sourceSHA256']and old['sourceFormSHA256']==new['sourceFormSHA256']
    assert new['originalOwnership']['sourceGraphVerified']and new['exactCurrentComponentRoute']['qualified']
    assert new['freshCurrentIdentity']['exactObjectAndCSUID']and new['exactWholeCellCoverage']['covered']
    return sorted(changed)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','prior-review','identity','runtime','foreign','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.prior_review,a.identity,a.runtime,a.foreign])and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    old=take(a.prior_review,'ROOT-IDENTITY-REVIEW.json');assert old['uid']==a.uid and old['identityOnlyApproved']and old['identityReviewApproved']
    raw=take(a.identity,a.uid.split('/')[1]+'/identity.json');changed=identical_identity_facts(old['rawIdentityVerbatim'],raw)
    selected=take(a.runtime,'selection.json.gz');source=next(r for r in selected['rows']if r['uid']==a.uid)
    assert source['sourceSHA256']==old['sourceSHA256']==raw['sourceSHA256']and source['modelId']==old['modelId']
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==old['completeSourceFaces']and digest(tri.astype('<f8').tobytes())==old['worldTrianglesSHA256']==raw['worldTrianglesSHA256']
    footprint=old['freshPrimaryFootprint'];form=source['source']['building']
    assert footprint['BuildingCSUID']==form['buildingCSUID']and footprint['BuildingID']==form['buildingId']
    foreign=take(a.foreign,'summary.json');external=[r for r in foreign['rows']if r['uid']==a.uid]
    assert len(external)==3 and all(m['allFiniteContactPairs']==0 for r in external for m in r['modes'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==selected['manifestSHA256']==raw['exactRouteManifestSHA256']==pins[a.identity][str(manifest.relative_to(ROOT))];refs.append(manifest)
    for path,sha in raw['exactRouteTileHashes'].items():
        p=ROOT/path if path.startswith('3d-viewer/')else ROOT/'3d-viewer'/path
        assert digest(p.read_bytes())==sha;refs.append(p)
    result=dict(uid=a.uid,uids=[a.uid],modelId=source['modelId'],sourceSHA256=source['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],completeSourceFaces=len(tri),currentManifestSHA256=msha,identityOnlyApproved=True,identityReviewApproved=True,identityProof=old['identityProof'],rawIdentityVerbatim=raw,rawReasonsRetained=raw['reasons'],freshPrimaryFootprint=footprint,historicalIdentityReview=dict(path=str((base/a.prior_review/'ROOT-IDENTITY-REVIEW.json').relative_to(ROOT)),sha256=digest((base/a.prior_review/'ROOT-IDENTITY-REVIEW.json').read_bytes())),changedRoutingFields=changed,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Exact source bytes, all identity measurements, ownership graph, source-form hash, complete geographic cell and primary stable identifiers are unchanged. Only current scene-routing bindings may differ and are freshly authenticated. Historical identity interpretation is revalidated for this exact component; no prior physical, support, collision, visual, neighbouring-model or installation approval is transferred. Raw automatic extent failures remain recorded.')
    save(out/'ROOT-IDENTITY-REVIEW.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('unchanged_identity_revalidation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'fresh-routing-revalidation-of-exact-unchanged-original-identity',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
