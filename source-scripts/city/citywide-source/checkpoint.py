"""Pack HKS-221 working caches for the existing verified R2 checkpoint uploader."""
import argparse, gzip, hashlib, io, json, os, re, tarfile, tempfile
from pathlib import Path, PurePosixPath
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREFIXES=('source-scripts/city/citywide-source/cache/', 'source-scripts/city/citywide-audit/local/', 'docs/astra-city/citywide-source/', 'docs/astra-city/citywide-audit/')
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()
def permitted(name):
    p=PurePosixPath(name)
    return (not p.is_absolute() and '..' not in p.parts and '\\' not in name
            and not any(x.startswith('.env') or x=='__pycache__' for x in p.parts)
            and any(name.startswith(prefix) for prefix in PREFIXES))
def pack(output,audit_run):
    if not re.fullmatch(r"[0-9a-f]{64}",audit_run): raise ValueError("Select the final authoritative audit run ID")
    audit_root=ROOT/'source-scripts/city/citywide-audit/local'/audit_run
    reports=[json.loads(p.read_text()) for p in audit_root.glob('run-*.json')]
    if not (audit_root/'plan.json').is_file() or not list(audit_root.glob('results-*.jsonl.gz')) or not any(r.get('runId')==audit_run and r.get('expected',0)>0 and r.get('cached')==r['expected'] and r.get('missing')==0 for r in reports):
        raise ValueError('Selected audit run is absent or incomplete')
    summary=json.loads((ROOT/'docs/astra-city/citywide-source/summary.json').read_text())
    if summary['status']!='complete': raise ValueError('Finish the source directory run before making its final checkpoint')
    files=[]
    for prefix in PREFIXES:
        for p in sorted((ROOT/prefix).rglob('*')):
            if not p.is_file() or p.is_symlink(): continue
            name=p.relative_to(ROOT).as_posix()
            if not permitted(name): raise ValueError('Unexpected checkpoint path')
            if prefix.endswith('citywide-audit/local/') and p.relative_to(ROOT/prefix).parts[0]!=audit_run: continue
            files.append((p,name))
    output.mkdir(parents=True,exist_ok=True)
    manifest=[]
    with tempfile.NamedTemporaryFile(dir=output,delete=False) as raw:
        temporary=Path(raw.name)
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as gz, tarfile.open(fileobj=gz,mode='w|') as tar:
            for path,name in files:
                before=path.stat();blob=path.read_bytes();after=path.stat()
                if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns): raise ValueError('Working input changed during checkpoint')
                info=tarfile.TarInfo(name);info.size=len(blob);info.mode=0o644;tar.addfile(info,io.BytesIO(blob))
                manifest.append({'path':name,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()})
    sha=digest(temporary);archive=output/('citywide-'+sha+'.tar.gz');os.replace(temporary,archive)
    (output/'contents.json').write_text(json.dumps({'archiveSHA256':sha,'files':manifest},indent=2)+'\n')
    relative=archive.relative_to(ROOT).as_posix()
    inventory={'snapshotId':'HKS-221-'+sha,'rows':[{'path':relative,'kind':'file','gitTracked':False,'profiles':['unmodified-cli-restore']}]}
    (output/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    result={'archive':relative,'sha256':sha,'compressedBytes':archive.stat().st_size,'files':len(manifest),'decodedBytes':sum(x['bytes'] for x in manifest)}
    (output/'pack.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
def unpack(archive,sha,destination):
    if not re.fullmatch(r'[0-9a-f]{64}',sha) or digest(archive)!=sha: raise ValueError('Archive SHA mismatch')
    if destination.exists(): raise ValueError('Extract into a new empty destination, then reconcile with the checkout')
    # Validate every member before writing. Only regular files under the four cache/report roots are accepted.
    with tarfile.open(archive,'r:gz') as tar:
        members=tar.getmembers();seen=set()
        for member in members:
            if not member.isfile() or not permitted(member.name) or member.name in seen: raise ValueError('Unsafe or duplicate archive member')
            seen.add(member.name)
        destination.mkdir(parents=True)
        tar.extractall(destination,members=members,filter='data')
    print(json.dumps({'extractedFiles':len(members),'destination':str(destination)}))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['pack','unpack']);p.add_argument('--output',type=Path,default=HERE/'local');p.add_argument('--audit-run');p.add_argument('--archive',type=Path);p.add_argument('--sha256');p.add_argument('--destination',type=Path);a=p.parse_args()
    if a.operation=='pack':
        if not a.audit_run:p.error('pack needs --audit-run')
        pack(a.output.resolve(),a.audit_run)
    else:
        if not all((a.archive,a.sha256,a.destination)):p.error('unpack needs --archive, --sha256 and --destination')
        unpack(a.archive,a.sha256,a.destination)
if __name__=='__main__':main()
