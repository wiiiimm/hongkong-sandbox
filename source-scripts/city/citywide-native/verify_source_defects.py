"""HKS-222: bounded original-member verification for failed native JSON sources.

Read-only Neon queries and conditional government byte ranges; no converter/DB
mutations. Only CRC-verified NUL-only glTF plus CRLF is classified as corruption.
Existing proofs are reusable only for identical frozen source/member identities.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import urllib.request

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source_defect_acquisition',HERE.parent/'landmark-acquisition/acquire.py');ac=importlib.util.module_from_spec(spec);spec.loader.exec_module(ac)


def nul_only(raw):
    return len(raw)>2 and raw.endswith(b'\r\n') and raw[:-2]==b'\x00'*(len(raw)-2)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_member(source, directory_bytes, model_id, max_range_bytes=1024*1024):
    """One exact member; never download/extract an entire source archive."""
    infos,check=ac.parse_directory(directory_bytes)
    name=f'BUILDING/{model_id}/{model_id}.gltf'
    matches=[(i,e)for i,e in enumerate(infos)if e.filename==name]
    if len(matches)!=1:raise ValueError('Missing/duplicate indexed glTF member')
    i,entry=matches[0];start=entry.header_offset;end=(infos[i+1].header_offset if i+1<len(infos) else check['centralDirectoryOffset'])-1
    if end-start+1>max_range_bytes or entry.file_size>max_range_bytes:
        raise ValueError('Failed JSON member exceeds explicit read bound')
    req=urllib.request.Request(source['sourceURL'],headers={'Range':f'bytes={start}-{end}','If-Match':source['etag']})
    with urllib.request.urlopen(req,timeout=30)as response:
        if response.status!=206 or response.headers.get('ETag')!=source['etag']:
            raise ValueError('Range response/source revision mismatch')
        content_range=response.headers.get('Content-Range','')
        if not content_range.startswith(f'bytes {start}-{end}/'):
            raise ValueError('HTTP Content-Range differs from requested member')
        blob=response.read(end-start+2)
        if len(blob)!=end-start+1:raise ValueError('Bounded response length mismatch')
    raw=ac.unpack_member(blob,entry)
    row={'sourceEntry':name,'memberSHA256':hashlib.sha256(raw).hexdigest(),'sourceCRC32':entry.CRC,'bytes':len(raw),'nulBytes':raw.count(b'\x00'),'sourceETag':source['etag'],'sourceURL':source['sourceURL'],'sourceHeaderOffset':start,'sourceCompressedBytes':entry.compress_size,'verifiedHTTPRange':[start,end],'verification':{'httpPartialContent206':True,'responseETagMatchedFrozenSource':True,'boundedMemberRangeLengthVerified':True,'contentRangeVerified':True,'originalZipCRCAndDecodedLengthVerified':True}}
    if nul_only(raw):
        row.update(classification='confirmed-source-corrupt',remainingBytesHex='0d0a',observation='Original government glTF consists solely of NUL bytes followed by CRLF; no recoverable JSON/accessor/node metadata.')
        row['verification'].update(jsonOpenBracePresent=False,utf8OrNulRemovalRecoversJSON=False)
    else:
        row.update(classification='unclassified-source-json-failure',prefixHex=raw[:24].hex(),observation='Original member verified but is not the proven NUL-only corruption pattern; no automatic repair or source classification.')
    return row


def inspect_cases(cases, previous, max_range_bytes=1024*1024):
    proofs={(r['sheet'],r['modelId'],r['nativeStageSourceSHA256']):r for r in previous}
    checked=[];confirmed=[];reused=0
    for case in cases:
        item=case['item'];plan=item['inputs']['plan'];source_path=ROOT/plan['directory'];raw_path=ROOT/plan['rawDirectory'];key=(case['sheet'],case['modelId'],case['sourceSHA256'])
        base={'sheet':case['sheet'],'modelId':case['modelId'],'nativeStageSourceSHA256':case['sourceSHA256'],'originalError':case['error']}
        try:
            if sha(source_path)!=item['inputs']['directoryJSONSha256']:raise ValueError('Directory JSON differs from frozen stage input')
            source=json.loads(source_path.read_text());raw=raw_path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=source['directorySHA256']:raise ValueError('Raw ZIP directory checksum mismatch')
            expected=hashlib.sha256(json.dumps([source['sourceURL'],source['etag'],source['directorySHA256']],separators=(',',':')).encode()).hexdigest()
            if expected!=case['sourceSHA256']:raise ValueError('Native source identity differs from frozen run')
            old=proofs.get(key)
            if old:
                infos,_=ac.parse_directory(raw);member=next((e for e in infos if e.filename==old['sourceEntry']),None)
                if member and member.CRC==old['sourceCRC32'] and member.file_size==old['bytes'] and old['sourceETag']==source['etag'] and old['classification']=='confirmed-source-corrupt':
                    confirmed.append(old);checked.append({**base,'classification':'confirmed-source-corrupt','reusedFrozenProof':True});reused+=1;continue
            proof={**base,**verify_member(source,raw,case['modelId'],max_range_bytes)}
            checked.append(proof)
            if proof['classification']=='confirmed-source-corrupt':confirmed.append(proof)
        except Exception as error:
            checked.append({**base,'classification':'verification-incomplete','error':f'{type(error).__name__}: {error}'})
    # Preserve previous frozen proofs; the final auditor independently checks source hashes.
    for p in confirmed:proofs[(p['sheet'],p['modelId'],p['nativeStageSourceSHA256'])]=p
    return {'models':sorted(proofs.values(),key=lambda p:(p['sheet'],p['modelId'],p['nativeStageSourceSHA256'])),'checked':checked,'currentCases':len(cases),'reusedFrozenProofs':reused,'newConfirmed':len(confirmed)-reused,'unclassifiedCurrentCases':sum(r['classification']!='confirmed-source-corrupt'for r in checked)}


def run(run_id,output,max_range_bytes):
    sys.path.insert(0,str(HERE.parent/'shared-modelling'));from db import connect
    from psycopg.rows import dict_row
    with connect()as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY');con.row_factory=dict_row
        snapshot=con.execute('SELECT now()::text AS value').fetchone()['value']
        rows=con.execute('''SELECT i.sheet,i.source_sha AS "sourceSHA256",i.input_json AS item,x->>'modelId' AS "modelId",x->>'error' AS error FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_results r USING(cache_key) JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE m.run_id=%s AND x->>'state'='failed' AND (x->'asset' IS NULL OR x->'asset'='null'::jsonb) AND (x->>'error' LIKE 'JSONDecodeError:%%' OR x->>'error' LIKE 'UnicodeDecodeError:%%') ORDER BY i.sheet,x->>'modelId' ''',(run_id,)).fetchall()
    previous=json.loads(output.read_text()).get('models',[])if output.exists()else[]
    result=inspect_cases(rows,previous,max_range_bytes)
    result.update(issue='HKS-222',runId=run_id,snapshotAt=snapshot,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Read-only failed-JSON query; exact conditional member range, ETag, original ZIP CRC/length. Only NUL-only bytes plus CRLF are classified. Existing proofs require matching frozen source/member identity.',converterChanged=False)
    output.parent.mkdir(parents=True,exist_ok=True);temporary=output.with_suffix(output.suffix+'.part');temporary.write_text(json.dumps(result,indent=2)+'\n');temporary.replace(output)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-id',required=True);p.add_argument('--output',type=Path,default=ROOT/'docs/astra-city/citywide-native/source-defect-audit.json');p.add_argument('--max-range-bytes',type=int,default=1024*1024);a=p.parse_args()
    if not 1<=a.max_range_bytes<=8*1024*1024:p.error('Range bound must be 1 byte through 8 MiB')
    result=run(a.run_id,a.output,a.max_range_bytes)
    print(json.dumps({k:result[k]for k in ('runId','snapshotAt','currentCases','reusedFrozenProofs','newConfirmed','unclassifiedCurrentCases')}))

if __name__=='__main__':main()
