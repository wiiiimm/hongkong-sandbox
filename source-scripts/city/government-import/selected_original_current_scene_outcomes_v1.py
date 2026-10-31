"""Summarise completed current-scene/identity evidence; no installation or skip credit."""
import argparse
from collections import Counter
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','identity']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists()
    refs=[Path(__file__)];cache={}
    for name in [a.runtime,a.identity]:
        cache[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
    def take(name,filename):
        path=base/name/filename;assert digest(path.read_bytes())==cache[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,'selection.json.gz');metrics=take(a.runtime,'metrics.json');foundations=take(a.runtime,'summary.json');identities=take(a.identity,'summary.json')
    by_metric={r['uid']:r for r in metrics['rows']};by_foundation={r['uid']:r for r in foundations['rows']};by_identity={r['uid']:r for r in identities['rows']}
    wanted={r['uid']for r in selection['rows']};assert wanted==set(by_metric)==set(by_foundation)==set(by_identity)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    policy=module('scene_outcomes_policy',HERE/'acceptance-policy.py');rows=[]
    for source in selection['rows']:
        uid=source['uid'];metric=by_metric[uid];foundation=by_foundation[uid];identity=by_identity[uid]
        proof=take(a.identity,uid.split('/')[1]+'/identity.json')
        assert proof['uid']==uid and proof['sourceSHA256']==source['sourceSHA256']==identity['sourceSHA256']
        assert proof['passed']==identity['passed'] and proof['reasons']==identity['reasons']
        if not metric.get('error'):assert metric['sourceSHA256']==source['sourceSHA256']
        reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=source['sourceSHA256'],identityProof=proof['proof']),metric,metrics['profiles']['mobile'])
        whole=foundation['status']=='captured' and foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedTriangles']==0
        ready=not reasons and identity['passed'] and whole
        status='ready-for-all-mode-and-browser-checks' if ready else 'runtime-investigation' if metric.get('error') else 'current-scene-investigation'
        rows.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],name=source['source']['building'].get('name'),status=status,rawPolicyReasons=reasons,identityReasons=identity['reasons'],foundation=foundation,installationApproved=False,permanentRejection=False))
    summary=dict(uids=sorted(wanted),rows=rows,counts=dict(Counter(r['status']for r in rows)),runtimeBatch=a.runtime,identityBatch=a.identity,currentManifestSHA256=selection['manifestSHA256'],newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Literal whole-source foundation, strict contact/runtime policy and exact original identity diagnostics only. Ready candidates still require all-mode, source/collision/neighbour/browser and guarded installation checks. No skip or permanent-rejection credit.')
    save(doc/'summary.json',summary);refs.append(HERE/'acceptance-policy.py')
    module('scene_outcomes_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'selected-current-scene-diagnostic-outcomes',refs,summary)
    print(dict(sources=len(rows),counts=summary['counts']),flush=True)


if __name__=='__main__':main()
