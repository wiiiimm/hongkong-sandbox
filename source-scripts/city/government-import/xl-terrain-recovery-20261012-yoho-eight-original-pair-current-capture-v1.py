"""UNEXECUTED: original Yoho8/exact-podium fresh literal current capture only."""
from pathlib import Path
import ast,copy,importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
METHOD=BASE/'government-xl-yoho-eight-original-pair-current-capture-method-draft-20261012/METHOD.md'
PREFLIGHT=METHOD.parent/'offline-schema-hash-preflight.json'
TINPUT=BASE/'government-xl-yoho-eight-bound-current-provider-source-20261009/selection.json.gz'
PINPUT=BASE/'government-xl-five-more-original-supports-20261007/selection.json.gz'
UIDS=['landsd/146396:0','landsd/231756:0']
RELATED=['landsd/121143:0','landsd/55568:0','landsd/4757:0']
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
EXPECTED={UIDS[0]:dict(source='fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08',model='B217913364901063C0',csuid='2179133649T20050430',objectId=146396,faces=14792),
 UIDS[1]:dict(source='d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167',model='B218783363602062G0',csuid='2187833636P20050609',objectId=231756,faces=7731)}
HISTORY=[('government-xl-yoho-eight-current-bound-identity-promotion-20261009','11898a6fc1cc61ea594d4637773d9c056ed702c1cca2f61886e32caf996578f4'),
 ('government-xl-five-more-original-supports-20261007','5368d4f2dc68d7c1726ae66d56f57d27a6ebe0cd59f21ccc6af45911c1a73e43'),
 ('government-xl-yoho-eight-actual-current-podium-support-20261009','5fa261c5edce87eb462af134750e11b0d10463d25c3d96f096fe3e2f7bdce5d6'),
 ('government-xl-yoho-eight-complete-original-component-graph-20261009','47ef340cbffe46f4c4012a0e21a9d06d8fd53a27191a0d7f81ef2c6687021f43'),
 ('government-xl-yoho-original-podium-strict-anchor-paths-20261010','bf27ea6073b06103b6ecdb30a6816eb7504a86f046666eda6c439a3a1986a2e2'),
 ('government-xl-yoho-original-podium-current-ground-20261010','ed5b355100e2e3d7231deb8657e76642cc2541c7df422b492fa679d39f2f4f1e'),
 ('government-xl-yoho-original-pair-source-tin-context-20261010','631991793b8923c29e640029aa4fa8b2aaa00aff7659e3775ac172bb858002cf')]
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
ENTRY=HERE/'acceptance-metrics-multi-retained.mjs'
CLOSURE_HELPER=HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs'
ACORN=HERE/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs'
CLOSURE_TOOL_SHA256={'source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs': 'c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579', 'source-scripts/city/government-import/dependency-closure-vendor/acorn-8.8.1/acorn.mjs': 'a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55'}

def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert p.is_file() and ref(p)==pin,pin
 return p
def source_rows():
 return [copy.deepcopy(next(r for r in read(path)['rows'] if r['uid']==uid)) for path,uid in [(TINPUT,UIDS[0]),(PINPUT,UIDS[1])]]
def python_closure():
 queue=[Path(__file__),FREEZER,HERE/'exact_packed_world_bounds_v3_20261010.py'];out={}
 while queue:
  p=queue.pop().resolve()
  if str(p) in out:continue
  out[str(p)]=ref(p)
  for node in ast.walk(ast.parse(p.read_text())):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else [x.name for x in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    for root in [HERE,HERE.parent/'shared-modelling']:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():queue.append(q)
 return sorted(out.values(),key=lambda p:p['path'])

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists()
 pre=read(PREFLIGHT);assert pre['passed'] is True and pre['caller']==ref(Path(__file__)) and pre['noWorkerDatabaseOrLease'] is True
 refs=python_closure()+[ref(METHOD),ref(PREFLIGHT),ref(TINPUT),ref(PINPUT)]
 for pin in pre['sourceAndCurrentInputPins']:check(pin);refs.append(pin)
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 historical=[]
 for folder,job in HISTORY:
  path=BASE/folder/'result.json';result=read(path);assert result['jobId']==job and result['newlyInstalled']==0
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',result)
  refs.append(ref(path));historical.append(dict(resultRef=ref(path),jobId=job,
   historicalContextOnly=True,oldNumericalInputsReplayed=False,noCurrentAcceptanceTransfer=True));pulse()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT
 current=read(manifest);forms={};tile_refs=[]
 for tile in current['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];data=read(p)
  nominated=[b for b in data['buildings'] if b['uid'] in UIDS+RELATED]
  if nominated:tile_refs.append(ref(p))
  for b in nominated:
   assert b['uid'] not in forms
   forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes()))
  pulse()
 assert set(forms)==set(UIDS+RELATED)
 catalogue_refs=[ref(ROOT/'3d-viewer'/url) for url in current['officialModelCatalogues']]
 native={}
 for pin in catalogue_refs:
  for e in read(check(pin))['models']:
   assert e['uid'] not in native;native[e['uid']]=e
 assert len(native)==6649 and RELATED[0] in native
 for uid,x in EXPECTED.items():
  assert uid not in native and not any(e.get('modelId')==x['model'] or e.get('sha256')==x['source'] for e in native.values())
  assert forms[uid]['building']['buildingCSUID']==x['csuid'] and forms[uid]['building']['objectId']==x['objectId']
 refs += [start,*tile_refs,*catalogue_refs,ref(ROOT/'3d-viewer/city/data/terrain.json')]
 refs += [ref(ROOT/'3d-viewer'/p['url']) for p in current['terrainPatches']]
 for pin in refs:check(pin)
 from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'))
 rows=source_rows()
 for row in rows:
  uid=row['uid'];x=EXPECTED[uid];entry=row['candidate']['entry'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
  assert digest(raw)==row['sourceSHA256']==entry['sha256']==x['source']
  assert row['modelId']==entry['modelId']==x['model'] and entry['uid']==uid and entry['triangles']==x['faces']
  assert entry['buildingCSUID']==x['csuid'] and entry['objectId']==x['objectId'] and entry['rootTranslation']==[-834500,0,816500]
  proof=packed_world_bounds(raw);assert proof['completeOriginalTriangles']==x['faces']
  lo,hi=np.asarray(entry['worldBounds'],float);blo,bhi=np.asarray(proof['originalWholeSourceBounds'],float)
  assert np.all(blo[[0,2]]>=lo[[0,2]]-1) and np.all(bhi[[0,2]]<=hi[[0,2]]+1),'Original unused POSITION exceeds declared captured ground region'
  dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  row['candidate']=dict(row['candidate'],path=str(dest.relative_to(ROOT)))
  row['source']=forms[uid];row['completeOriginalPOSITIONProof']=proof
  refs += [ref(asset),ref(dest)];pulse(True)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=CURRENT,sourceGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))
 save(LOCAL/'catalogue.json',dict(models=[r['candidate']['entry'] for r in rows]));save(DOC/'terrain-candidates.json',[])
 save(DOC/'historical-obligations-and-current-forms.json',dict(historicalReceipts=historical,
  originalSourcePair=EXPECTED,rawCurrentForms=forms,installedBlock7RawEntry=native[RELATED[0]],
  sourceGraphLabelsAreHistoricalOnly=True,noNativeReapproval=True,noRootRoleOrForeignExemption=True))
 snapshot=DOC/'production-module-closure.json'
 closure_tools=[ref(CLOSURE_HELPER),ref(ACORN)]
 for pin in closure_tools:assert pin['sha256']==CLOSURE_TOOL_SHA256[pin['path']];check(pin)
 refs += closure_tools
 js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure,verifyModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);const snapshot=snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root);verifyModuleClosure(snapshot,root);writeFileSync(process.argv[1],JSON.stringify(snapshot));"
 subprocess.run(['node','--input-type=module','-e',js,str(snapshot)],cwd=ROOT,check=True)
 closure=read(snapshot)
 assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1' and closure['entryPath']==str(ENTRY.relative_to(ROOT))
 assert closure['completeAuditedLiteralImportClosure'] is True and closure['unsupportedDynamicImports']==0 and closure['computedImportsRejected'] is True and closure['opaqueResourcesAreNotParsedModules'] is True
 assert len(closure['modules'])==len(set(closure['modules'])) and len(closure['resources'])==len(set(closure['resources']))
 assert set(closure['modules']).isdisjoint(closure['resources']) and set(closure['inputHashes'])==set(closure['modules'])|set(closure['resources'])
 expected_resources=[dict(from_='3d-viewer/vendor/DRACOLoader.js',to='3d-viewer/vendor/'+name,responseType=kind,decoderDirectory='3d-viewer/vendor/',opaqueRuntimeResource=True) for name,kind in [('draco_decoder.js','text'),('draco_decoder.wasm','arraybuffer'),('draco_wasm_wrapper.js','text')]]
 expected_edges=[{('from' if k=='from_' else k):v for k,v in e.items()} for e in expected_resources]
 assert sorted(closure['resources'])==sorted(e['to'] for e in expected_edges) and sorted(closure['resourceEdges'],key=lambda e:e['to'])==sorted(expected_edges,key=lambda e:e['to'])
 assert {'3d-viewer/city/model-codecs.js','3d-viewer/vendor/DRACOLoader.js'}<=set(closure['modules'])
 assert all(e['from'] in closure['modules'] and (e.get('builtin') is True or e['to'] in closure['modules']) for e in closure['importEdges'])
 refs += [ref(ROOT/p) for p in closure['inputHashes']]+[ref(snapshot)]
 for p,sha in closure['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha
 for pin in closure_tools:check(pin)
 pulse(True)
 subprocess.run(['node',str(ENTRY),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),
  '--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),
  '--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 metric=read(DOC/'metrics.json');geometry=read(LOCAL/'runtime-geometry.json.gz')
 assert [r['uid'] for r in metric['rows']]==[r['uid'] for r in geometry['rows']]==UIDS and not any(r.get('error') for r in metric['rows'])
 for raw,row in zip(geometry['rows'],rows):
  uid=row['uid'];entry=row['candidate']['entry'];assert raw['sourceSHA256']==EXPECTED[uid]['source'] and len(raw['index'])==EXPECTED[uid]['faces']*3
  position=np.asarray(raw['position'],float).reshape(-1,3);assert np.isfinite(position).all()
  lo,hi=np.asarray(entry['worldBounds']);assert np.all(position[:,[0,2]].min(0)>=lo[[0,2]]-1) and np.all(position[:,[0,2]].max(0)<=hi[[0,2]]+1),'Actual literal positions exceed frozen ground capture region'
  ground=np.asarray(raw['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground) and np.isfinite(ground).all()
 for p,sha in geometry['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha;refs.append(ref(ROOT/p))
 refs += [ref(DOC/name) for name in ['selection.json.gz','terrain-candidates.json','metrics.json','historical-obligations-and-current-forms.json']]
 refs += [ref(LOCAL/'catalogue.json'),ref(LOCAL/'runtime-geometry.json.gz')]
 for p,sha in closure['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha
 for pin in closure_tools:check(pin)
 verify_js="import{readFileSync}from'node:fs';import{verifyModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';verifyModuleClosure(JSON.parse(readFileSync(process.argv[1],'utf8')),new URL('./',import.meta.url));"
 subprocess.run(['node','--input-type=module','-e',verify_js,str(snapshot)],cwd=ROOT,check=True)
 for pin in refs:check(pin)
 assert ref(manifest)==start;pulse(True)
 spec=importlib.util.spec_from_file_location('yoho_pair_current_freezer',FREEZER);freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
 freezer.freeze(BATCH,'yoho-eight-original-pair-readonly-current-capture-v1',[check(p) for p in {(r['path'],r['sha256']):r for r in refs}.values()],
  dict(uids=UIDS,completeOriginalFaces=22523,completeCurrentNativeCount=6649,
   historicalReceiptsAreContextOnly=True,allCurrentForeignFormsRetained=True,noTerrainProposal=True,
   noRoleRootNativeIdentityOrPhysicalAcceptance=True,currentAcceptance=False,newlyInstalled=0,
   sampledMetricsVerbatim=metric['rows'],completeProductionModuleClosure=ref(snapshot)))

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 controlled=UIDS+RELATED[:2]
 claim=reservations.claim('yoho-eight-original-pair-current-'+str(uuid.uuid4()),
  ['building:'+u for u in controlled]+['terrain-patch:'+u for u in controlled]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
