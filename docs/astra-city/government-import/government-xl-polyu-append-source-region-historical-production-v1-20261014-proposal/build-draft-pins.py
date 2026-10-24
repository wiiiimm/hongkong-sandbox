"""Static AST/input byte hashing only; no draft imports/source calculations."""
from pathlib import Path
import ast,gzip,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[3];HERE=ROOT/'source-scripts/city/government-import';SHARED=HERE.parent/'shared-modelling';BASE=ROOT/'docs/astra-city/government-import'
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    caller=HERE/'polyu_append_source_region_historical_production_caller_v1_draft_20261014.py';runtime=HERE/'polyu_append_source_region_historical_production_runtime_v1_draft_20261014.mjs'
    helper=HERE/'polyu_append_historical_capture_binding_v1_draft_20261014.py';test=HERE/'test_polyu_append_historical_capture_binding_v1_draft_20261014.py'
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
    seen.update([runtime,P/'METHOD.md',P/'prepare-readonly.py',Path(__file__),P/'runtime-v4-to-append-historical-v1.patch'])
    seen.update(HERE/name for name in ['polyu_compact_runtime_mesh_projection_v1_draft_20261014.mjs','exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','exact_incremental_json_gzip_v1_20261012.mjs','upton_six_basic_guard_samples_v1_20261012.mjs','resolve-pass-indexed-parent-clipping.py','check-neighbours.mjs'])
    nom=BASE/'government-xl-polyu-append-source-region-residual-repair-v1-20261014';cap=BASE/'government-xl-polyu-parent-cell-actual-production-capture-v4-20261014';source=BASE/'government-xl-polyu-five-current-parent-actual-production-capture-v2-20261014';upton=BASE/'government-xl-upton-joint-original-functional-installed-v2-20261014'
    inputs=[nom/name for name in ['result.json','ROOT-VERIFIED.json','private-append-only-source-region-nomination.json.gz','complete-preservation-and-counts.json']]
    inputs += [cap/name for name in ['result.json','ROOT-VERIFIED.json','input.json.gz','private-native-terrain-candidate.json.gz','real-validator-outcome.json']]
    inputs += [source/name for name in ['result.json','ROOT-VERIFIED.json','complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']]
    inputs += [upton/name for name in ['result.json','ROOT-VERIFIED.json','historical-input-context.json']]
    inp=read(cap/'input.json.gz');previous=inp['newNomination'];assert ref(ROOT/previous['path'])==previous;inputs.append(ROOT/previous['path'])
    context=read(upton/'historical-input-context.json');rows=[q for q in context['mutableCurrentByteSnapshots']if q['original']['path']=='3d-viewer/city/data/manifest.json'];assert len(rows)==1
    row=rows[0];assert row['original']['sha256']==row['savedHistoricalBytes']['sha256']=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
    archive=row['savedHistoricalBytes'];assert ref(ROOT/archive['path'])==archive;inputs.append(ROOT/archive['path'])
    actors=read(source/'complete-fresh-current-native59527-and24-BASIC.json.gz');resolved=[]
    for path,h in actors['inputHashes'].items():
        q=dict(path=path,sha256=h)
        if path=='3d-viewer/city/data/manifest.json':assert q==row['original'];q=archive
        assert ref(ROOT/q['path'])==q;inputs.append(ROOT/q['path']);resolved.append(q)
    candidate=read(nom/'private-append-only-source-region-nomination.json.gz');new_binding=candidate['newCompleteMeshBinding']
    assert new_binding['completeMeshTupleSHA256']=='504e482f0467f396c5c570a154582da94fe6a1a04e8f52404bd687ad6420816b'and new_binding['completeIndexedRawBinary64LE_SHA256']=='c3c5e4b5ea68aa21fda2d5a2f9ac6fb1477872920e106b9b5e69a8265b75a18b'
    out=dict(caller=ref(caller),runtime=ref(runtime),codeRefs=[ref(p)for p in sorted(seen)],inputRefs=[ref(p)for p in sorted(set(inputs))],completeMeshBinding=new_binding,
        historicalSceneManifestReference=archive,historicalSourceInputRefsResolvedByExactNamedManifestOnly=sorted(resolved,key=lambda q:q['path']),historicalReplay=True,currentAcceptance=False,noTestsImportsSchemaSourceMathOrWorkerExecuted=True)
    with(P/'draft-pins.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(dict(caller=out['caller'],runtime=out['runtime'],codePins=len(out['codeRefs']),inputPins=len(out['inputRefs']),draftPins=ref(P/'draft-pins.json'))))
if __name__=='__main__':main()
