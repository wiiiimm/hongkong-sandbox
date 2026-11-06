"""Archive verified regional source/variant bytes for a portable data handoff.

No registry changes, approval or runtime publication. Keeps content identities and
independently reads every archived object/receipt back before reporting success.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[3]


def sha(data):return hashlib.sha256(data).hexdigest()


def build(report,recipes,output):
    report=report.resolve();output=output.resolve();assert report.is_relative_to(ROOT)and output.is_relative_to(ROOT)
    assert not output.exists()
    source_bytes=(report/'sources.json.gz').read_bytes();snapshot=json.loads(gzip.decompress(source_bytes))
    variants=json.loads(gzip.decompress((report/'variants.json.gz').read_bytes()))
    summary=json.loads((report/'summary.json').read_bytes())
    assert summary['models']==len(snapshot['selected'])and summary['variants']==len(variants)and summary['failedVariants']==0
    assert not summary['published']and summary['modelReviewWrites']==0
    members={};objects={}
    for row in snapshot['selected']:
        p=Path(row['inputPath']).resolve();assert p.is_relative_to(ROOT)
        raw=p.read_bytes();assert sha(raw)==row['sourceSha256'];objects[sha(raw)]=raw
    for row in variants:
        p=(ROOT/row['artifact']['path']).resolve();assert p.is_relative_to(ROOT)
        raw=p.read_bytes();assert sha(raw)==row['artifact']['sha256'];objects[sha(raw)]=raw
        receipt=(ROOT/row['report']).read_bytes();assert sha(receipt)==row['reportSha256']
        members['receipts/'+row['variantId']+'.json']=receipt
    members.update({'objects/'+digest+'.glb.gz':raw for digest,raw in objects.items()})
    for name in ('sources.json.gz','variants.json.gz','summary.json','neon-sync.json'):
        members['metadata/'+name]=(report/name).read_bytes()
    for p in sorted(recipes.glob('*.json')):members['recipes/'+p.name]=p.read_bytes()
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb')as f,gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0)as zipped,tarfile.open(fileobj=zipped,mode='w|')as archive:
        for name,raw in sorted(members.items()):
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(raw))
    verified=set()
    with tarfile.open(output,'r:gz')as archive:
        for info in archive:
            assert info.isfile()and info.name in members and info.name not in verified
            raw=archive.extractfile(info).read();assert raw==members[info.name]
            if info.name.startswith('objects/'):assert sha(raw)==Path(info.name).name.removesuffix('.glb.gz')
            verified.add(info.name)
    assert verified==set(members)
    result={'bundlePath':str(output.relative_to(ROOT)),'bundleSha256':sha(output.read_bytes()),'bundleBytes':output.stat().st_size,
        'models':summary['models'],'variants':len(variants),'uniqueSourceAndVariantObjects':len(objects),'receipts':len(variants),
        'allMembersReadBackExactly':True,'sourceSnapshotSha256':summary['sourceSnapshotSha256'],'published':False,
        'validationStatus':'unreviewed','qualification':'Portable source/candidate geometry, immutable processing receipts and metadata only; no viewer/terrain/runtime package or inherited quality approval.'}
    (report/'portable-bundle.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('report','recipes','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(a.report,a.recipes,a.output)
