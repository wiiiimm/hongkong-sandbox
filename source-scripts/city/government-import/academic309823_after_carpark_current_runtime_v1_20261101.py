"""Capture three unchanged HKUST originals against current installed terrain only.

No private terrain substitution, source edits or acceptance transfer.
"""
import sys,uuid,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-academic309823-after-carpark-current-runtime-v1-20261101'
CAPTURE='government-xl-academic309823-after-carpark-current-selection-v1-20261101'
UIDS=['landsd/309823:0','landsd/309829:0','landsd/336320:0']
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
    assert reservations.owns(read(LOCAL/'reservation.json')) and not DOC.exists()
    receipt,pins=authenticate(BASE/CAPTURE)
    selectionpath=BASE/CAPTURE/'selection.json.gz'
    assert digest(selectionpath.read_bytes())==pins[str(selectionpath.relative_to(ROOT))]
    selection=read(selectionpath);assert sorted(r['uid']for r in selection['rows'])==UIDS
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']
    refs=[Path(__file__),BASE/CAPTURE/'result.json',selectionpath,manifest]
    for row in selection['rows']:
        source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==row['sourceSHA256']==row['candidate']['entry']['sha256']
        target=LOCAL/row['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);refs.extend([source,target])
        row['candidate']['path']=str(target.relative_to(ROOT))
    save(DOC/'selection.json.gz',selection)
    tool=HERE/'acceptance_metrics_multi_retained_v2.mjs'
    command=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
    with (DOC/'worker.log').open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=3600)
    metrics=read(DOC/'metrics.json');geometry=read(LOCAL/'runtime-geometry.json.gz')
    assert sorted(r['uid']for r in metrics['rows'])==UIDS and not any(r.get('error')for r in metrics['rows'])
    assert {r['uid']:r['sourceSHA256']for r in geometry['rows']}=={r['uid']:r['sourceSHA256']for r in selection['rows']}
    for name,sha in metrics['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    assert digest(manifest.read_bytes())==selection['manifestSHA256'] and reservations.owns(read(LOCAL/'reservation.json'))
    refs.extend([tool,DOC/'selection.json.gz',DOC/'metrics.json',LOCAL/'runtime-geometry.json.gz'])
    result=dict(uids=UIDS,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in selection['rows']},currentManifestSHA256=selection['manifestSHA256'],metrics=metrics['rows'],currentTerrainOnly=True,privateTerrainSubstitutions=0,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False)
    save(DOC/'summary.json',result)
    module('academic_current_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-unchanged-originals-actual-current-terrain-runtime',list(dict.fromkeys(refs)),result)

if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists()and not DOC.exists()
        claim=reservations.claim('academic-current-runtime-'+str(uuid.uuid4()),['building:'+u for u in [*UIDS,'landsd/26949:0']]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
