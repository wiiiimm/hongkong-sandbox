"""Static saved metadata/AST/input hashes only; no geometry or imports."""
from pathlib import Path
import ast,gzip,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[3];HERE=ROOT/'source-scripts/city/government-import';SHARED=HERE.parent/'shared-modelling';BASE=ROOT/'docs/astra-city/government-import'
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw)if str(p).endswith('.gz')else raw)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    caller=HERE/'polyu_saved_append_overlap_ancestry_caller_v1_draft_20261014.py';helper=HERE/'polyu_saved_append_overlap_ancestry_v1_draft_20261014.py';test=HERE/'test_polyu_saved_append_overlap_ancestry_v1_draft_20261014.py'
    pending=[caller,helper,test,HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'];seen=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p)
        for n in ast.walk(ast.parse(p.read_text(),filename=str(p))):
            names=([a.name for a in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[])
            for name in names:
                for parent in [HERE,SHARED]:
                    local=parent/(name.split('.')[0]+'.py')
                    if local.is_file():pending.append(local);break
    seen.update([P/'METHOD.md',P/'prepare-readonly.py',Path(__file__),HERE.parent/'island-detail-integration/native_terrain_validation.py'])
    cap=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014';nom=BASE/'government-xl-polyu-append-source-region-residual-repair-v1-20261014'
    inputs=[cap/name for name in ['result.json','ROOT-VERIFIED.json','input.json.gz','actual-production-replay.json.gz','private-native-terrain-candidate.json.gz','real-validator-outcome.json','all25-original-production-guard-site-replay.json.gz']]
    inputs += [nom/name for name in ['result.json','ROOT-VERIFIED.json','private-append-only-source-region-nomination.json.gz']]
    inp=read(cap/'input.json.gz');replay=read(cap/'actual-production-replay.json.gz')
    previous=inp['previousFullNomination'];assert ref(ROOT/previous['path'])==previous;inputs.append(ROOT/previous['path'])
    parent=dict(path='3d-viewer/city/data/terrain.json',sha256=replay['inputHashes']['3d-viewer/city/data/terrain.json']);assert ref(ROOT/parent['path'])==parent;inputs.append(ROOT/parent['path'])
    out=dict(caller=ref(caller),codeRefs=[ref(p)for p in sorted(seen)],inputRefs=[ref(p)for p in sorted(set(inputs))],completeMeshBinding=inp['completeMeshBinding'],
        historicalCapturedManifestSHA256='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7',historicalSavedOnly=True,currentAcceptance=False,
        sourceInputRefsAlreadyROOTVerifiedAtCaptureEpochNotLiveAliased=True,noFixturesImportsSchemaUnionPairsOrWorkerExecuted=True)
    with(P/'draft-pins.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(dict(caller=out['caller'],helper=ref(helper),test=ref(test),method=ref(P/'METHOD.md'),preparation=ref(P/'prepare-readonly.py'),codePins=len(out['codeRefs']),inputPins=len(out['inputRefs']),draftPins=ref(P/'draft-pins.json'))))
if __name__=='__main__':main()
