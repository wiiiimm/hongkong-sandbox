"""Read current official footprint and structure records for six exact source IDs.

Source identity, geometry, placement, publication and membership are not inferred.
"""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-arena275446-after-palazzo-'
BATCH, CAP, FETCH = P+'primary-sequence-v1-20261101', P+'primary-selection-v1-20261101', P+'primary-records-v1-20261101'
UIDS = ['landsd/'+str(n)+':0' for n in [275446,318697,318701,318704,318722,318723]]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owned',action='store_true');a=parser.parse_args()
    lp=HERE/'local'/BATCH/'reservation.json'
    if not a.owned:
        assert not lp.parent.exists() and not (BASE/BATCH).exists()
        claim=reservations.claim('arena-primary-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());refs=[Path(__file__),manifest];sources={}
    for tile in read(manifest)['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];forms=read(path)['buildings']
        for form in forms:
            if form['uid'] in UIDS:
                assert form['uid'] not in sources
                sources[form['uid']]=dict(building=form,tile=tile['url'],tileSHA256=digest(path.read_bytes()));refs.append(path)
    assert set(sources)==set(UIDS)
    rows=[dict(uid=u,source=sources[u]) for u in UIDS]
    save(BASE/CAP/'selection.json.gz',dict(rows=rows,manifestSHA256=sha,qualification='Current form identifiers only; no source selection or approval.'))
    freezer=module('arena_primary_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freezer.freeze(CAP,'six-current-arena-form-primary-record-selection',list(dict.fromkeys(refs)),dict(uids=UIDS,sourceGeometryChanges=0,installationApproved=False,publication=False))
    out=BASE/BATCH;out.mkdir();tool=HERE/'selected_original_primary_records_v1_20261025.py'
    with (out/'fetch.log').open('w') as log:
        subprocess.run([sys.executable,str(tool),'--batch',FETCH,'--capture',CAP],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    receipt,pins=authenticate(BASE/FETCH);relation=BASE/FETCH/'relations.json';assert digest(relation.read_bytes())==pins[str(relation.relative_to(ROOT))]
    csuids={u:sources[u]['building']['buildingCSUID'] for u in UIDS}
    structures={u:sorted({int(f['attributes']['BuildingStructureID']) for f in read(relation)['features'] if f['attributes']['BuildingCSUID']==csuids[u]}) for u in UIDS}
    result=dict(uids=UIDS,currentManifestSHA256=sha,primaryJobId=receipt['jobId'],buildingCSUIDByUid=csuids,structureIDsByUid=structures,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification=__doc__)
    assert reservations.owns(lease) and digest(manifest.read_bytes())==sha
    save(out/'summary.json',result)
    freezer.freeze(BATCH,'current-six-arena-original-primary-record-comparison',list(dict.fromkeys(refs+[tool,BASE/CAP/'result.json',BASE/FETCH/'result.json',relation])),result)
    print(result,flush=True)

if __name__=='__main__':main()
