"""Reconcile interrupted cohort outcomes from exact completed child checkpoints."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','cohort']:
        ap.add_argument('--'+k,required=True)
    ap.add_argument('--replacement',action='append',default=[])
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not doc.exists()
    refs=[Path(__file__),HERE/'acceptance-policy.py'];cache={}
    def receipt(name):
        if name not in cache:
            cache[name]=authenticate(base/name);refs.append(base/name/'result.json')
        return cache[name][0]
    def take(name,filename):
        receipt(name);p=base/name/filename
        assert digest(p.read_bytes())==cache[name][1][str(p.relative_to(ROOT))]
        refs.append(p);return read(p)
    selected=take(a.capture,'selection.json.gz');expected={r['uid']:r for r in selected['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    replacements=dict(x.split(',',1)for x in a.replacement);assert set(replacements)<=set(expected)
    rows=[];policy=module('cohort_reconcile_policy',HERE/'acceptance-policy.py')
    for uid,source in expected.items():
        if uid in replacements:
            original=take(replacements[uid],'summary.json');assert original['uids']==[uid]
            names={**original['batches'],'terrain':original['patch']}
        else:
            p=base/a.cohort/(uid.split('/')[1].replace(':','-')+'.json')
            original=read(p);assert original['uid']==uid;refs.append(p);names=original['batches']
        steps={k:receipt(n)for k,n in names.items()if(base/n/'result.json').exists()}
        result=dict(uid=uid,sourceSHA256=source['sourceSHA256'],batches=names,completedStepJobs={k:r['jobId']for k,r in steps.items()},installationApproved=False,permanentRejection=False)
        terrain=steps.get('terrain')
        if terrain is None:result.update(status='script-investigation',failedPhase='terrain')
        elif terrain['status']!='private-terrain-validator-passed':
            assert terrain['uids']==[uid];result.update(status='terrain-investigation',reason=terrain.get('reason'),errorType=terrain.get('errorType'))
        elif 'runtime'not in steps:result.update(status='script-investigation',failedPhase='runtime')
        else:
            runtime=take(names['runtime'],'summary.json')['rows'];assert len(runtime)==1 and runtime[0]['uid']==uid
            result['foundation']=runtime[0]
            if runtime[0]['status']!='captured':result.update(status='runtime-investigation')
            elif not {'identity','scope'}<=steps.keys():result.update(status='script-investigation',failedPhase='identity-or-scope')
            else:
                actual=take(names['runtime'],'selection.json.gz');assert len(actual['rows'])==1 and actual['rows'][0]['uid']==uid and actual['rows'][0]['sourceSHA256']==source['sourceSHA256'] and actual['rows'][0]['source']['building']==source['source']['building']and actual['manifestSHA256']==selected['manifestSHA256']
                identity=take(names['identity'],uid.split('/')[1]+'/identity.json');assert identity['uid']==uid and identity['sourceSHA256']==source['sourceSHA256']
                scope=take(names['scope'],'scope.json');result['identityReasons']=identity['reasons']
                if scope['positiveAreaTerrainOverlaps']:result.update(status='overlapping-terrain-investigation',terrainContacts=scope['terrainContacts'])
                elif 'forms'not in steps:result.update(status='script-investigation',failedPhase='forms')
                else:
                    metrics=take(names['runtime'],'metrics.json');metric=next(r for r in metrics['rows']if r['uid']==uid);assert metric['sourceSHA256']==source['sourceSHA256']
                    forms=take(names['forms'],'summary.json')
                    reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=source['sourceSHA256'],identityProof=identity['proof']),metric,metrics['profiles']['mobile'])
                    complete=runtime[0]['completeTerrainTriangles']==runtime[0]['triangles']and runtime[0]['fullyBuriedTriangles']==0
                    ready=not reasons and identity['passed']and complete and not forms['flagged']and not scope['touchingNativeUids']
                    result.update(status='ready-for-source-browser-acceptance'if ready else'current-placement-investigation',rawPolicyReasons=reasons,flaggedForms=forms['flagged'],touchingNativeUids=scope['touchingNativeUids'])
        rows.append(result)
    assert len(rows)==len(expected)and digest(manifest.read_bytes())==selected['manifestSHA256']
    from collections import Counter
    summary=dict(uids=sorted(expected),rows=rows,counts=dict(Counter(r['status']for r in rows)),completedSources=len(rows),originalCohort=a.cohort,replacementContinuations=replacements,newlyInstalled=0,installationApproved=False,qualification='Interrupted controller reconciled from exact Neon-authenticated completed source steps. Existing geometry work not replayed. Readiness is not all-mode, browser, source interpretation or installation approval; holds remain unfinished.')
    save(doc/'summary.json',summary)
    module('cohort_reconcile_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'reconciled-original-current-candidate-cohort',refs,summary)


if __name__=='__main__':main()
