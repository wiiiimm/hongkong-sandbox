"""Bounded parallel R2 transfer around the existing verified snapshot/restore format."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from dotenv import dotenv_values
from r2_snapshot import LocalStore,R2Store,PREFIX,digest,key_for,verify_object,snapshot,restore,safe_path


def objects(manifest):
    unique={}
    for row in manifest['files']:
        if row['kind']!='file':continue
        key=key_for(row['sha256']);size=row['bytes']
        if not isinstance(size,int) or size<0:raise ValueError('Invalid object size')
        if key in unique and unique[key]['bytes']!=size:raise ValueError('Conflicting object sizes')
        unique[key]=row
    return unique


def transfer(manifest, local, remote, workers=8, upload=True):
    if not 1<=workers<=16:raise ValueError('Workers must be 1–16')
    entries=list(objects(manifest).items());started=time.monotonic()
    stats={'verifiedObjects':0,'verifiedBytes':0,'uploadedObjects':0,'uploadedBytes':0}
    def one(item):
        key,row=item
        source=local.root/key
        if upload:
            if not source.is_file() or source.stat().st_size!=row['bytes'] or digest(source)!=row['sha256']:
                raise ValueError('Local object failed integrity check')
            added=remote.put(key,source)
        else:added=False
        # Always retrieve from remote, even if another local cache contains the same object.
        with tempfile.TemporaryDirectory() as temp:
            checked=Path(temp)/'checked'
            verify_object(remote,key,row['sha256'],row['bytes'],checked)
            if not upload:local.put(key,checked)
        return added,row['bytes']
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(one,item) for item in entries]
        for future in concurrent.futures.as_completed(futures):
            added,size=future.result()
            stats['verifiedObjects']+=1;stats['verifiedBytes']+=size
            if added:stats['uploadedObjects']+=1;stats['uploadedBytes']+=size
            if stats['verifiedObjects']%100==0:
                print(json.dumps({'phase':'upload' if upload else 'download',**stats}),flush=True)
    stats['seconds']=round(time.monotonic()-started,3)
    return stats


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['upload','restore'])
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--manifest-sha256')
    p.add_argument('--inventory',type=Path)
    p.add_argument('--env-file',type=Path,required=True)
    p.add_argument('--workers',type=int,default=8)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    for k,v in dotenv_values(a.env_file).items():
        if k.startswith('R2_') and v:os.environ[k]=v
    remote=R2Store('hk-sandbox-assets');local=LocalStore(a.cache)
    if a.operation=='upload':
        if not a.inventory:p.error('--inventory required for upload')
        result=snapshot(a.root,a.inventory,local,a.manifest,['unmodified-cli-restore'])
        manifest=json.loads(a.manifest.read_text())
        result['remoteTransfer']=transfer(manifest,local,remote,a.workers)
        # Make the checkpoint discoverable only after all payloads have verified readback.
        remote.put(result['manifestKey'],a.manifest)
        with tempfile.TemporaryDirectory() as temp:
            verify_object(remote,result['manifestKey'],result['manifestSHA256'],a.manifest.stat().st_size,Path(temp)/'manifest')
    else:
        if not a.manifest_sha256:p.error('--manifest-sha256 required for restore')
        key_for(a.manifest_sha256)
        key=PREFIX+'snapshots/'+a.manifest_sha256+'.json'
        with tempfile.TemporaryDirectory() as temp:
            downloaded=Path(temp)/'manifest';remote.get(key,downloaded)
            if digest(downloaded)!=a.manifest_sha256:raise ValueError('Remote manifest checksum mismatch')
            manifest=json.loads(downloaded.read_text())
            if manifest.get('version')!=1:raise ValueError('Unsupported manifest')
            commit=subprocess.check_output(['git','-C',str(a.root),'rev-parse','HEAD'],text=True).strip()
            if commit!=manifest['gitCommit']:raise ValueError('Restore checkout revision mismatch')
            for row in manifest['files']:safe_path(a.root.resolve(),row['path'])
            a.manifest.write_bytes(downloaded.read_bytes())
        result={'remoteTransfer':transfer(manifest,local,remote,a.workers,upload=False)}
        result.update(restore(a.root,a.manifest,local,a.manifest_sha256))
        result['manifestSHA256']=a.manifest_sha256
    result.update(bucket='hk-sandbox-assets',prefix=PREFIX,operation=a.operation)
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
