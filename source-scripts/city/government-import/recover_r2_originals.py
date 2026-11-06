"""Read exact allowlisted government originals from immutable R2 archives.

GET/HEAD only. No extraction paths from archives, database access, credentials in
outputs, R2 writes, model changes, acceptance or viewer publication.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def exact_bytes(raw,expected):
    if hashlib.sha256(raw).hexdigest()==expected:return raw,'exact'
    if raw[:3]==b'\x1f\x8b\x08':
        for os_byte in (3,255):
            candidate=raw[:9]+bytes([os_byte])+raw[10:]
            if hashlib.sha256(candidate).hexdigest()==expected:
                assert gzip.decompress(candidate)==gzip.decompress(raw)
                return candidate,'exact-gzip-os-header-recovery'
    raise ValueError('Pinned source hash mismatch')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--plan-sha256',required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert digest(a.plan)==a.plan_sha256
    plan=json.loads(a.plan.read_text());assert plan['bucket']=='hk-sandbox-assets' and plan['readOnlyR2'] is True
    targets=plan['targets'];archives=plan['archives']
    assert 0<len(targets)<=17 and 0<len(archives)<=17
    assert sum(x['bytes']for x in archives)<=8*1024**3
    wanted={}
    for t in targets:
        h=t['sourceSHA256'];assert re.fullmatch('[0-9a-f]{64}',h) and 0<t['bytes']<=128*1024**2
        assert h not in wanted;wanted[h]=t
    for obj in archives:
        h=obj['sha256'];assert re.fullmatch('[0-9a-f]{64}',h)
        assert obj['key']=='astra-modelling/objects/sha256/'+h[:2]+'/'+h
        assert 0<obj['bytes']<=2*1024**3
    assert not a.output.exists();a.output.mkdir(parents=True)
    account=os.environ['R2_ACCOUNT_ID'];assert re.fullmatch('[0-9a-fA-F]{32}',account)
    import boto3
    client=boto3.client('s3',endpoint_url='https://'+account+'.r2.cloudflarestorage.com',region_name='auto',
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
    outcomes=[];recovered={}
    for obj in archives:
        needed={h:t for h,t in wanted.items()if h not in recovered and obj['key']in t['archiveKeys']}
        if not needed:continue
        entry={'archiveSHA256':obj['sha256'],'expectedBytes':obj['bytes'],'recovered':[]}
        try:
            assert shutil.disk_usage(a.output).free>obj['bytes']*2+128*1024**2
            with tempfile.TemporaryDirectory(dir=a.output.parent)as temporary:
                archive=Path(temporary)/'archive.tar.gz'
                client.download_file(plan['bucket'],obj['key'],str(archive))
                assert archive.stat().st_size==obj['bytes'] and digest(archive)==obj['sha256']
                entry['archiveVerified']=True
                with tarfile.open(archive,'r|gz')as tar:
                    for member in tar:
                        h=Path(member.name).name.removesuffix('.glb.gz')
                        if h not in needed or h in recovered:continue
                        t=needed[h];assert member.isfile() and member.size==t['bytes']
                        with tar.extractfile(member)as stream:raw=stream.read(t['bytes']+1)
                        assert len(raw)==t['bytes'];raw,method=exact_bytes(raw,h)
                        target=a.output/(h+'.glb.gz');assert not target.exists();target.write_bytes(raw)
                        assert target.stat().st_size==t['bytes'] and digest(target)==h
                        recovered[h]={'uid':t['uid'],'sourceSHA256':h,'bytes':t['bytes'],'method':method,'archiveSHA256':obj['sha256']}
                        entry['recovered'].append(t['uid'])
        except Exception as error:
            # Exception messages can contain account endpoints. Preserve only
            # class and HTTP status; model/source negatives stay distinguishable.
            entry['errorClass']=type(error).__name__
            entry['httpStatus']=getattr(error,'response',{}).get('ResponseMetadata',{}).get('HTTPStatusCode')
        outcomes.append(entry)
    report={'planSHA256':a.plan_sha256,'requested':len(targets),'recovered':len(recovered),'rows':list(recovered.values()),
        'missing':[t['uid']for h,t in wanted.items()if h not in recovered],'archives':outcomes,
        'readOnlyR2':True,'sourceGeometryChanges':0,'databaseWrites':0,'publication':False}
    (a.output/'recovery-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'requested':len(targets),'recovered':len(recovered),'missing':len(report['missing']),'readOnlyR2':True}),flush=True)


if __name__=='__main__':main()
