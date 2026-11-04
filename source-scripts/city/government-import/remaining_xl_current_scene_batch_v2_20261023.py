"""Check all remaining mapped XL originals against the exact current viewer scene.

Immediate compute only, with bounded40-source chunks and two processes maximum.
No publication, optimisation, modelling API, automatic skip or permanent rejection.
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'installed', 'selection']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    assert 1 <= args.workers <= 2
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs = [Path(__file__)]
    receipts = {}
    for key, name in [('installed', args.installed), ('selection', args.selection)]:
        receipts[key] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(key, name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == receipts[key][1][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    audit = take('installed', args.installed, 'full-xl-current-count.json')
    original = take('selection', args.selection, 'selection.json.gz')
    assert len(audit['rows']) == audit['counts']['total'] == 521
    pending = [r for r in audit['rows'] if not r['installedVerified']]
    assert len(pending) == audit['counts']['remaining']
    by_uid = {r['uid']:r for r in original['rows'] if r['uid'] is not None}
    excludes = set(args.exclude)
    assert len(excludes) == len(args.exclude) and excludes <= {r['uid'] for r in pending if r['uid'] is not None}
    mapped = [r for r in pending if r['uid'] is not None and r['uid'] not in excludes]
    for row in mapped:
        source = by_uid[row['uid']]
        assert row['sourceKey'] == source['native']['cacheKey'] + '/' + source['modelId']
        assert row['indexedSourceSHA256'] == source['sourceSHA256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifestsha = digest(manifest.read_bytes())
    assert manifestsha == audit['manifestSHA256']
    refs.append(manifest)
    chunks = [[r['uid'] for r in mapped[i:i+40]] for i in range(0, len(mapped), 40)]
    doc.mkdir(parents=True)
    save(doc / 'selection.json', dict(fixedXLTotal=521, installed=audit['counts']['installedVerified'], unfinished=len(pending), selected=len(mapped), excluded=sorted(excludes), unmatchedSourceKeys=[r['sourceKey'] for r in pending if r['uid'] is None], manifestSHA256=manifestsha, chunks=chunks, publication=False))
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'OPENBLAS_NUM_THREADS':'1'}

    def process(pair):
        number, uids = pair
        prefix = args.batch + '-chunk-' + str(number).zfill(2)
        names = {step:prefix+'-'+step for step in ['selection', 'runtime', 'identity']}
        result = dict(chunk=number, uids=uids, completedJobs=[], newlyInstalled=0, installationApproved=False)
        commands = [
            ('selection', 'selected_original_refresh_selection_v1.py', ['--capture', args.selection, *[v for uid in uids for v in ['--uid',uid]]]),
            ('runtime', 'selected_original_current_capture_v3.py', ['--capture', names['selection'], *[v for uid in uids for v in ['--uid',uid]]]),
            ('identity', 'selected_original_identity_v2.py', ['--capture', names['runtime']]),
        ]
        for step, tool, tail in commands:
            logfile = doc / (str(number).zfill(2)+'-'+step+'.log')
            with logfile.open('w') as log:
                proc = subprocess.run([sys.executable,str(HERE/tool),'--batch',names[step],*tail], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            if proc.returncode:
                result.update(status='script-adapter-investigation', stoppedAt=step, exitCode=proc.returncode, log=str(logfile.relative_to(ROOT)))
                break
            receipt = read(base/names[step]/'result.json')
            result['completedJobs'].append(dict(batch=names[step], jobId=receipt['jobId']))
        else:
            runtime = read(base/names['runtime']/'summary.json')
            metrics = read(base/names['runtime']/'metrics.json')
            identities = read(base/names['identity']/'summary.json')
            by_metric = {r['uid']:r for r in metrics['rows']}
            by_identity = {r['uid']:r for r in identities['rows']}
            by_foundation = {r['uid']:r for r in runtime['rows']}
            source_rows = {r['uid']:r for r in read(base/names['runtime']/'selection.json.gz')['rows']}
            policy = module('current_batch_policy_'+str(number), HERE/'acceptance-policy.py')
            rows=[]
            for uid in uids:
                source,metric,identity,foundation = source_rows[uid],by_metric[uid],by_identity[uid],by_foundation[uid]
                proof = read(base/names['identity']/uid.split('/')[1]/'identity.json')['proof']
                reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=source['sourceSHA256'],identityProof=proof), metric, metrics['profiles']['mobile'])
                whole = foundation['status']=='captured' and foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedTriangles']==0
                ready = not reasons and identity['passed'] and whole
                status = 'ready-for-all-mode-and-browser-checks' if ready else 'runtime-investigation' if metric.get('error') else 'current-scene-investigation'
                rows.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],status=status,rawPolicyReasons=reasons,identityReasons=identity['reasons'],foundation=foundation,installationApproved=False,permanentRejection=False))
            result.update(status='current-scene-checked',rows=rows,counts=dict(Counter(r['status']for r in rows)),batches=names)
        save(doc/('chunk-'+str(number).zfill(2)+'.json'),result)
        print(dict(chunk=number,totalChunks=len(chunks),sources=len(uids),status=result['status'],counts=result.get('counts')),flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results=list(pool.map(process,enumerate(chunks,1)))
    consumed={}
    for result in results:
        for job in result['completedJobs']:
            receipt,pins=authenticate(base/job['batch'])
            assert receipt['jobId']==job['jobId']
            for name,sha in pins.items():
                assert name not in consumed or consumed[name]==sha
                consumed[name]=sha
            refs.append(base/job['batch']/'result.json')
    for name,sha in consumed.items():assert digest((ROOT/name).read_bytes())==sha,name
    assert digest(manifest.read_bytes())==manifestsha
    rows=[r for chunk in results for r in chunk.get('rows',[])]
    summary=dict(uids=[r['uid']for r in mapped],selected=len(mapped),completedSources=len(rows),chunks=results,counts=dict(Counter(r['status']for r in rows)),newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,activeWorkers=0,qualification='Fresh V3 production captures with exact recorded-height bindings, complete literal foundations, strict policy and exact-source identity diagnostics. Readiness is not installation, all-mode approval or skip credit. Failures remain investigations; no source corruption or permanent rejection inferred.')
    save(doc/'summary.json',summary)
    refs.extend([HERE/'selected_original_refresh_selection_v1.py',HERE/'selected_original_current_capture_v3.py',HERE/'selected_original_identity_v2.py',HERE/'acceptance-policy.py'])
    module('remaining_current_batch_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'all-remaining-mapped-xl-current-scene-diagnostics',refs,summary)


if __name__=='__main__':
    main()
