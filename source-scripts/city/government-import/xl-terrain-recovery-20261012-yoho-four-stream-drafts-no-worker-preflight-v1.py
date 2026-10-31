"""Offline AST/schema/hash checks only; no caller import, decode, DB or lease."""
from pathlib import Path
import ast,gzip,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'source-scripts/city/government-import'
BASE=ROOT/'docs/astra-city/government-import'
METHOD=BASE/'government-xl-yoho-eight-four-stream-finite-edge-method-draft-20261012'
PROBE=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
PYTHON=[HERE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-attributes-v1.py',HERE/'xl-terrain-recovery-20261012-yoho-eight-pair-four-stream-finite-edge-interfaces-v1.py']
JS=HERE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-actual-render-attributes-v1.mjs'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=sha(p))
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def literals(tree):
 out={}
 for n in tree.body:
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
   try:out[n.targets[0].id]=ast.literal_eval(n.value)
   except (ValueError,TypeError):pass
 return out

def main():
 pins={};trees=[]
 def add(pin):
  p=ROOT/pin['path'];assert p.is_file() and sha(p)==pin['sha256'],pin
  assert pin['path'] not in pins or pins[pin['path']]==pin
  pins[pin['path']]=pin
 for p in PYTHON:
  tree=ast.parse(p.read_text());trees.append(tree);c=literals(tree)
  assert c['CURRENT']==CURRENT and c['UIDS']==['landsd/146396:0','landsd/231756:0'] and c['COUNTS']==[14792,7731]
  assert c['PROBE_JOB']=='6da18fbe3cb5a91c8fa1b24e5f9f6b8ed378eb09607299e0b8aeca4ec3691a1e'
  assert c['PROBE_SHA']=='778c6658ea3eced67f90fdbc5d02bcef631def48d509e57e896e1bcddc99dd06'
  for rootname in [c['BATCH']]:
   assert not (BASE/rootname).exists() and not (HERE/'local'/rootname).exists()
  add(ref(p))
 add(ref(JS));add(ref(METHOD/'METHOD.md'));add(ref(Path(__file__)))
 subprocess.run(['node','--check',str(JS)],cwd=ROOT,check=True)
 r=read(PROBE/'result.json');assert r['jobId']=='6da18fbe3cb5a91c8fa1b24e5f9f6b8ed378eb09607299e0b8aeca4ec3691a1e'
 assert sha(PROBE/'result.json')=='778c6658ea3eced67f90fdbc5d02bcef631def48d509e57e896e1bcddc99dd06' and r['newlyInstalled']==0 and r['currentAcceptance'] is False
 add(ref(PROBE/'result.json'))
 for pin in r['evidenceRefs']:add(pin)
 rows=read(PROBE/'selection.json.gz')['rows'];rt=read(HERE/'local'/PROBE.name/'runtime-geometry.json.gz')['rows']
 assert [a['uid'] for a in rows]==[a['uid'] for a in rt]==literals(trees[0])['UIDS']
 for row,raw,count,source in zip(rows,rt,[14792,7731],literals(trees[0])['SOURCES']):
  assert row['sourceSHA256']==raw['sourceSHA256']==source
  assert row['candidate']['entry']['triangles']==count and len(raw['index'])==count*3
  assert len(raw['position'])%3==0 and len(raw['drawnGroundGeometry'])%9==0 and raw['drawnGroundGeometry']
  assert row['completeOriginalPOSITIONProof']['sourceSHA256']==source and row['completeOriginalPOSITIONProof']['completeOriginalTriangles']==count
  assert 'originalWholeSourceBounds' in row['completeOriginalPOSITIONProof']
  add(ref(ROOT/row['candidate']['path']))
 closure=read(PROBE/'production-module-closure.json')
 assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1' and closure['computedImportsRejected'] and closure['unsupportedDynamicImports']==0
 assert set(closure['resources'])=={'3d-viewer/vendor/draco_decoder.js','3d-viewer/vendor/draco_decoder.wasm','3d-viewer/vendor/draco_wasm_wrapper.js'}
 for path,h in closure['inputHashes'].items():add(dict(path=path,sha256=h))
 # Every numerical helper and local Python dependency is pinned without importing.
 queue=PYTHON+[HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']+[HERE/n for n in literals(trees[1])['HELPERS']];visited=set()
 while queue:
  p=queue.pop().resolve()
  if p in visited:continue
  visited.add(p);add(ref(p));tree=ast.parse(p.read_text())
  for node in ast.walk(tree):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else [x.name for x in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    for parent in [HERE,HERE.parent/'shared-modelling']:
     q=parent/(name.replace('.','/')+'.py')
     if q.is_file():queue.append(q)
 for n in ['exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','dependency-closure-vendor/acorn-8.8.1/acorn.mjs','actual_float32_model_matrix_bounds_20261011.mjs']:
  p=HERE/n;add(ref(p));assert sha(p) in JS.read_text()
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 native={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;add(ref(p))
  for e in read(p)['models']:assert e['uid'] not in native;native[e['uid']]=e
 assert len(native)==6649
 for row in rows:
  e=row['candidate']['entry'];assert e['uid'] not in native and not any(x.get('sha256')==e['sha256'] or x.get('modelId')==e['modelId'] for x in native.values())
 expected=set(literals(trees[0])['UIDS']+literals(trees[0])['RELATED']);forms={}
 for t in manifest['tiles']:
  p=ROOT/'3d-viewer'/t['url']
  for b in read(p)['buildings']:
   if b['uid'] in expected:assert b['uid'] not in forms;forms[b['uid']]=b;add(ref(p))
 assert set(forms)==expected
 for row in rows:assert row['source']['building']==forms[row['uid']]
 out=dict(passed=True,noWorkerDatabaseOrLease=True,callerImportsPerformed=False,sourceDecoderPerformed=False,numericalGeometryPerformed=False,productionLoaderPerformed=False,javascriptSyntaxOnly=True,exactFrozenCaptureRefsChecked=len(r['evidenceRefs']),currentManifestSHA256=CURRENT,currentNativeCount=6649,completeOriginalFaces=22523,rawCurrentForms=list(sorted(forms)),draftCodePins={str(p.relative_to(ROOT)):sha(p) for p in [*PYTHON,JS]},method=ref(METHOD/'METHOD.md'),validationScript=ref(Path(__file__)),sourceAndCurrentInputPins=list(sorted(pins.values(),key=lambda x:x['path'])),futureAttributesReceiptMustBeCompletedAndAllRefsVerifiedBeforeFinite=True,currentAcceptance=False)
 p=METHOD/'no-worker-schema-hash-preflight.json';assert not p.exists();p.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='sourceAndCurrentInputPins'}));print('preflightSHA256',sha(p))

if __name__=='__main__':main()
