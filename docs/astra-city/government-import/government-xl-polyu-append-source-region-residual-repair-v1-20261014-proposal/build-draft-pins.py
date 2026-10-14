"""Code/input metadata hashing only; no imports of draft or source math."""
from pathlib import Path
import ast,gzip,hashlib,json
PROPOSAL=Path(__file__).resolve().parent;ROOT=PROPOSAL.parents[3]
HERE=ROOT/'source-scripts/city/government-import';SHARED=HERE.parent/'shared-modelling';BASE=ROOT/'docs/astra-city/government-import'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):
    data=p.read_bytes();return json.loads(gzip.decompress(data)if str(p).endswith('.gz')else data)
def main():
    caller=HERE/'polyu_append_source_region_residual_repair_caller_v1_draft_20261014.py'
    pending=[caller,HERE/'polyu_append_source_region_residual_repair_v1_draft_20261014.py',HERE/'test_polyu_append_source_region_residual_repair_v1_draft_20261014.py',HERE/'test_polyu_append_source_region_canonical_lease_v1_draft_20261014.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'];seen=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);tree=ast.parse(p.read_text(),filename=str(p))
        for n in ast.walk(tree):
            names=([a.name for a in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[])
            for name in names:
                for parent in [HERE,SHARED]:
                    local=parent/(name.split('.')[0]+'.py')
                    if local.is_file():pending.append(local);break
    seen.update([PROPOSAL/'METHOD.md',PROPOSAL/'prepare-readonly.py',Path(__file__)])
    gap=BASE/'government-xl-polyu-saved-rectangle-gap-attribution-v1-20261014';cap=BASE/'government-xl-polyu-parent-cell-actual-production-capture-v4-20261014'
    inputs=[gap/q for q in ['result.json','ROOT-VERIFIED.json','saved-coverage-region-and-guard-attribution.json.gz','saved-validator-missing-vs-outside.json.gz']]
    inputs += [cap/q for q in ['result.json','ROOT-VERIFIED.json','input.json.gz','real-validator-outcome.json','all25-original-production-guard-site-replay.json.gz']]
    nref=read(cap/'input.json.gz')['newNomination'];assert ref(ROOT/nref['path'])==nref;inputs.append(ROOT/nref['path'])
    inputs.append(PROPOSAL/'saved-gap-source-family-summary.json')
    inputs.append(PROPOSAL/'canonical-reservation-group-correction.patch')
    inputs.extend(p for p in (PROPOSAL/'preserved-before-static-serialization-export-correction').iterdir()if p.is_file())
    inputs.extend(p for p in (PROPOSAL/'preserved-before-canonical-reservation-group-correction').iterdir()if p.is_file())
    out=dict(caller=ref(caller),codeRefs=[ref(p)for p in sorted(seen)],inputRefs=[ref(p)for p in sorted(set(inputs))],
        historicalCapturedManifestSHA256='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7',
        noTestsImportSourcePackingOrWorkerExecuted=True,oldReceiptReferencesRemainHistoricalNotLiveAliases=True,
        ROOTFutureCurrentManifestSHA256='2a4c1ee569254ee5b93026e48454241a963feda3b7048856e672dcd0b1c58bcb',currentAcceptance=False)
    with(PROPOSAL/'draft-pins.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(dict(caller=out['caller'],codePins=len(out['codeRefs']),inputPins=len(out['inputRefs']),draftPins=ref(PROPOSAL/'draft-pins.json'))))
if __name__=='__main__':main()
