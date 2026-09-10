"""Multi-view source comparison and conservative routing; never AI or automatic acceptance.

Run through screen.py compare. Exact results are cached by geometry, current inputs,
policy and engine hashes. A dry-run plan is not a model publication or review decision.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from shape_metrics import compare, POLICY, VERSION
from pilot import native_metrics

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def encode(d):return json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_bytes(encode(d)+b'\n');tmp.replace(p)

def route(state, native, audit, metrics, budget, profiles, landmark=False):
    # Current ledger acceptance wins; explicit rework must never become a new skip.
    if state in ('enhanced','good-to-go'):return 'skip',['current-unchanged-acceptance']
    if not metrics:return 'retain-pending',['geometry-unavailable-or-invalid']
    gates=[]
    if native.get('matches')!=1 or not native.get('identityMatches') or not native.get('recordedHeightsMatch') or native.get('state')!='packed-needs-placement-review':gates.append('source-identity-or-assembly-hold')
    if native.get('cachedOverlap',0)<.9 or native.get('cachedCentroidDistanceMetres',float('inf'))>2:gates.append('footprint-match-needs-investigation')
    if audit.get('flags') or audit.get('terrain',{}).get('state')!='sampled-source-footprint-envelope':gates.append('source-or-terrain-diagnostic')
    # Native cached terrain diagnostics are evidence only; do not call them placement approval.
    terrain=native.get('nativeTerrainDiagnostic',{})
    gaps=terrain.get('lowRimGapRange')
    if terrain.get('status')!='diagnostic-complete' or not gaps or gaps[0]<-.25 or gaps[1]>2:gates.append('native-support-or-terrain-review')
    if not budget or any(budget[k]>profiles['mobile'][k] for k in ('triangles','geometryBytes','residentBytes')):gates.append('runtime-budget-exception')
    kind=metrics['comparison']
    if state=='enhancement-required':return ('import-candidate' if not gates and kind=='material-difference' else 'retain-pending'), ['existing-rework-decision',*gates]
    if kind=='placement-only-difference':return 'retain-pending',['placement-offset-not-shape-benefit',*gates]
    if kind=='negligible-difference':
        if landmark:gates.append('landmark-adequacy-not-established-by-geometry')
        return ('retain-pending' if gates else 'keep-current-candidate'), ['negligible-multi-view-difference',*gates]
    if kind=='material-difference':
        return ('retain-pending' if gates else 'import-candidate'), ['material-multi-view-difference',*gates]
    return 'retain-pending',['comparison-inconclusive',*gates]


def cache_key(row, pair, engine):
    return digest(encode({'namespace':VERSION,'inputHash':row['inputHash'],'geometrySHA256':pair['geometrySHA256'],'engine':engine,'policy':POLICY}))


def valid_cached(value,key):
    if not isinstance(value,dict) or value.get('cacheKey')!=key or value.get('kind')!=VERSION or value.get('resultSHA256')!=digest(encode(value.get('result'))):raise ValueError('Corrupt or mismatched shape cache')
    return value['result']


class SharedCache:
    """Reuse the existing immutable audit store with a distinct hash namespace."""
    def __init__(self):
        sys.path.insert(0,str(HERE.parent/'shared-modelling'));from db import connect
        self.connect=connect
    def get_many(self,keys):
        with self.connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            return dict(c.execute('SELECT cache_key,result FROM astra_modelling.city_audit_cache WHERE cache_key=ANY(%s)',(keys,)).fetchall())
    def put_many(self,rows):
        from psycopg.types.json import Jsonb
        if not rows:return
        with self.connect() as c:
            with c.cursor() as cur:
                cur.executemany('INSERT INTO astra_modelling.city_audit_cache(cache_key,uid,source_sha,model_sha,pipeline_sha,terrain_sha,result) VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',[(*r[:-1],Jsonb(r[-1])) for r in rows])
            old=dict(c.execute('SELECT cache_key,result FROM astra_modelling.city_audit_cache WHERE cache_key=ANY(%s)',([r[0] for r in rows],)).fetchall())
            if any(old[r[0]]!=r[-1] for r in rows):raise ValueError('Immutable shared shape-cache disagreement')


def run(evidence,geometry,out,shared=False):
    started=time.perf_counter();e=json.loads(gzip.decompress(Path(evidence).read_bytes()));geometry=Path(geometry);out=Path(out)
    idx=read(geometry/'index.json');pairs={r['uid']:r for r in idx['rows']};native=defaultdict(list)
    for n in e['native']:
        for v in n['model']['matching']['viewerMatches']:native[v['uid']].append(n)
    # The source input contains current geometry, but a saved plan is never current authority by itself.
    engine=digest(b''.join((HERE/p).read_bytes() for p in ['shape_metrics.py','shape_geometry.mjs']))
    keys={uid:cache_key(e['rows'][uid],p,engine) for uid,p in pairs.items() if 'error' not in p}
    store=SharedCache() if shared else None;remote=store.get_many(list(keys.values())) if store else {};writes=[]
    cache=geometry.parent/'comparison-cache';cache.mkdir(exist_ok=True);results=[];hits=Counter();errors=[]
    for uid,row in sorted(e['rows'].items()):
        b=e['sources'][uid]['building'];a=e['audits'][e['auditKeys'][uid]['cacheKey']];n=native_metrics(b,native[uid]);pair=pairs.get(uid,{});metric=None;key=keys.get(uid)
        if key:
            try:
                raw=(geometry/pair['file']).read_bytes()
                if digest(raw)!=pair['sha256']:raise ValueError('Geometry file SHA mismatch')
                unpacked=gzip.decompress(raw)
                if digest(unpacked)!=pair['geometrySHA256']:raise ValueError('Decoded geometry SHA mismatch')
                data=json.loads(unpacked)
                if data['uid']!=uid or data['candidateSHA']!=n.get('assetSha256'):raise ValueError('Geometry source identity mismatch')
                path=cache/(key+'.json')
                cached=remote.get(key) if key in remote else read(path) if path.exists() else None
                if cached:
                    metric=valid_cached(cached,key);hits['shared' if key in remote else 'local']+=1
                else:
                    metric=compare(data['current'],data['candidate']);cached={'kind':VERSION,'cacheKey':key,'result':metric,'resultSHA256':digest(encode(metric))};hits['computed']+=1
                save(path,cached)
                if store and key not in remote:writes.append((key,uid,row['inputHash'],n['assetSha256'],engine,e['contextHash'],cached))
            except (ValueError,KeyError,OSError) as ex:errors.append({'uid':uid,'error':str(ex)});metric=None
        if pair.get('terrain'):n['nativeTerrainDiagnostic']=pair['terrain']
        action,reasons=route(row['state'],n,a,metric,pair.get('budget'),idx['profiles'],uid in set(e['landmarkUids']))
        results.append({'uid':uid,'name':b.get('name',''),'tile':e['sources'][uid]['tile'],'inputHash':row['inputHash'],'state':row['state'],
          'action':action,'comparison':metric['comparison'] if metric else None,'reasons':reasons,'cacheKey':key,'geometryFile':pair.get('file'),
          'metrics':metric,'native':n,'geometryError':pair.get('error')})
    if store:store.put_many(writes)
    sample_set=set(e['sampleUids']);sample=[r for r in results if r['uid'] in sample_set]
    summary={'version':VERSION,'mode':'bounded-validation-dry-run','sampleSize':len(sample),'controlCount':len(e['controlUids']),
      'counts':dict(Counter(r['action'] for r in sample)),'comparisons':dict(Counter(r['comparison'] or 'unavailable' for r in sample)),
      'reasonCounts':dict(Counter(reason for r in sample for reason in r['reasons'])),'cache':dict(hits),'sharedCacheWrites':len(writes),
      'geometryErrors':errors,'aiCalls':0,'modelReviewWrites':0,'screeningAcceptanceWrites':0,'publishedModels':0,
      'seconds':round(time.perf_counter()-started,3),'sourceCommit':e['sourceCommit'],'manifestDigest':e['manifestDigest'],'engineSHA256':engine,
      'evidenceSHA256':digest(Path(evidence).read_bytes()),'policy':POLICY,
      'qualification':'Geometry differences measure change, not architectural improvement or present-day accuracy. Candidates require validated acceptance and existing ownership/publication guards. Pending cases make no AI calls.'}
    out.mkdir(parents=True,exist_ok=True);save(out/'summary.json',summary)
    (out/'results.json.gz').write_bytes(gzip.compress(encode(results),mtime=0))
    save(out/'controls.json',[r for r in results if r['uid'] in e['controlUids']])
    save(out/'actions.json',{'authoritative':False,'automaticAcceptanceEnabled':False,'counts':summary['counts'],'rows':[{k:r[k] for k in ('uid','inputHash','action','comparison','reasons','cacheKey')} for r in results]})
    print(json.dumps({k:v for k,v in summary.items() if k not in ('policy','reasonCounts','geometryErrors')},indent=2))
    return summary,results


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,default=HERE/'local/shape-inputs.json.gz');p.add_argument('--geometry',type=Path,default=HERE/'local/shapes/geometry');p.add_argument('--out',type=Path,default=ROOT/'docs/astra-city/enhancement-screening/shape-pilot-1000');p.add_argument('--shared-cache',action='store_true')
    a=p.parse_args();run(a.evidence,a.geometry,a.out,a.shared_cache)

if __name__=='__main__':main()
