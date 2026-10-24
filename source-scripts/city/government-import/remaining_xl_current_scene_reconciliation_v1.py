"""Reconcile all bulk current-scene diagnostics with completed repaired identity chunks."""
import argparse
from collections import Counter
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','source-batch']:p.add_argument('--'+key,required=True)
    p.add_argument('--replacement',action='append',required=True,help='chunkNumber,outcomesBatch')
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists()
    receipt,pins=authenticate(base/a.source_batch);refs=[Path(__file__),base/a.source_batch/'result.json']
    def original(filename):
        path=base/a.source_batch/filename;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=original('selection.json');summary=original('summary.json')
    expected={uid for chunk in selection['chunks']for uid in chunk};assert len(expected)==selection['selected']
    replacements={}
    for spec in a.replacement:
        number,name=spec.split(',');number=int(number);assert number not in replacements
        r,bound=authenticate(base/name);path=base/name/'summary.json';assert digest(path.read_bytes())==bound[str(path.relative_to(ROOT))]
        refs.extend([base/name/'result.json',path]);replacements[number]=read(path)
    rows=[]
    for chunk in summary['chunks']:
        number=chunk['chunk']
        if number in replacements:
            fixed=replacements[number];assert set(fixed['uids'])==set(chunk['uids']) and fixed['currentManifestSHA256']==selection['manifestSHA256'];rows.extend(fixed['rows'])
        else:
            assert chunk['status']=='current-scene-checked';rows.extend(chunk['rows'])
    assert len(rows)==len(expected) and {r['uid']for r in rows}==expected
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=sorted(expected),rows=rows,counts=dict(Counter(r['status']for r in rows)),rawPolicyReasonCounts=dict(Counter(reason for r in rows for reason in r['rawPolicyReasons'])),identityReasonCounts=dict(Counter(reason for r in rows for reason in r['identityReasons'])),fixedXLTotal=521,fixedXLInstalledAtCheck=selection['installed'],unfinishedAtCheck=selection['unfinished'],mappedSourcesChecked=len(rows),separateInProgressSources=selection['excluded'],unmatchedSourceKeys=selection['unmatchedSourceKeys'],currentManifestSHA256=selection['manifestSHA256'],allSelectedSourcesReconciled=True,newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,activeWorkers=0,qualification='All selected sources have exact current-scene diagnostics. Earlier invalid-cell adapter crashes are superseded by failure-preserving complete identity results, not repeated acquisition. No source declared corrupt/uninstallable or granted installation/skip credit; contact, boundary, terrain or source-routing failures remain actionable investigations.')
    save(doc/'summary.json',result)
    module('remaining_scene_reconcile_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'all-selected-xl-current-scene-reconciled',refs,result)
    print(dict(sources=len(rows),counts=result['counts'],policyReasons=result['rawPolicyReasonCounts']),flush=True)


if __name__=='__main__':main()
