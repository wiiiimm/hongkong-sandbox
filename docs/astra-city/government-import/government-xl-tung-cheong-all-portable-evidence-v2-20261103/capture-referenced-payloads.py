"""Archive exact private evidence bytes. No runtime assets, variants or approvals."""
import gzip,hashlib,json,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    assert not (OUT/'restore-map.json').exists()
    receipts=sorted(BASE.glob('government-xl-tung-cheong*/result.json'))
    assert receipts and all(p.parent!=OUT for p in receipts)
    needed={};sources=[]
    for p in receipts:
        raw=p.read_bytes();r=json.loads(raw)
        sources.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(raw),jobId=r['jobId']))
        for ref in r['evidenceRefs']:
            key=ref['path'];path=(ROOT/key).resolve()
            assert path.is_relative_to(ROOT)
            private=key.startswith('source-scripts/city/government-import/local/')
            large_current=(key.startswith('docs/astra-city/government-import/government-xl-tung-cheong') and path.stat().st_size>1000000)
            if not(private or large_current):continue
            assert not any(part.startswith('.env') for part in path.parts)
            assert key not in needed or needed[key]==ref['sha256']
            needed[key]=ref['sha256']
    groups=defaultdict(list)
    for key,h in needed.items():
        raw=(ROOT/key).read_bytes();assert sha(raw)==h;groups[h].append(key)
    prior_path=BASE/'government-xl-tung-cheong53799-portable-evidence-v1-20261103/restore-map.json'
    prior_raw=prior_path.read_bytes();prior={r['originalSHA256']:r for r in json.loads(prior_raw)['payloads']}
    payloads=[]
    for h,paths in sorted(groups.items()):
        raw=(ROOT/paths[0]).read_bytes();assert sha(raw)==h
        reused=h in prior
        if reused:
            target=ROOT/prior[h]['archivePath'];packed=target.read_bytes();assert sha(packed)==prior[h]['archiveSHA256']
        else:
            packed=gzip.compress(raw,compresslevel=6,mtime=0)
            target=OUT/(h+'.bytes.gz');assert not target.exists();target.write_bytes(packed)
        restored=gzip.decompress(target.read_bytes());assert restored==raw and sha(restored)==h
        for key in paths:assert sha((ROOT/key).read_bytes())==h
        payloads.append(dict(originalSHA256=h,originalBytes=len(raw),restorePaths=sorted(paths),archivePath=str(target.relative_to(ROOT)),archiveSHA256=sha(packed),archiveBytes=len(packed),reusedPriorArchive=reused))
    result=dict(purpose=__doc__,sourceReceipts=sources,priorArchiveMap=dict(path=str(prior_path.relative_to(ROOT)),sha256=sha(prior_raw)),payloads=payloads,sourceGeometryChanges=0,publication=False,optimisation=False,installationApproved=False,restoreRule='Verify archive SHA, decompress and verify original SHA/size. Restore only missing declared paths. Never overwrite a different existing file. Public/runtime files are not restore destinations.')
    (OUT/'restore-map.json').write_text(json.dumps(result,indent=2)+'\n')
    print(dict(receipts=len(sources),paths=len(needed),payloads=len(payloads),originalBytes=sum(x['originalBytes']for x in payloads),archiveBytes=sum(x['archiveBytes']for x in payloads)),flush=True)
if __name__=='__main__':main()
