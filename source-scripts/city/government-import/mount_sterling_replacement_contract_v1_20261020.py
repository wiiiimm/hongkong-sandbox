"""Bind private terrain replacement to the complete installed parent actor scope."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-replacement-contract-v1-20261020';DOC=BASE/BATCH;PROPOSAL=BASE/'government-xl-mount-sterling-private-surface-v1-20261020';SCOPE=BASE/'government-xl-mount-sterling-current-scope-v2-20261020'
def main():
    assert not DOC.exists();refs=[Path(__file__)];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (PROPOSAL,SCOPE):
            r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rows=take(PROPOSAL,PROPOSAL/'terrain-candidates.json');scope=take(SCOPE,SCOPE/'scope.json')['rows'][0];assert len(rows)==len(scope['overlappingInstalledTerrain'])==1
    parent=scope['overlappingInstalledTerrain'][0];r=rows[0];assert r['replaces']['url']==parent['url'] and r['replaces']['sha256']==parent['sha256'];r['replaces']['retainedUids']=parent['parentNativeUids'];r['uids']=['landsd/289787:0'];assert len(r['replaces']['retainedUids'])==11
    for p,h in [(r['path'],r['sha256']),('3d-viewer/'+parent['url'],parent['sha256'])]:assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    save(DOC/'terrain-candidates.json',rows);save(DOC/'summary.json',dict(uids=r['uids'],requiredNativeUids=parent['parentNativeUids'],installationApproved=False,geometryChanges=0))
    module('mount_sterling_contract_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-parent-retained-replacement-contract',refs,dict(uids=r['uids'],requiredNativeUids=parent['parentNativeUids'],installationApproved=False))
if __name__=='__main__':main()
