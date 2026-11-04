"""Compare official structure memberships for owner76610 and five retained forms."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'retained-five-primary-records-v1-20261101';CAP=P+'retained-five-record-selection-v1-20261101';FETCH=P+'retained-five-official-records-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json'
    uids=['landsd/'+k+':0'for k in ['76610','68540','88780','252555','252556','252558']]
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-five-primary-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)]
    rebind=P+'owner64-foreign-current-rebind-v1-20261101';_,pins=authenticate(BASE/rebind);bp=BASE/rebind/'basic.json';assert digest(bp.read_bytes())==pins[str(bp.relative_to(ROOT))];refs.extend([bp,BASE/rebind/'result.json'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mr=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));assert mr['sha256']==read(BASE/rebind/'summary.json')['currentManifestSHA256'];refs.append(manifest)
    by={r['uid']:r for r in read(bp)['rows']};rows=[]
    for uid in uids:
        building=by[uid]['currentBuilding'];assert building['uid']==uid and building['buildingCSUID'].isalnum()
        rows.append(dict(uid=uid,source=dict(building=building)))
    save(BASE/CAP/'selection.json.gz',dict(rows=rows,manifestSHA256=mr['sha256'],qualification='Current BASIC form identifiers only; no original assets selected or identity approval.'))
    module('palazzo_five_record_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(CAP,'current-six-form-primary-record-selection',refs.copy(),dict(uids=uids,sourceGeometryChanges=0,installationApproved=False,publication=False))
    tool=HERE/'selected_original_primary_records_v1_20261025.py';out=BASE/BATCH;out.mkdir();refs.append(tool)
    with(out/'fetch.log').open('w')as log:subprocess.run([sys.executable,str(tool),'--batch',FETCH,'--capture',CAP],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    _,fetchpins=authenticate(BASE/FETCH);relations=BASE/FETCH/'relations.json';assert digest(relations.read_bytes())==fetchpins[str(relations.relative_to(ROOT))];refs.extend([relations,BASE/FETCH/'result.json',BASE/CAP/'result.json'])
    csuids={r['uid']:r['source']['building']['buildingCSUID']for r in rows};by_structure={u:sorted({int(f['attributes']['BuildingStructureID'])for f in read(relations)['features']if f['attributes']['BuildingCSUID']==csuids[u]})for u in uids};owner=set(by_structure['landsd/76610:0'])
    result=dict(uids=uids,currentManifest=mr,buildingCSUIDByUid=csuids,structureIDsByUid=by_structure,sharedOwnerStructureIDsByUid={u:sorted(owner&set(s))for u,s in by_structure.items()if u!='landsd/76610:0'},sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Exact primary relation comparison is context only. Common structure membership does not authorize source identity transfer, counterpart suppression, geometry edits, support or collision acceptance.')
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mr['sha256'];save(out/'summary.json',result)
    module('palazzo_five_membership_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-current-form-official-structure-membership-comparison',refs,result)
    print(result['sharedOwnerStructureIDsByUid'],flush=True)
if __name__=='__main__':main()
