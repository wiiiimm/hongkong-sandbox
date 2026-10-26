"""Join disjoint authenticated source/attribute captures for diagnostics only.

Does not merge terrain, neighbours, browser evidence or acceptance decisions.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True)
    p.add_argument('--runtime',action='append',required=True)
    p.add_argument('--attributes',action='append',required=True)
    a=p.parse_args()
    assert len(a.runtime)==len(a.attributes)>=2
    assert all(s.startswith('government-xl-')and '/'not in s for s in [a.batch,*a.runtime,*a.attributes])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs=[Path(__file__)];verified={};pins={};rows={};attrs={};origins={};headers=None;manifest_sha=None
    def take(batch,name):
        if batch not in pins:
            _,bound=authenticate(base/batch);pins[batch]=bound;refs.append(base/batch/'result.json')
            for path,sha in bound.items():
                assert path not in verified or verified[path]==sha,'Conflicting exact evidence'
                if path not in verified:
                    assert digest((ROOT/path).read_bytes())==sha,path
                    verified[path]=sha
        path=base/batch/name
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    input_hashes={}
    for runtime,attribute in zip(a.runtime,a.attributes):
        selected=take(runtime,'selection.json.gz');captured=take(attribute,'attributes.json.gz')
        assert captured['startEndAllInputsVerified']is True and captured['sourceGeometryChanges']==0
        assert captured['currentAcceptance']is False and captured['nativeReacceptance']is False
        header={k:v for k,v in captured.items()if k not in ['rows','inputHashes']}
        if headers is None:headers=header
        assert header==headers,'Different renderer/closure declarations'
        if manifest_sha is None:manifest_sha=selected['manifestSHA256']
        assert selected['manifestSHA256']==manifest_sha
        part={r['uid']:r for r in selected['rows']};attributes={r['uid']:r for r in captured['rows']}
        assert len(part)==len(selected['rows']) and len(attributes)==len(captured['rows'])
        assert set(part)==set(attributes) and not set(part)&set(rows)
        for uid,row in part.items():
            attr=attributes[uid];assert attr['sourceSHA256']==row['sourceSHA256']
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
            assert not any(row['candidate']['entry'].get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
            assert len(attr['completeOriginalIndex'])==row['triangles']*3
            tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
            assert next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
            rows[uid]=row;attrs[uid]=attr;origins[uid]=dict(runtime=runtime,attributes=attribute)
        for path,sha in captured['inputHashes'].items():
            assert path not in input_hashes or input_hashes[path]==sha
            assert digest((ROOT/path).read_bytes())==sha
            input_hashes[path]=sha;refs.append(ROOT/path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==manifest_sha;refs.append(manifest)
    save(out/'selection.json.gz',dict(rows=list(rows.values()),manifestSHA256=manifest_sha))
    save(out/'attributes.json.gz',dict(headers,rows=list(attrs.values()),inputHashes=input_hashes))
    result=dict(uids=sorted(rows),sourceOrigins=origins,currentManifestSHA256=manifest_sha,
                completeOriginalFaces=sum(r['triangles']for r in rows.values()),verifiedEvidenceFiles=len(verified),
                sourceGeometryChanges=0,sourcePoseChanges=0,groundEvidenceMerged=False,sceneAcceptanceTransferred=False,
                identityApproved=False,physicalAcceptance=False,installationApproved=False,newlyInstalled=0,publication=False,
                qualification='Disjoint complete source rows and identical-closure renderer attributes joined verbatim after current byte verification. For cross-batch numerical diagnostics only. No terrain, neighbour, physical, identity, browser, support or publication approval is merged.')
    save(out/'summary.json',result)
    module('merge_runtime_evidence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch,'disjoint-exact-original-runtime-attribute-evidence-join',list(dict.fromkeys(refs)),result)
    print(dict(sources=len(rows),faces=result['completeOriginalFaces']),flush=True)


if __name__=='__main__':main()
