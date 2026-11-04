"""Static preparation only: hash closed inputs, no source/model imports or DB."""
from pathlib import Path
import ast,json,gzip,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved64-actual-max-reviewed-validator-v1-20261014'
PROPOSAL=BASE/(BATCH+'-proposal');OVERLAP=BASE/'government-xl-polyu-saved-append-overlap-ancestry-v1-20261014'
CAPTURE=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014'
APPEND=BASE/'government-xl-polyu-append-source-region-residual-repair-v1-20261014'
CALLER=HERE/'polyu_saved64_actual_max_validator_caller_v1_draft_20261014.py';RUNTIME=HERE/'polyu_saved64_actual_max_full_ray_runtime_v1_draft_20261014.mjs'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def distinct(qs):
 d={}
 for q in qs:
  if q['path']in d:assert d[q['path']]==q
  d[q['path']]=q
 return [d[p]for p in sorted(d)]
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
 todo=[CALLER,Path(__file__),HERE/'polyu_saved64_actual_max_prepare_v1_draft_20261014.py',HERE/'test_polyu_saved64_site_selection_v1_draft_20261014.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',ROOT/read(CAPTURE/'real-validator-outcome.json')['unchangedValidator']['path']];seen=set()
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def main():
 assert not(PROPOSAL/'draft-pins.json').exists();inputs=[]
 for folder in [OVERLAP,CAPTURE,APPEND]:
  receipt=read(folder/'result.json');inputs+=receipt['evidenceRefs']+[ref(folder/'result.json'),ref(folder/'ROOT-VERIFIED.json')]
 inputs=distinct(inputs)
 for q in inputs:assert ref(ROOT/q['path'])==q,q
 candidate=read(CAPTURE/'private-native-terrain-candidate.json.gz');inp=read(CAPTURE/'input.json.gz');summary=read(OVERLAP/'complete-overlap-summary.json')
 chunkrefs=[q for q in inputs if q['path'].startswith(str((OVERLAP/'complete-pair-chunks').relative_to(ROOT))+'/')]
 assert len(chunkrefs)==1159
 code=[ref(p)for p in code_paths()]+[ref(RUNTIME),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'runtime-reviewed-upton-v6-to-polyu-saved64-v1.patch'),ref(PROPOSAL/'draft-files.json')]
 oldruntime=HERE/'upton_v6_saved64_actual_max_full_ray_runtime_draft_v1_20261013.mjs'
 code +=[ref(oldruntime),ref(HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs'),ref(HERE/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs'),ref(HERE/'exact_incremental_json_gzip_v1_20261012.mjs')]
 value=dict(caller=ref(CALLER),runtime=ref(RUNTIME),codeRefs=distinct(code),inputRefs=inputs,completePairChunkRefs=chunkrefs,
  completeSavedMeasurement=summary['measurement'],completeMeshBinding=inp['completeMeshBinding'],
  candidateCanonicalSHA256=hashlib.sha256((json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest(),
  actualBaseParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),candidateOnly=True,historicalSourceContext=True,currentAcceptance=False)
 (PROPOSAL/'draft-pins.json').write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
 print(json.dumps(dict(pins=ref(PROPOSAL/'draft-pins.json'),codeRefs=len(value['codeRefs']),inputRefs=len(inputs),completeChunks=len(chunkrefs))))
if __name__=='__main__':main()
