"""Lease-bound raw hierarchy inspection of an authenticated FBX acquisition."""
import argparse, subprocess, sys, uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from fbx_jsonb_literal_v1_20261103 import jsonb_literals
BASE=ROOT/'docs/astra-city/government-import'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--acquisition-batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.acquisition_batch])
    parent=BASE/a.acquisition_batch;receipt,pins=authenticate(parent);source_list=parent/'untouched-current-fbx-sources.json'
    assert digest(source_list.read_bytes())==pins[str(source_list.relative_to(ROOT))];rows=read(source_list)['rows'];assert rows and all(r['sourceGeometryChanges']==r['sourcePoseChanges']==0 for r in rows)
    uids=sorted({r['uid']for r in rows});assert set(uids)==set(receipt['uids'])
    out,local=BASE/a.batch,HERE/'local'/a.batch;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        c=reservations.claim('original-fbx-hierarchy-'+str(uuid.uuid4()),['building:'+u for u in uids]+['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    refs=[Path(__file__),HERE/'fbx_jsonb_literal_v1_20261103.py',parent/'result.json',source_list,HERE/'original_fbx_hierarchy_inspection_v1_20261103.py']
    for row in rows:
        path=(ROOT/row['sourcePath']).resolve();assert path.is_relative_to(ROOT) and digest(path.read_bytes())==row['sourceSHA256']==pins[str(path.relative_to(ROOT))];refs.append(path)
    target=out/'raw';arrays=local/'arrays';log=local/'blender.log';local.mkdir(exist_ok=True)
    command=['/usr/local/bin/blender','--background','--factory-startup','--python',str(HERE/'original_fbx_hierarchy_inspection_v1_20261103.py'),'--',str(source_list.relative_to(ROOT)),str(target.relative_to(ROOT)),str(arrays.relative_to(ROOT))]
    save(local/'command.json',command)
    with log.open('w')as output:subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=600)
    result=jsonb_literals(read(target/'inspection.json'));assert len(result['rows'])==len(rows) and all(r['sourceBytesUnchanged'] and r['sourceGeometryChanges']==r['sourcePoseChanges']==0 for r in result['rows'])
    assert reservations.owns(lease)
    result.update(uids=uids,sourceAcquisitionBatch=a.acquisition_batch,acquisitionJobId=receipt['jobId'],diagnosticOnly=True,publication=False,permanentRejection=False)
    for row in rows:assert digest((ROOT/row['sourcePath']).read_bytes())==row['sourceSHA256']
    save(out/'summary.json',result);refs.extend(p for folder in [out,local]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json')
    module('original_fbx_hierarchy_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'raw-original-fbx-all-hierarchies-and-polygons-inspection',refs,result)

if __name__=='__main__':main()
