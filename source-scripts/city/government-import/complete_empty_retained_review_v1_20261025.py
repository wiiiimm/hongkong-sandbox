"""Bind explicit empty retained-native metadata to a complete separation proof.

Only completes an already accepted source review's reporting fields. Rejects
any nominated/contacting retained actor; never changes source or review policy.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','review','scope','contacts']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    review=take(a.review,'ROOT-SOURCE-REVIEW.json');physical=take(a.review,'ROOT-PHYSICAL-REVIEW.json');assert review==physical
    assert all(review[k] for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
    assert review['retainedNativeUids']==[] and review['supportByUid']=={} and review['terrainEdits'] is False
    scope=take(a.scope,'summary.json');contacts=take(a.contacts,'summary.json')
    assert contacts['emptyNativeContactSetProved'] and contacts['rows']==[]
    assert set(scope['uids'])==set(contacts['uids'])==set(review['sourceSHA256ByUid'])
    assert scope['currentManifestSHA256']==contacts['currentManifestSHA256']==review['currentManifest']['sha256']
    for r in scope['rows']:
        assert r['sourceSHA256']==review['sourceSHA256ByUid'][r['uid']] and r['nearbyNativeActors']==[]
        proof=next(x for x in contacts['boundsProofs'] if x['uid']==r['uid'])
        assert proof['currentNativeActorsChecked']==r['currentNativeActorsChecked'] and proof['completeSourceFourWorldBounds']==r['completeSourceFourWorldBounds']
    for k,v in [('retainedNativeEntries',{}),('retainedImagesActuallyViewed',[])]:
        assert k not in review or review[k]==v
        review[k]=v
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==review['currentManifest']['sha256'];refs.append(manifest)
    review['emptyRetainedMetadataEvidence']=dict(review=a.review,scope=a.scope,contacts=a.contacts)
    save(out/'ROOT-SOURCE-REVIEW.json',review);save(out/'ROOT-PHYSICAL-REVIEW.json',review)
    module('empty_retained_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-empty-retained-metadata-binding-no-new-source-approval',refs,review)

if __name__=='__main__':main()
