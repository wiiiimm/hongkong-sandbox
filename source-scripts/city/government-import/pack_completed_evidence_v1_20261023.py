"""Archive completed source evidence in bounded, byte-verified reproducible parts.

Original files and completed receipts remain untouched. No modelling or approval.
"""
import argparse,tarfile,io,gzip
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','source']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.source])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;source=base/a.source;assert not out.exists()
    receipt,pins=authenticate(source);refs=[Path(__file__),source/'result.json'];files=[]
    for path in sorted(p for p in source.rglob('*')if p.is_file()):
        sha=digest(path.read_bytes());key=str(path.relative_to(ROOT))
        assert path.name in ['result.json','neon-sync.json']or pins[key]==sha
        name=str(path.relative_to(source));assert '..'not in Path(name).parts and not Path(name).is_absolute()
        files.append(dict(originalPath=key,name=name,sha256=sha,bytes=path.stat().st_size))
    limit=32*1024*1024;chunks=[];current=[];size=0
    for row in files:
        stored=512+((row['bytes']+511)//512)*512;assert stored<limit,'One source file exceeds bounded archive-part budget'
        if current and size+stored>limit:chunks.append(current);current=[];size=0
        current.append(row);size+=stored
    if current:chunks.append(current)
    out.mkdir();parts=[];verified=set()
    for i,chunk in enumerate(chunks,1):
        path=out/f'evidence-part-{i:03d}.tar.gz'
        with path.open('wb')as rawout,gzip.GzipFile(filename='',mode='wb',fileobj=rawout,mtime=0,compresslevel=1)as compressed,tarfile.open(fileobj=compressed,mode='w|',format=tarfile.USTAR_FORMAT)as archive:
            for row in chunk:
                raw=(ROOT/row['originalPath']).read_bytes();assert digest(raw)==row['sha256']and len(raw)==row['bytes']
                info=tarfile.TarInfo(row['name']);info.size=len(raw);info.mtime=0;info.mode=0o644;info.uid=info.gid=0
                archive.addfile(info,io.BytesIO(raw))
        expected={r['name']:r for r in chunk}
        with tarfile.open(path,'r:gz')as archive:
            members=archive.getmembers();assert len(members)==len(expected)
            for info in members:
                assert info.isfile()and info.name in expected
                row=expected[info.name];raw=archive.extractfile(info).read();assert digest(raw)==row['sha256']and len(raw)==row['bytes']
                assert row['originalPath']not in verified;verified.add(row['originalPath'])
        part=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),bytes=path.stat().st_size,files=chunk);parts.append(part);refs.append(path)
        print(dict(part=i,files=len(chunk),compressedBytes=part['bytes']),flush=True)
    assert verified=={r['originalPath']for r in files}
    manifest=dict(originalFolder=str(source.relative_to(ROOT)),originalReceiptSHA256=digest((source/'result.json').read_bytes()),parts=parts,allArchivedBytesReadBack=True,originalFilesUnmodified=True)
    save(out/'archive-manifest.json',manifest)
    result=dict(uids=receipt['uids'],sourceJobId=receipt['jobId'],sourceReceipt=dict(path=str((source/'result.json').relative_to(ROOT)),sha256=manifest['originalReceiptSHA256']),files=len(files),originalBytes=sum(r['bytes']for r in files),archiveParts=len(parts),archiveBytes=sum(r['bytes']for r in parts),allArchivedBytesReadBack=True,sourceGeometryChanges=0,installationApproved=False,qualification='Lossless reproducible archive of complete original analysis evidence, including exact original paths/SHA256 for restoration. Original producer files/receipt unchanged. No source identity/support/model installation or optimisation credit.')
    save(out/'summary.json',result)
    module('completed_evidence_pack_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'lossless-completed-source-evidence-archive',refs,result)
    print({k:result[k]for k in ['files','originalBytes','archiveParts','archiveBytes']},flush=True)


if __name__=='__main__':main()
