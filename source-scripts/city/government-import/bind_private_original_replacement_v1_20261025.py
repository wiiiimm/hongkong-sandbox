"""Bind fresh runtime/scope evidence to every explicit original terrain replacement."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','patch','runtime','scope']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in vars(a).values())
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={};receipts={}
    def take(batch,name):
        if batch not in pins:
            receipts[batch],pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    take(a.patch,'summary.json');proposal=receipts[a.patch];assert proposal['status']=='private-terrain-validator-passed'
    candidates=take(a.runtime,'terrain-candidates.json');scope=take(a.scope,'scope.json');assert len(candidates)==1
    candidate=candidates[0];assert candidate['path']==proposal['candidate']['path']and candidate['sha256']==proposal['candidate']['sha256']
    assert set(candidate['uids'])==set(proposal['uids'])==set(scope['uids'])and candidate['bounds']==scope['regionalParentExtent']
    path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256'];refs.append(path);patch=read(path)
    assert candidate['triangles']==len(patch['nativeMesh']['index'])//3
    replacements=proposal['replacedNativeTerrain'];assert replacements
    expected=[dict(url=r['url'],sha256=r['sha256'],retainedUids=r['targetUids'])for r in replacements]
    actual=candidate.get('replacesMany')or[candidate['replaces']];assert actual==expected
    positive={r['url']for r in scope['terrainContacts']if r['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in r['packedContacts'])}
    assert positive=={r['url']for r in replacements}
    retained=set()
    for old in replacements:
        path=ROOT/'3d-viewer'/old['url'];assert digest(path.read_bytes())==old['sha256'];refs.append(path);before=read(path)
        assert before['meta']['targetUids']==old['targetUids']and before['coarseCells']==old['coarseCells']
        assert set(old['targetUids'])<=set(scope['touchingNativeUids']);retained.update(old['targetUids'])
    assert set(patch['meta']['targetUids'])==set(proposal['uids'])|retained
    result=dict(uids=proposal['uids'],candidate=candidate,scope=scope,replacedNativeTerrain=replacements,sourceSHA256ByUid=proposal['sourceSHA256ByUid'],sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Exact fresh runtime/candidate/replacement/closed-neighbour-scope binding. Every positive-area overlap is one explicitly pinned replacement with every retained target preserved. Zero-area contacts remain in the full scope. Physical/native regression, seam coverage, support, browser and publication acceptance are not inferred.')
    save(out/'summary.json',result);module('fresh_original_replacement_binding',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-explicit-private-original-native-terrain-replacement-contract',refs,result)
if __name__=='__main__':main()
