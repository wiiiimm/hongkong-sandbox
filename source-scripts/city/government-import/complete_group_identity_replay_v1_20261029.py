"""Replay two existing complete-group identity policies on current exact sources.

Only the policies' two singleton-extent reasons may be replaced. All other
fresh guarded identity failures remain binding; physical gates are separate.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH='government-xl-two-complete-groups-current-identity-v1-20261029'
SELECT='government-xl-six-current-clearance-v1-20261029-selection'
IDENTITY='government-xl-six-current-clearance-v1-20261029-identity'
HISTORICAL='government-xl-22-complete-group-official-context-v2-20261008'
CASES={'landsd/81743:0':'ocean_walk_complete_source_identity.py','landsd/120104:0':'siu_ho_wan_complete_source_identity.py'}

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(SELECT,base/SELECT/'selection.json.gz')
    for name in ['context.json.gz','official-context.json']:take(HISTORICAL,base/HISTORICAL/name)
    rows=[]
    for uid,filename in CASES.items():
        row=next(r for r in selection['rows']if r['uid']==uid);part=uid.split('/')[1]
        fresh=take(IDENTITY,base/IDENTITY/part/'identity.json');context=take(IDENTITY,base/IDENTITY/part/'context.json')
        tool=module('complete_group_current_'+part.replace(':','_'),HERE/filename);refs.append(HERE/filename)
        assert fresh['sourceSHA256']==row['sourceSHA256'] and set(fresh['reasons'])<=tool.REPLACED
        proof=tool.verify_files(row,context,HERE/'local'/BATCH/part)
        # An existing complete-group policy cannot erase any additional failure.
        assert set(fresh['reasons'])-set(proof.get('replacedSingletonExtentReasons',[]))==set()
        for path in [ROOT/row['candidate']['path'],ROOT/'3d-viewer'/row['source']['tile']]:refs.append(path)
        record=dict(uid=uid,sourceSHA256=row['sourceSHA256'],passed=proof['passed'],reasons=proof['reasons'],freshSingletonReasons=fresh['reasons'],completeGroupProof=proof,placementApproved=False,installationApproved=False)
        save(out/part/'identity.json',record);rows.append(record);print(dict(uid=uid,passed=proof['passed'],reasons=proof['reasons']),flush=True)
    result=dict(uids=list(CASES),rows=rows,allIdentityPoliciesPassed=all(r['passed']for r in rows),physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Existing exact-source complete-group policies replayed over current unchanged forms and authenticated historical official records. Only the two explicit singleton extent reasons can be replaced; no source, suppression, foundation, contact, runtime, browser or publication gate changes.')
    save(out/'summary.json',result)
    for name in ['routed_original_cell_identity.py','government_georef_cell_identity.py','original_source_ownership.py','xl-second-pass.py','xl-final-script-pass.py']:refs.append(HERE/name)
    module('complete_groups_current_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-current-existing-complete-group-identity-policy-replays',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
