"""Rebind actual identical numeric renderer inputs; never transfer acceptance."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','before','after']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name,local=False):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=(HERE/'local'/batch if local else base/batch)/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    captures={};metrics={};geometry={}
    for batch in [a.before,a.after]:
        captures[batch]=take(batch,'selection.json.gz');metrics[batch]=take(batch,'metrics.json');geometry[batch]={r['uid']:r for r in take(batch,'runtime-geometry.json.gz',True)['rows']}
    first,last=captures[a.before],captures[a.after];assert first['manifestSHA256']==last['manifestSHA256'];manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==first['manifestSHA256'];refs.append(manifest)
    old={r['uid']:r for r in first['rows']};new={r['uid']:r for r in last['rows']};assert set(old)==set(new)==set(geometry[a.before])==set(geometry[a.after]);assert metrics[a.before]['profiles']==metrics[a.after]['profiles'];rows=[]
    # All renderer implementation inputs shared between captures must still be
    # the exact same bytes. Different private terrain metadata/files stay bound
    # separately and are never treated as historical surface approval.
    implementation=[]
    for path,sha in metrics[a.before]['inputHashes'].items():
        if path.endswith(('.js','.mjs')):
            assert metrics[a.after]['inputHashes'][path]==sha==digest((ROOT/path).read_bytes());refs.append(ROOT/path);implementation.append(dict(path=path,sha256=sha))
    for uid,r in old.items():
        q=new[uid];assert r['source']==q['source']and r['sourceSHA256']==q['sourceSHA256']and r['candidate']['entry']==q['candidate']['entry']
        for row in [r,q]:
            path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path)
        before,after=geometry[a.before][uid],geometry[a.after][uid];assert before['sourceSHA256']==after['sourceSHA256']==r['sourceSHA256'];fields={}
        for key,dtype in [('position','<f8'),('index','<i8'),('drawnGroundGeometry','<f8')]:
            x,y=np.asarray(before[key],dtype=dtype),np.asarray(after[key],dtype=dtype);assert x.shape==y.shape and np.array_equal(x,y),uid+': current numeric field changed: '+key;fields[key]=dict(shape=list(x.shape),sha256=digest(x.tobytes()))
        oldmetric=next(m for m in metrics[a.before]['rows']if m['uid']==uid);newmetric=next(m for m in metrics[a.after]['rows']if m['uid']==uid);assert oldmetric==newmetric and not newmetric.get('error')
        rows.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],numericInputs=fields,completeMetricsUnchanged=True,sourceRecordAndEntryUnchanged=True))
    result=dict(uids=sorted(new),rows=rows,beforeBatch=a.before,currentBatch=a.after,rendererImplementationInputs=implementation,currentManifestSHA256=last['manifestSHA256'],allActualLiteralSourceAndDrawnGroundInputsIdentical=True,priorNumericRelationsStillApplyToExactCurrentInputs=True,sourceGeometryChanges=0,physicalAccepted=False,historicalApprovalTransferred=False,installationApproved=False,qualification='Actual current and previous complete source position/index/drawn-ground arrays, renderer modules, full source records/catalogue entries and every numeric metric match exactly. This rebinds pure numeric relations only. New private terrain metadata still requires its own surface/native/scope validation and every identity/source-role/device/browser/publication decision remains separate. No historical installation or physical approval is transferred.')
    save(out/'summary.json',result);module('numeric_rebinding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-identical-current-original-renderer-numeric-input-rebinding',refs,result);print(dict(actors=len(rows),allNumericInputsIdentical=True,physicalAccepted=False),flush=True)

if __name__=='__main__':main()
