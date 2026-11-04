"""UNEXECUTED: unchanged Yoho pair full attributes; no import acceptance."""
from pathlib import Path
import ast, importlib.util, json, subprocess, sys, time, uuid
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-yoho-eight-original-pair-current-attributes-v1'
DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'reservation.json'
PROBE=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
PROBE_JOB='6da18fbe3cb5a91c8fa1b24e5f9f6b8ed378eb09607299e0b8aeca4ec3691a1e'
PROBE_SHA='778c6658ea3eced67f90fdbc5d02bcef631def48d509e57e896e1bcddc99dd06'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/146396:0','landsd/231756:0']; COUNTS=[14792,7731]
RELATED=['landsd/121143:0','landsd/55568:0','landsd/4757:0']
SOURCES=['fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08','d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167']
CAPTURE=HERE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-actual-render-attributes-v1.mjs'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
METHOD=BASE/'government-xl-yoho-eight-four-stream-finite-edge-method-draft-20261012/METHOD.md'
PREFLIGHT=METHOD.parent/'no-worker-schema-hash-preflight.json'

def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert p.is_file() and ref(p)==pin,pin
 return p
def python_closure():
 queue=[Path(__file__),FREEZER];out={}
 while queue:
  p=queue.pop().resolve()
  if str(p) in out:continue
  out[str(p)]=ref(p)
  for node in ast.walk(ast.parse(p.read_text())):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else [x.name for x in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    for parent in [HERE,HERE.parent/'shared-modelling']:
     q=parent/(name.replace('.','/')+'.py')
     if q.is_file():queue.append(q)
 return sorted(out.values(),key=lambda p:p['path'])

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists()
 pre=read(PREFLIGHT);assert pre['passed'] and pre['noWorkerDatabaseOrLease'] and pre['draftCodePins'][str(Path(__file__).resolve().relative_to(ROOT))]==ref(Path(__file__))['sha256']
 refs=python_closure()+[ref(METHOD),ref(PREFLIGHT),ref(CAPTURE)]
 for pin in pre['sourceAndCurrentInputPins']:check(pin);refs.append(pin)
 receipt=read(PROBE/'result.json');assert ref(PROBE/'result.json')['sha256']==PROBE_SHA and receipt['jobId']==PROBE_JOB
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PROBE_JOB,)).fetchone()==('complete',receipt)
 refs.extend(receipt['evidenceRefs']);refs.append(ref(PROBE/'result.json'))
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 for pin in refs:check(pin);pulse()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT
 current=read(manifest);cats=[ref(ROOT/'3d-viewer'/url) for url in current['officialModelCatalogues']];native={}
 for pin in cats:
  for e in read(check(pin))['models']:assert e['uid'] not in native;native[e['uid']]=e
 assert len(native)==6649 and RELATED[0] in native
 assert not any(e['uid'] in UIDS or e.get('sha256') in SOURCES for e in native.values())
 rows=read(PROBE/'selection.json.gz')['rows'];rtpath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(rtpath)['rows']
 assert [r['uid'] for r in rows]==[r['uid'] for r in runtime]==UIDS
 assert ref(PROBE/'selection.json.gz') in receipt['evidenceRefs'] and ref(rtpath) in receipt['evidenceRefs']
 forms={}
 for tile in current['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid'] in UIDS+RELATED:assert b['uid'] not in forms;forms[b['uid']]=(b,path)
  pulse()
 assert set(forms)==set(UIDS+RELATED)
 inputs=[]
 for row,rt,uid,sha,count in zip(rows,runtime,UIDS,SOURCES,COUNTS):
  assert row['source']['building']==forms[uid][0] and row['uid']==rt['uid']==uid
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']==rt['sourceSHA256']==sha
  assert row['candidate']['entry']['triangles']==count and len(rt['index'])==count*3
  refs.append(ref(asset));inputs.append(dict(uid=uid,entry=row['candidate']['entry'],building=forms[uid][0],path=str(asset.relative_to(ROOT))))
 refs.extend(cats+[ref(p) for b,p in forms.values()]);refs.extend(ref(HERE/n) for n in ['actual_float32_model_matrix_bounds_20261011.mjs','exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','dependency-closure-vendor/acorn-8.8.1/acorn.mjs'])
 for pin in refs:check(pin)
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes())
 refs.append(ref(DOC/'historical-current-manifest.json'))
 save(DOC/'literal-source-inputs.json.gz',dict(rows=inputs,currentManifest=start,currentCatalogueRefs=cats,evidenceRefs=refs))
 pulse(True)
 subprocess.run(['node',str(CAPTURE),str((DOC/'literal-source-inputs.json.gz').relative_to(ROOT)),str((DOC/'actual-render-attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 actual=read(DOC/'actual-render-attributes.json.gz');assert [r['uid'] for r in actual['rows']]==UIDS
 closure=actual['completeRecursiveProductionModuleClosure'];assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1' and closure['computedImportsRejected'] and closure['unsupportedDynamicImports']==0
 assert closure['opaqueResourcesAreNotParsedModules'] and len(closure['resourceEdges'])==3
 for a,rt,count in zip(actual['rows'],runtime,COUNTS):
  assert a['sourceSHA256']==rt['sourceSHA256'] and a['completeOriginalIndex']==rt['index'] and len(a['completeOriginalIndex'])==count*3
  assert np.array_equal(np.asarray(a['completeLiteralWorldPosition']),np.asarray(rt['position']))
  for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   position=np.asarray(a[key],float).reshape(-1,3);assert len(position)==len(rt['position'])//3 and np.isfinite(position).all()
 for p,sha in actual['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha;refs.append(ref(ROOT/p))
 for pin in refs:check(pin);pulse()
 assert ref(manifest)==start;refs.extend([ref(DOC/'literal-source-inputs.json.gz'),ref(DOC/'actual-render-attributes.json.gz')]);pulse(True)
 spec=importlib.util.spec_from_file_location('yoho_attributes_freezer',FREEZER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'yoho-complete22523-original-literal-two-explicit-float32-attributes-diagnostic-v1',[check(p) for p in {(r['path'],r['sha256']):r for r in refs}.values()],dict(uids=UIDS,completeOriginalFaces=22523,currentManifest=start,allCompletePOSITIONAttributesIncludingUnused=True,allCurrentCatalogueHashesPinned=True,explicitArithmeticOnlyNotUniversalGPUCameraGuarantee=True,noTerrainProposal=True,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0))

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 controlled=UIDS+RELATED[:2]
 claim=reservations.claim('yoho-pair-attributes-'+str(uuid.uuid4()),['building:'+u for u in controlled]+['terrain-patch:'+u for u in controlled]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
