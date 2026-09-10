"""Read-only, deterministic enhancement triage; recommendations never grant acceptance.

Capture current city inputs and exact audit-cache hits from the pinned Neon branch.
Replay the retained evidence to reproduce the report without a database or AI calls.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import heapq
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SEED = 'hks-screening-pilot-v1'
POLICY = 'pilot-triage-v1'
NATIVE_RUN = 'e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec'
ORDINARY = {'yes', 'house', 'apartments', 'residential', 'industrial', 'service',
            'retail', 'commercial', 'warehouse', 'semidetached_house', 'dormitory',
            'terrace', 'office'}
SPECIAL = {'stadium', 'grandstand', 'sports_centre', 'museum', 'temple', 'church',
           'cathedral', 'pavilion', 'transportation', 'train_station', 'terminal'}


def read(path):
    return json.loads(Path(path).read_bytes())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select(rows, count=1000, seed=SEED):
    if count < 1 or count > len(rows) or len({r['uid'] for r in rows}) != len(rows):
        raise ValueError('Invalid sample size or duplicate UID')
    return heapq.nsmallest(count, rows, key=lambda r: (hashlib.sha256(
        (seed + ':' + r['uid']).encode()).hexdigest(), r['uid']))


def native_metrics(building, outcomes):
    matches = []
    for outcome in outcomes:
        model = outcome['model']
        viewers = model.get('matching', {}).get('viewerMatches', [])
        for match in viewers:
            if match['uid'] == building['uid']:
                matches.append((outcome, match))
    if len(matches) != 1:
        return {'matches': len(matches)}
    outcome, match = matches[0]
    model = outcome['model']
    low, high = model['worldBounds']
    points = [p for ring in building['rings'] for p in ring]
    current_bounds = [min(p[0] for p in points), min(p[1] for p in points),
                      max(p[0] for p in points), max(p[1] for p in points)]
    native_bounds = [low[0], low[2], high[0], high[2]]
    return {'matches': 1, 'modelId': model['modelId'], 'sheet': outcome['sheet'],
            'stageCacheKey': outcome['cacheKey'], 'stageResultSha': outcome['resultSha'],
            'state': model['state'], 'triangles': model['triangles'],
            'assetSha256': model['asset']['sha256'], 'compressedBytes': model['asset']['bytes'],
            'identityMatches': bool(building.get('buildingCSUID')) and
                match.get('buildingCSUID') == building['buildingCSUID'],
            'recordedHeightsMatch': match.get('recordedBaseHeight') == building.get('baseHeightHKPD')
                and match.get('recordedTopHeight') == building.get('topHeightHKPD'),
            'cachedOverlap': match['overlapOfSmallerFootprint'],
            'cachedCentroidDistanceMetres': match['footprintCentroidDistanceMetres'],
            'maxBoundsDeltaMetres': round(max(abs(a-b) for a,b in zip(current_bounds, native_bounds)), 4),
            'baseDeltaMetres': round(low[1] - building['base'], 4),
            'topDeltaMetres': round(high[1] - building['base'] - building['height'], 4),
            'nativeTopHKPD': high[1], 'currentTopHKPD': building['base'] + building['height'],
            'nativeTerrainDiagnostic': model.get('terrainCheck', {})}


def classify(row, building, audit, native, landmark=False, triangle_limit=64):
    # Only current ledger acceptance grants a confirmed skip. A new rework decision wins.
    if row['state'] == 'enhancement-required':
        return 'enhancement-candidate', ['current-rework-decision']
    if row['state'] in {'enhanced', 'good-to-go'}:
        return 'confirmed-skip', ['existing-current-acceptance']
    reasons = []
    if row['geometry'] == 'footprint' and (landmark or building.get('kind') in SPECIAL):
        return 'enhancement-candidate', ['distinctive-use-or-landmark-with-footprint-only']
    if row['geometry'] != 'footprint':
        return 'review', ['existing-detail-without-current-acceptance']
    if audit['flags']:
        reasons.append('source-or-terrain-diagnostic')
    if audit['terrain']['state'] != 'sampled-source-footprint-envelope':
        reasons.append('terrain-not-checked')
    if building.get('heightSource') != 'landsd':
        reasons.append('estimated-height')
    if building.get('structureType') != 'Tower' or building.get('kind') not in ORDINARY:
        reasons.append('nonordinary-or-support-form')
    if len(building.get('rings', [])) != 1:
        reasons.append('holes-or-missing-footprint')
    if building['height'] > 60 or audit['areaM2'] > 1500:
        reasons.append('large-or-tall-form')
    if native['matches'] != 1:
        reasons.append('native-source-missing-or-ambiguous')
    else:
        if (not native['identityMatches'] or not native['recordedHeightsMatch'] or
                native['state'] != 'packed-needs-placement-review'):
            reasons.append('native-source-identity-or-state')
        if (native['cachedOverlap'] < .9 or native['cachedCentroidDistanceMetres'] > 2 or
                native['maxBoundsDeltaMetres'] > 2 or abs(native['baseDeltaMetres']) > 1.5 or
                abs(native['topDeltaMetres']) > 1.5):
            reasons.append('native-envelope-differs')
        if native['triangles'] > triangle_limit:
            reasons.append('native-mesh-complexity-needs-review')
    if reasons:
        return 'review', reasons
    return 'likely-skip', ['ordinary-surveyed-form-small-native-envelope-difference-low-complexity']


def capture(local, count, seed):
    sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
    from db import connect
    from screen import build_plan
    start = time.perf_counter()
    local.mkdir(parents=True, exist_ok=True)
    plan = build_plan(local / 'pilot-inputs.json.gz')
    sample = select(plan['rows'], count, seed)
    selected = {r['uid'] for r in sample}
    source, control = {}, []
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    for tile in manifest['tiles']:
        for building in read(ROOT / '3d-viewer' / tile['url'])['buildings']:
            is_control = building.get('name', '').casefold() == 'kai tak stadium'
            if building['uid'] in selected or is_control:
                source[building['uid']] = {'tile': tile['id'], 'building': building}
            if is_control:
                control.append(building['uid'])
    if not control:
        raise ValueError('Kai Tak Stadium source identity not found')
    ids = set(source)
    if not selected <= ids:
        raise ValueError('Sample source disappeared')
    # Generate fresh keys before reusing a cached audit; no cache-by-UID fallback.
    subprocess.run(['node', str(HERE.parent / 'citywide-audit/engine.mjs'), 'plan',
        str(local/'audit-plan.jsonl.gz'), str(local/'audit-meta.json')], cwd=ROOT, check=True)
    keys = {}
    with gzip.open(local/'audit-plan.jsonl.gz', 'rt') as stream:
        for line in stream:
            row = json.loads(line)
            if row['uid'] in ids:
                keys[row['uid']] = row
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        # The read-only pilot must not silently use an older shared screening proof.
        events = con.execute('''SELECT DISTINCT ON(uid) uid,input_hash,policy,decision,reason,evidence,evidence_hash
          FROM astra_modelling.enhancement_screening_events ORDER BY uid,id DESC''').fetchall()
        proof = read(ROOT/'3d-viewer/scripts/building-progress/screening-proof.json')
        fields = ['uid','inputHash','policy','decision','reason','evidence','evidenceHash']
        if sorted(tuple(r[k] for k in fields) for r in proof['rows']) != sorted(events):
            raise ValueError('Shared screening changed; refresh with screen.py plan before capture')
        audits = dict(con.execute('SELECT cache_key,result FROM astra_modelling.city_audit_cache WHERE cache_key=ANY(%s)',
                                 ([r['cacheKey'] for r in keys.values()],)).fetchall())
        outcomes = con.execute('''SELECT i.sheet,r.cache_key,r.result_sha,m
          FROM astra_modelling.native_stage_members member
          JOIN astra_modelling.native_stage_inputs i USING(cache_key)
          JOIN astra_modelling.native_stage_results r USING(cache_key)
          CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m
          WHERE member.run_id=%s AND EXISTS(SELECT 1 FROM jsonb_array_elements(m->'matching'->'viewerMatches') v
          WHERE v->>'uid'=ANY(%s))''', (NATIVE_RUN, sorted(ids))).fetchall()
    misses = [r for r in keys.values() if r['cacheKey'] not in audits]
    hits = len(audits)
    if misses:
        with gzip.open(local/'audit-misses.jsonl.gz', 'wt') as stream:
            for row in misses:
                stream.write(json.dumps(row)+'\n')
        subprocess.run(['node', str(HERE.parent/'citywide-audit/engine.mjs'), 'compute',
            str(local/'audit-results.jsonl.gz'), str(local/'audit-misses.jsonl.gz')], cwd=ROOT, check=True)
        with gzip.open(local/'audit-results.jsonl.gz','rt') as stream:
            audits.update((r['cacheKey'], r['result']) for line in stream if (r:=json.loads(line)))
    landmarks_path = ROOT/'docs/astra-city/landmark-registry/inventory-candidates.json'
    landmarks = sorted({c['uid'] for r in read(landmarks_path)['rows'] for c in r['candidates']})
    plan_rows = {r['uid']: r for r in plan['rows'] if r['uid'] in ids}
    if set(plan_rows) != ids or set(keys) != ids:
        raise ValueError('Control or sample is not a currently displayed source form')
    return {'version':1, 'seed':seed, 'policy':POLICY, 'capturedAt':datetime.now(timezone.utc).isoformat(),
        'population':len(plan['rows']), 'sampleUids':[r['uid'] for r in sample], 'controlUids':control,
        'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'manifestDigest':plan['manifestDigest'], 'contextHash':plan['contextHash'],
        'nativeRun':NATIVE_RUN, 'landmarkInventorySha':digest(landmarks_path), 'landmarkUids':landmarks,
        'rows':plan_rows, 'sources':source, 'auditKeys':keys, 'audits':audits,
        'native':[{'sheet':s,'cacheKey':k,'resultSha':h,'model':m} for s,k,h,m in outcomes],
        'auditCacheHits':hits, 'auditRecomputed':len(misses), 'captureSeconds':round(time.perf_counter()-start,3),
        'aiCalls':0, 'geometryDownloads':0, 'databaseWrites':0, 'newAcceptanceDecisions':0}


def report(evidence, out):
    if evidence.get('version') != 1 or evidence.get('policy') != POLICY:
        raise ValueError('Unsupported pilot evidence')
    started = time.perf_counter()
    outcomes = defaultdict(list)
    for o in evidence['native']:
        for uid in {v['uid'] for v in o['model'].get('matching',{}).get('viewerMatches',[])}:
            outcomes[uid].append(o)
    landmarks = set(evidence['landmarkUids'])
    results = {}
    for uid,row in evidence['rows'].items():
        b = evidence['sources'][uid]['building']
        a = evidence['audits'][evidence['auditKeys'][uid]['cacheKey']]
        n = native_metrics(b, outcomes[uid])
        verdict, reasons = classify(row,b,a,n,uid in landmarks)
        results[uid] = {'uid':uid,'name':b.get('name',''),'tile':evidence['sources'][uid]['tile'],
            'inputHash':row['inputHash'],'geometry':row['geometry'],'priorState':row['state'],
            'recommendation':verdict,'reasons':reasons,'auditFlags':a['flags'],
            'heightMetres':b['height'],'areaM2':a['areaM2'],'kind':b.get('kind'),
            'structureType':b.get('structureType'),'heightSource':b.get('heightSource'), 'native':n}
    sample = [results[uid] for uid in evidence['sampleUids']]
    counts = dict(Counter(r['recommendation'] for r in sample))
    sensitivity = {}
    for limit in (64,128,256):
        sensitivity[str(limit)] = sum(classify(evidence['rows'][uid], evidence['sources'][uid]['building'],
            evidence['audits'][evidence['auditKeys'][uid]['cacheKey']],results[uid]['native'],uid in landmarks,limit)[0]
            == 'likely-skip' for uid in evidence['sampleUids'])
    summary = {k:evidence[k] for k in ['policy','seed','capturedAt','population','nativeRun','sourceCommit',
        'captureSeconds','auditCacheHits','auditRecomputed','aiCalls','geometryDownloads','databaseWrites','newAcceptanceDecisions']}
    summary.update(sampleSize=len(sample), sampleTiles=len({r['tile'] for r in sample}),
        counts=counts, percentages={k:round(v/len(sample)*100,2) for k,v in counts.items()},
        reasonCounts=dict(Counter(reason for r in sample for reason in r['reasons'])),
        currentGeometry=dict(Counter(r['geometry'] for r in sample)),
        nativeSourceMatchedForms=sum(r['native']['matches']>0 for r in sample),
        sensitivityLikelySkipsByTriangleCeiling=sensitivity,
        controlCases=[results[uid] for uid in evidence['controlUids']],
        classificationSeconds=round(time.perf_counter()-started,4),
        qualification='Likely-skip and enhancement-candidate are uncalibrated review priorities, not public acceptance or modelling jobs. Cached source-envelope matches do not prove architectural similarity. No new good-to-go decisions written.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (out/'sample.csv').open('w',newline='') as stream:
        fields=['uid','name','tile','geometry','priorState','recommendation','reasons','auditFlags',
                'kind','structureType','heightMetres','heightSource','areaM2','inputHash']
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        writer.writerows({**r,'reasons':';'.join(r['reasons']),'auditFlags':';'.join(r['auditFlags'])} for r in sample)
    (out/'kai-tak-stadium.json').write_text(json.dumps(summary['controlCases'],indent=2)+'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',action='store_true')
    parser.add_argument('--evidence',type=Path,default=ROOT/'docs/astra-city/enhancement-screening/pilot-1000/evidence.json.gz')
    parser.add_argument('--out',type=Path,default=ROOT/'docs/astra-city/enhancement-screening/pilot-1000')
    parser.add_argument('--count',type=int,default=1000)
    parser.add_argument('--seed',default=SEED)
    args=parser.parse_args()
    if args.capture:
        data=capture(HERE/'local/pilot',args.count,args.seed)
        args.evidence.parent.mkdir(parents=True,exist_ok=True)
        args.evidence.write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    else:
        data=json.loads(gzip.decompress(args.evidence.read_bytes()))
    result=report(data,args.out)
    print(json.dumps({k:v for k,v in result.items() if k not in ['controlCases','reasonCounts']},indent=2))


if __name__=='__main__':
    main()
