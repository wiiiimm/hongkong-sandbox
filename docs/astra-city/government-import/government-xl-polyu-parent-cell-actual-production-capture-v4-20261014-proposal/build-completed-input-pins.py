"""UNEXECUTED ROOT-only pin closure after the actual nominee is verified.

No future placeholder receipt, DB, production import, source decode or proof.
"""
from pathlib import Path
import ast,gzip,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';BASE=ROOT/'docs/astra-city/government-import';PROPOSAL=Path(__file__).resolve().parent
NOM=BASE/'government-xl-polyu-saved-parent-cell-repacking-v1-20261014'
CAP=BASE/'government-xl-polyu-five-current-parent-actual-production-capture-v2-20261014'
FAILED=BASE/'government-xl-polyu-parent-cell-actual-production-capture-v3-20261014'
CALLER=HERE/'polyu_parent_cell_actual_production_capture_v4_draft_20261014.py'
RUNTIME=HERE/'polyu_parent_cell_actual_production_runtime_v4_draft_20261014.mjs'
HELPER=HERE/'polyu_saved_parent_cell_capture_binding_v3_draft_20261014.py'
TEST=HERE/'test_polyu_saved_parent_cell_capture_binding_v3_draft_20261014.py'
def read(p):
    with (gzip.open(p,'rt')if str(p).endswith('.gz')else p.open())as f:return json.load(f)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    assert not (PROPOSAL/'draft-pins.json').exists()
    receipt=read(NOM/'result.json');verified=read(NOM/'ROOT-VERIFIED.json')
    assert verified['jobId']==receipt['jobId']and verified['exactNeonReadback']and verified['allEvidenceHashesVerified']and verified['leaseReleased']
    assert not receipt['physicalAccepted']and not receipt['installationApproved']
    nom=read(NOM/'private-saved-parent-cell-repacked-nomination.json.gz');mesh=nom['newNativeMesh']
    positions=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);index=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)
    assert np.isfinite(positions).all()and index.min()>=0 and index.max()<len(positions)
    raw=positions[index];assert len(raw)==len(nom['candidateFaceProvenance'])
    previous=read(CAP/'result.json');assert previous['jobId']=='8f204d9c83bc0cc6ca45bb56da6da2fb8b70255c5af6c7dd37f346f73aceae9e'
    prior=read(BASE/'government-xl-polyu-saved-parent-cell-repacking-v1-20261014-proposal/draft-pins.json')
    code={q['path']:q for q in prior['codeRefs']};inputs={q['path']:q for q in prior['inputRefs']};pending=[CALLER,HELPER,TEST];seen=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);q=ref(p);code[q['path']]=q
        for n in ast.walk(ast.parse(p.read_text(),filename=str(p))):
            names=([a.name for a in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[])
            for name in names:
                q=HERE/(name.split('.')[0]+'.py')
                if q.is_file():pending.append(q)
    for p in [RUNTIME,HERE/'polyu_compact_runtime_mesh_projection_v1_draft_20261014.py',HERE/'polyu_compact_runtime_mesh_projection_v1_draft_20261014.mjs',HERE/'test_polyu_compact_runtime_mesh_projection_v1_draft_20261014.py',PROPOSAL/'METHOD.md',Path(__file__).resolve(),PROPOSAL/'prepare-readonly-v4.py']:
        q=ref(p);code[q['path']]=q
    for folder in [NOM,CAP,FAILED]:
        for q in read(folder/'result.json')['evidenceRefs']+[ref(folder/'result.json'),ref(folder/'ROOT-VERIFIED.json'),ref(folder/'neon-sync.json')]:
            if q['path']in inputs:assert inputs[q['path']]==q,'Conflicting frozen evidence '+q['path']
            inputs[q['path']]=q
    for path,q in code.items():
        if path in inputs:assert inputs[path]==q;inputs.pop(path)
    current='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==current
    value=dict(caller=ref(CALLER),runtime=ref(RUNTIME),bindingHelper=ref(HELPER),bindingTests=ref(TEST),completedNominationJob=receipt['jobId'],previousCompleteCaptureJob=previous['jobId'],completeNewNativeFacets=len(raw),completeNewPositionVertices=len(positions),completePriorV3PositionVertices=read(CAP/'input.json.gz')['completeNewPositionVertices'],completeNewRawSHA256=hashlib.sha256(raw.tobytes()).hexdigest(),currentManifestSHA256=current,codeRefs=sorted(code.values(),key=lambda q:q['path']),inputRefs=sorted(inputs.values(),key=lambda q:q['path']),noSourceDecodeOrProductionCapture=True)
    with (PROPOSAL/'draft-pins.json').open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(dict(pins=ref(PROPOSAL/'draft-pins.json'),actualFacets=len(raw),actualPositionVertices=len(positions),completedNominationJob=receipt['jobId'])))
if __name__=='__main__':main()
