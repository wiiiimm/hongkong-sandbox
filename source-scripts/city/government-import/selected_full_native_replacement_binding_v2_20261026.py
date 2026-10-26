"""Bind one validated full native-envelope candidate to its exact current replacement."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest

def validate_envelope(cells, scoped_cells, old_cells, proof):
    assert cells == scoped_cells
    assert all(type(x) is int for x in cells + old_cells)
    a,b,c,d=old_cells;aa,bb,cc,dd=cells
    assert aa<=a<c<=cc and bb<=b<d<=dd, 'Full previous terrain envelope must remain covered'
    if cells != old_cells:
        assert proof['coarseCells'] == cells
        assert proof['allRetainedRenderedFacesAndMultiplicityPreserved'] is True
        assert proof['allExtraFacesMatchProductionRoot'] is True
        assert proof['geometryChangesToCapturedSurface'] == 0
        assert proof['completeCapturedFaces'] == proof['existingRenderedFaces'] + proof['exactAddedRootFaces']
        assert proof['exactAddedRootFaces'] > 0

from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','patch','runtime','scope']:ap.add_argument('--'+key,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.patch,a.runtime,a.scope]) and not out.exists()
    refs=[Path(__file__)];receipts={};pins={}
    for n in [a.patch,a.runtime,a.scope]:
        receipts[n],pins[n]=authenticate(base/n);refs.append(base/n/'result.json')
    def take(n,file):
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    proposal=receipts[a.patch];assert proposal['status']=='private-terrain-validator-passed'
    scope=take(a.scope,'scope.json');candidates=take(a.runtime,'terrain-candidates.json');assert len(candidates)==1
    candidate=dict(candidates[0]);assert candidate['path']==proposal['candidate']['path']and candidate['sha256']==proposal['candidate']['sha256']
    assert len(proposal['replacedNativeTerrain'])==1
    old=proposal['replacedNativeTerrain'][0];replacement=dict(url=old['url'],sha256=old['sha256'],retainedUids=old['targetUids'])
    assert candidate['replaces']==replacement
    oldpath=ROOT/old['path'];assert digest(oldpath.read_bytes())==old['sha256'];refs.append(oldpath)
    actual=read(oldpath);assert actual['coarseCells']==old['coarseCells']and actual['meta']['targetUids']==old['targetUids']
    path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256'];refs.append(path);patch=read(path)
    proof = take(a.patch,'retained-template-proof.json')
    assert proof['templatePath']==old['path'] and proof['templateSHA256']==old['sha256']
    validate_envelope(patch['coarseCells'],scope['regionalCoarseCells'],old['coarseCells'],proof)
    assert patch['meta']['parentTerrain']==actual['meta']['parentTerrain'] and patch['meta']['parentSha256']==actual['meta']['parentSha256']
    assert set(patch['meta']['targetUids'])==set(scope['uids'])==set(proposal['uids'])|set(old['targetUids'])
    assert set(scope['touchingNativeUids'])>=set(old['targetUids'])
    positive=[r for r in scope['terrainContacts']if r['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in r['packedContacts'])]
    assert len(positive)==1 and positive[0]['url']==old['url']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[a.scope][str(manifest.relative_to(ROOT))];refs.append(manifest)
    candidate.update(uids=scope['uids'],bounds=scope['regionalParentExtent'])
    result=dict(uids=scope['uids'],newSourceUids=proposal['uids'],candidate=candidate,replacedNativeTerrain=proposal['replacedNativeTerrain'],
                currentManifestSHA256=digest(manifest.read_bytes()),sourceSHA256ByUid=proposal['sourceSHA256ByUid'],
                sourceGeometryChanges=0,installationApproved=False,publication=False,
                qualification='Schema binding of an unchanged private candidate and exact whole current replacement. Full old extent and all original targets retained; every touching installed actor and all scoped forms still require fresh regression. No identity, physical or publication approval.')
    save(out/'summary.json',result)
    module('full_native_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-private-full-native-terrain-replacement-contract',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
