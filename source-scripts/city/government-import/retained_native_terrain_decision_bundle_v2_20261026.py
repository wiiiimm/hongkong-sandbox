"""Combine strict native regressions and exact unchanged-terrain proofs, without reacceptance."""
import argparse,copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_native_nonregression_v1_20261023 import terrain_decision


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','owner','patch','inventory','neighbours']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--context',action='append',required=True);a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={};receipts={}
    def take(name,file):
        if name not in pins:receipts[name],pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
        p=base/name/file;assert digest(p.read_bytes())==pins[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    raw=take(a.neighbours,'summary.json');proposal=receipts.get(a.patch)
    if proposal is None:receipts[a.patch],pins[a.patch]=authenticate(base/a.patch);refs.append(base/a.patch/'result.json');proposal=receipts[a.patch]
    assert proposal['status']=='private-terrain-validator-passed'and proposal['uids']==[a.owner]
    assert set(raw['uids'])==set(proposal['uids'])|set(proposal['retainedNativeTerrainTargets'])
    inventory=take(a.inventory,'complete-bounds.json.gz');indexed={r['uid']:r for r in inventory['rows']};mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());assert pins[a.inventory][str(mp.relative_to(ROOT))]==pins[a.neighbours][str(mp.relative_to(ROOT))]==pins[a.patch][str(mp.relative_to(ROOT))]==msha;refs.append(mp)
    candidate=ROOT/proposal['candidate']['path'];assert digest(candidate.read_bytes())==proposal['candidate']['sha256']==pins[a.patch][str(candidate.relative_to(ROOT))];refs.append(candidate)
    installed={}
    for url in read(mp)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==pins[a.inventory][str(path.relative_to(ROOT))];refs.append(path)
        for entry in read(path)['models']:
            assert entry['uid']not in installed;installed[entry['uid']]=entry
    assert set(installed)==set(indexed)
    raw_rows={r['uid']:r for r in raw['nativeRows']};assert len(raw_rows)==len(raw['nativeRows'])and set(raw_rows)==set(raw['requiredNativeUids'])
    assert set(raw['nativeResolved'])=={u for u,r in raw_rows.items()if r['passed']}and not raw['basicFlags']
    failures={u for u,r in raw_rows.items()if not r['passed']};contexts={};context_refs={}
    for name in a.context:
        c=take(name,'summary.json');uid=c['nativeUid'];assert uid not in contexts and uid in failures and c['uids']==[a.owner]
        assert pins[name][str(candidate.relative_to(ROOT))]==proposal['candidate']['sha256']and pins[name][str(mp.relative_to(ROOT))]==msha
        assert c['rawNativeRegression']==raw_rows[uid]
        for actor in c['rows']:
            u=actor['uid'];assert u in installed and actor['sourceSHA256']==installed[u]['sha256']==indexed[u]['sourceSHA256']and actor['completeFourWorldBounds']==indexed[u]['completeFourWorldBounds']
        contexts[uid]=c;context_refs[uid]=dict(batch=name,summary=dict(path=str((base/name/'summary.json').relative_to(ROOT)),sha256=digest((base/name/'summary.json').read_bytes())))
    assert set(contexts)==failures,'Every raw failure needs its own exact current context; no extras accepted'
    decisions=[]
    for uid,r in raw_rows.items():decisions.append(copy.deepcopy(r)if r['passed']else terrain_decision(r,contexts[uid],installed))
    assert all(r['passed']for r in decisions)and{r['uid']for r in decisions}==set(raw['requiredNativeUids'])
    result=dict(uids=[a.owner],nativeNeighbourBatch=a.neighbours,sourceTerrainProposalBatch=a.patch,currentManifestSHA256=msha,candidate=proposal['candidate'],requiredNativeUids=raw['requiredNativeUids'],rawNativeResolved=raw['nativeResolved'],rawNativeFailures=sorted(failures),rawNativeRows=raw['nativeRows'],terrainDecisionResolved=sorted(raw_rows),terrainDecisionRows=decisions,unchangedNativeContexts=context_refs,rawBasicFlags=raw['basicFlags'],allTerrainChangeDecisionsPassed=True,existingNativeReaccepted=False,sourceGeometryChanges=0,nativeMetadataChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Strict passing rows retain their exact raw results. Each failing legacy support row requires an independently authenticated exact whole actor AND support terrain-face-multiset equality proof, exact current source/metadata hashes, unchanged burial metrics and an explicit existing helper terrain-only decision. All raw support failures remain false. This qualifies only the terrain change; no legacy source/support/identity approval, metadata edit, threshold change or installation credit.')
    save(out/'summary.json',result);refs.append(HERE/'retained_native_nonregression_v1_20261023.py');module('retained_native_decision_bundle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-exact-retained-native-terrain-change-decision-bundle',list(dict.fromkeys(refs)),result);print(dict(strictPassed=len(raw_rows)-len(failures),exactUnchangedContexts=len(failures),allTerrainChangeDecisionsPassed=True,existingNativeReaccepted=False),flush=True)

if __name__=='__main__':main()
