"""Share storage for verified byte-identical immutable files, preserving every path."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import uuid
from run import ROOT,HERE,save
from publication_lock import locked_publication
from primrose_compound_foundation_v2_20261015 import module


def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def safe(path):
    relative=str(path.relative_to(ROOT));name=path.name
    assert not path.is_symlink()and path.is_file()and path.resolve().is_relative_to(ROOT.resolve())
    asset=bool(re.fullmatch('[0-9a-f]{64}\\.glb\\.gz',name))and relative.startswith(('source-scripts/city/','3d-viewer/city/data/'))
    geometry=name in {'parent-before.json','candidate-terrain.json','original-terrain.json','parent-template.json','child.json','before-validation-terrain.json'}and relative.startswith(('source-scripts/city/government-import/local/','source-scripts/city/government-import/accepted/','docs/astra-city/government-import/'))
    public_terrain=name.startswith('government-')and'terrain'in name and name.endswith('.json')and path.parent==ROOT/'3d-viewer/city/data'
    assert asset or geometry or public_terrain,'Not an immutable model/cache geometry path'


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    assert a.apply,'Audit is separate; explicit apply required'
    batch='government-xl-immutable-cache-storage-consolidation-v1-20261029';out=ROOT/'docs/astra-city/government-import'/batch
    assert not out.exists();audit=json.loads(Path(a.audit).read_text());out.mkdir();save(out/'audit.json.gz',audit)
    before=shutil.disk_usage(ROOT).free;changed=0;verified=0;groups=0;expected_reclaimed=0
    with locked_publication(ROOT),(out/'journal.ndjson').open('w')as journal:
        for group in audit['rows']:
            paths=[ROOT/s for s in group['paths']]
            for path in paths:
                safe(path);assert path.stat().st_size==group['bytes']and sha(path)==group['sha256'];verified+=1
            counts=collections.Counter(path.stat().st_ino for path in paths)
            paths.sort(key=lambda path:(path.stat().st_nlink==counts[path.stat().st_ino],not str(path.relative_to(ROOT)).startswith('3d-viewer/'),len(str(path))))
            source=paths[0];source_inode=source.stat().st_ino
            if len(counts)==1:continue
            groups+=1;inodes={path.stat().st_ino:path.stat().st_nlink for path in paths}
            expected_reclaimed+=sum(group['bytes']for inode,n in counts.items()if inode!=source_inode and n==inodes[inode])
            # Content-addressed originals and frozen terrain assets are immutable;
            # read-only links also fail closed on accidental in-place rewrites.
            os.chmod(source,0o444)
            for path in paths[1:]:
                if path.stat().st_ino==source_inode:continue
                assert sha(path)==group['sha256']and sha(source)==group['sha256']
                temporary=path.with_name('.model-cache-share-'+uuid.uuid4().hex)
                try:
                    os.link(source,temporary);os.replace(temporary,path)
                finally:temporary.unlink(missing_ok=True)
                assert path.stat().st_ino==source_inode and sha(path)==group['sha256']
                changed+=1;journal.write(json.dumps(dict(path=str(path.relative_to(ROOT)),sha256=group['sha256'],bytes=group['bytes']))+'\n');journal.flush()
    result=dict(uids=[],filesVerified=verified,immutableDuplicateGroups=groups,pathsStorageShared=changed,
                expectedPhysicalBytesReclaimed=expected_reclaimed,freeBytesBefore=before,freeBytesAfter=shutil.disk_usage(ROOT).free,
                allPathsPreserved=True,allBytesPreserved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,
                modelAcceptanceChanges=0,publication=False,acquisitionFloorBytes=3*1024**3,acquisitionGuardChanged=False,
                qualification='Every candidate path was restricted to immutable content-addressed model bytes or frozen terrain assets. Full size/SHA256 checks precede every replacement and follow every new hard link. Atomic directory-entry replacement preserves every file and byte; no reference source, mutable manifest, credentials, database schema or model acceptance row is changed. Shared files are read-only and must never be rewritten in place.')
    save(out/'summary.json',result)
    module('immutable_cache_consolidation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'byte-preserving-immutable-local-cache-storage-consolidation',[Path(__file__),out/'audit.json.gz',out/'journal.ndjson'],result)
    print({k:v for k,v in result.items()if k!='qualification'},flush=True)


if __name__=='__main__':main()
