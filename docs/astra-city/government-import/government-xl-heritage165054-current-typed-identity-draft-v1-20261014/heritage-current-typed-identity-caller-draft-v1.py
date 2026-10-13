"""ROOT-only unmocked current identity account, exact saved source reused."""
import argparse,gzip,hashlib,importlib.util,json,sys,time
from functools import lru_cache
from pathlib import Path
PACKET=Path(__file__).resolve().parent;ROOT=PACKET.parents[3];HERE=ROOT/'source-scripts/city/government-import'
CONTRACT=PACKET/'input-contract.json';OUTPUT=PACKET/'current-identity-output-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,v):
 b=json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
def fence(c,ch):
 assert sha(CONTRACT)==ch and sha(Path(__file__))==c['callerSHA256']
 for p,h in c['filePins'].items():assert sha(ROOT/p)==h,p
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==c['currentManifestSHA256']

def imported_local_code_fence(c):
 actual={}
 for module in list(sys.modules.values()):
  path=getattr(module,'__file__',None)
  if path is None:continue
  path=Path(path).resolve()
  if not path.is_relative_to(ROOT)or path.suffix!='.py':continue
  if not(path.is_relative_to(ROOT/'source-scripts')or path in [Path(__file__).resolve(),PACKET/'heritage_current_typed_identity_draft_v1.py',PACKET/'test_heritage_current_typed_identity_draft_v1.py']):continue
  key=str(path.relative_to(ROOT));assert key in c['filePins']and sha(path)==c['filePins'][key],key
  actual[key]=sha(path)
 return actual

def calculation_inputs():
 """Unmocked current geometry/whole-cell proof. ROOT tests/normal only; no DB."""
 import numpy as np
 sys.path[:0]=[str(PACKET),str(HERE)]
 from government_georef_cell_identity import verify
 from exact_original_georef_cell_identity_20261009 import apply_exact_cell
 c=read(CONTRACT);fence(c,sha(CONTRACT));row=read(ROOT/c['sourceRowPath'])
 scope=read(ROOT/c['sourceContextPath']);array=read(ROOT/c['completeArrayPath']);meaning=read(ROOT/c['interpretationPath'])
 tri=np.asarray(array['completeOrderedOriginalTriangles'],dtype='<f8')
 assert tri.shape==(15140,3,3)and hashlib.sha256(tri.tobytes()).hexdigest()==c['wholeOriginalWorldSHA256']
 assert array['sourceSHA256']==scope['sourceSHA256']==row['sourceSHA256']==c['sourceSHA256']
 raw=(ROOT/row['candidate']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==c['sourceSHA256']
 spec=importlib.util.spec_from_file_location('heritage_fresh_complete_current_forms',HERE/'xl-final-script-pass.py')
 final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
 lo,hi=row['native']['model']['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 own=[(b,p,t)for b,p,t in forms if b['uid']==row['uid']];assert len(own)==1
 assert own[0][0]==row['source']['building']and own[0][2]==row['source']['tile']
 # All newly nominated tiles must already be byte-pinned, never silently added.
 for b,_,tile in forms:assert 'building:'+b['uid']in c['canonicalResources']and '3d-viewer/'+tile in c['filePins'] and sha(ROOT/'3d-viewer'/tile)==c['filePins']['3d-viewer/'+tile]
 closure=imported_local_code_fence(c)
 identity=final.identity_context(row,tri,forms)
 context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':identity,
  'neighbourTileHashes':{t:sha(ROOT/'3d-viewer'/t)for _,_,t in forms},'actualImportedLocalCodeHashes':closure}
 previous=verify(raw,row,context,tri,current_identity=identity)
 binding={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'decodedWorldTrianglesSHA256':c['wholeOriginalWorldSHA256']}
 previous=apply_exact_cell(previous,tri,expected_binding=binding,current_binding=binding)
 fence(c,sha(CONTRACT));assert imported_local_code_fence(c)==closure
 return {'previous':previous,'row':row,'world':tri,'forms':[b for b,_,_ in forms],
  'source_context':scope,'interpretation':meaning,'expected_context_hash':c['sourceContextSemanticSHA256'],
  'expected_interpretation_hash':c['interpretationSemanticSHA256']},context

@lru_cache(maxsize=1)
def actual_test_fixture():return calculation_inputs()[0]

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--preflight-only',action='store_true');g.add_argument('--replay-current-typed-identity-only',action='store_true')
 p.add_argument('--lease-file',type=Path);p.add_argument('--test-validation',type=Path);p.add_argument('--test-validation-sha256')
 args=p.parse_args();c=read(CONTRACT);ch=sha(CONTRACT);fence(c,ch)
 assert not OUTPUT.exists();scope=read(ROOT/c['sourceContextPath']);meaning=read(ROOT/c['interpretationPath'])
 sys.path.insert(0,str(PACKET));from heritage_current_typed_identity_draft_v1 import validate_scope,compose
 far,ordinary=validate_scope(scope,meaning,expected_context_hash=c['sourceContextSemanticSHA256'],expected_interpretation_hash=c['interpretationSemanticSHA256'])
 if args.preflight_only:
  assert args.lease_file is None;fence(c,ch)
  print(json.dumps({'passed':True,'completeSourceFaces':15140,'typedExtentFaces':len(far),'ordinaryExtentFaces':len(ordinary),'associatedIdentityActor':'landsd/104467:0','independentStarMartRetained':True,'noSourceDecodeOrGeometryCalculation':True,'noDBOrLease':True,'resources':c['canonicalResources']}));return
 assert args.test_validation is not None and sha(args.test_validation)==args.test_validation_sha256
 validation=read(args.test_validation);assert validation['testCount']==16 and validation['exitCode']==0 and validation['allPassed']is True
 assert validation['testedCodePins']==c['testedCodePins'] and validation['inputContractSHA256']==ch
 assert sha(ROOT/validation['testLog']['path'])==validation['testLog']['sha256']
 validation_sha=sha(args.test_validation)
 sys.path.insert(0,str(HERE));from run import reservations,connect,NATIVE_RUN
 lease=read(args.lease_file);assert lease['resources']==c['canonicalResources']and reservations.owns(lease)
 def neon_fence():
  row=read(ROOT/c['sourceRowPath'])
  with connect()as connection:
   connection.execute('SET TRANSACTION READ ONLY')
   for path in c['priorCompleteReceipts']:
    r=read(ROOT/path);assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   assert connection.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchall()==[(row['native']['resultSha'],)]
 assert reservations.heartbeat(lease,ttl=3600)['ok'];neon_fence();OUTPUT.mkdir()
 try:
  manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries=[m for path in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/path)['models']]
  assert len(entries)==len({m['uid']for m in entries})==6650 and not any(m['uid']=='landsd/165054:0'for m in entries)
  inputs,context=calculation_inputs();save(OUTPUT/'raw-current-identity.json',inputs['previous']);save(OUTPUT/'current-context.json',context)
  result=compose(**inputs);assert reservations.heartbeat(lease,ttl=3600)['ok']
  fence(c,ch);neon_fence();assert reservations.owns(lease)
  assert sha(args.test_validation)==validation_sha and sha(ROOT/validation['testLog']['path'])==validation['testLog']['sha256']
  save(OUTPUT/'typed-current-identity.json',result)
  save(OUTPUT/'result.json',{'uids':['landsd/165054:0'],'complete':True,'identityAccepted':result['passed'],
   'rawReasonsRetained':result['rawReasonsRetained'],'remainingIdentityReasons':result['reasons'],
   'completeOriginalFaces':15140,'typedExtentFaces':462,'ordinaryExtentFaces':14678,'associatedIdentityActor':'landsd/104467:0',
   'identitySHA256':sha(OUTPUT/'typed-current-identity.json'),'allInputHashes':c['filePins'],'physicalAccepted':False,'currentAcceptance':False,'installationApproved':False,'newlyInstalled':0})
  print(json.dumps(read(OUTPUT/'result.json')),flush=True)
 except BaseException as error:
  save(OUTPUT/'failure.json',{'complete':False,'errorType':type(error).__name__,'error':str(error),'sourceCorruptionInferred':False,'physicalAccepted':False});raise
 # ROOT supervisor releases only after child/group exit; caller never releases.
if __name__=='__main__':main()
