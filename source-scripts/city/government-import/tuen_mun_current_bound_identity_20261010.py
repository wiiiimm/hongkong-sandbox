"""Replay current/source/owner provenance before named hospital identity.

Identity only. Both native members, every packed stream, exact primary query,
all nearby forms/tiles and the full raw geographic cell remain mandatory.
"""
import gzip,importlib.util,json
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from yoho_eight_current_bound_identity_20261009 import stream_pin
from routed_original_cell_identity import verify_files as raw_verify
from tuen_mun_named_original_hospital_identity_20261010 import verify,SPEC,OWNER,UID,RELATED
DOC=ROOT/'docs/astra-city/government-import/government-xl-tuen-mun-bound-current-owner-source-20261010'
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
WHERE="BuildingCSUID IN ('1566329899T20080513','1561229778P20210726')"
PARAMS=dict(f='json',where=WHERE,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
def checked_provider(load=read,read_bytes=lambda p:p.read_bytes()):
 req=load(DOC/'exact-current-primary.request.json');raw=read_bytes(DOC/'exact-current-primary.json')
 assert req['url']==BASE+'/0/query' and req['method']=='GET' and req['parameters']==PARAMS,'Exact provider request differs'
 assert req['decodedSHA256']==digest(raw),'Primary decoded bytes differ'
 if req['gzipDecoded']:
  original=read_bytes(DOC/'exact-current-primary.provider-original.gz');assert digest(original)==req['sha256'] and gzip.decompress(original)==raw
 else:assert req['sha256']==digest(raw)
 obj=json.loads(raw);assert not obj.get('error') and not obj.get('exceededTransferLimit') and len(obj['features'])==2
 assert obj['spatialReference'].get('latestWkid',obj['spatialReference'].get('wkid'))==2326
 return obj['features']
def verify_receipt(receipt,read_bytes=lambda p:p.read_bytes()):
 assert receipt['batch']==DOC.name and receipt['identityAccepted'] is False and receipt['newlyInstalled']==0
 refs=receipt['evidenceRefs'];assert len(refs)==len({r['path'] for r in refs})
 for r in refs:
  p=(ROOT/r['path']).resolve();assert p.is_relative_to(ROOT.resolve()) and digest(read_bytes(p))==r['sha256'],'Frozen evidence differs: '+r['path']
 return refs
def native_rows(c):
 return [dict(cacheKey=k,resultSHA256=h,sheet=s,model=m) for k,h,s,m in c.execute("SELECT r.cache_key,r.result_sha,i.sheet,m FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members n USING(cache_key),LATERAL jsonb_array_elements(r.result->'models') m WHERE n.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[s[0] for s in SPEC.values()])).fetchall()]
def current_binding(row,context,tri,capture,load_forms,read_bytes=lambda p:p.read_bytes()):
 assert digest(read_bytes(ROOT/'3d-viewer/city/data/manifest.json'))==capture['manifestSHA256'],'Current manifest differs'
 lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));loaded=load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[f for f,_,_ in loaded]
 hashes={u:digest(read_bytes(ROOT/'3d-viewer'/u)) for _,_,u in loaded}
 assert hashes==capture['tileHashes']==context['neighbourTileHashes'],'Complete current tile inventory differs'
 assert forms==capture['forms'] and len(forms)==len({f['uid'] for f in forms}),'Complete current actor inventory differs'
 assert next(f for f in forms if f['uid']==UID)==row['source']['building']
 return forms
def verify_files(row,context,local):
 receipt=read(DOC/'result.json');verify_receipt(receipt)
 capture=read(DOC/'current-inputs.json.gz');lookup=read(DOC/'original-source-lookup.json.gz');pins=read(DOC/'complete-original-stream-pins.json.gz')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert native_rows(c)==lookup['rows'],'Both exact native run memberships or source versions differ'
  for owner in lookup['ownerReceipts']:
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(owner['jobId'],)).fetchone()==('complete',owner)
   for r in owner['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256'],'Independent owner provenance changed'
 assert len(lookup['rows'])==2
 own=next(r for r in lookup['rows'] if r['model']['modelId']==row['modelId'])
 assert row['native']['cacheKey']==own['cacheKey'] and row['native']['resultSha']==own['resultSHA256'] and row['native']['model']==own['model']
 source={uid:(ROOT/capture['originalPaths'][uid]).read_bytes() for uid in SPEC}
 assert pins=={uid:stream_pin(source[uid],s[0],s[1]) for uid,s in SPEC.items()},'Complete original streams/root/world differ'
 assert capture['originalPaths'][UID]==row['candidate']['path']
 tri=decode_original_world_triangles(source[UID]);s=importlib.util.spec_from_file_location('hospital_current_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 forms=current_binding(row,context,tri,capture,m.load_forms)
 provider=checked_provider();assert provider==lookup['primaryRecords']
 owners={name:(ROOT/capture['ownerPaths'][name]).read_bytes() for name in OWNER}
 previous=raw_verify(row,context,local);out=verify(previous,row,source,forms,provider,owners)
 out['currentBinding']=dict(manifestSHA256=capture['manifestSHA256'],completeCurrentTileHashes=capture['tileHashes'],completeCurrentFormsSHA256=digest(json.dumps(forms,sort_keys=True,separators=(',',':')).encode()),sourceEvidenceJobId=receipt['jobId'],bothNativeRunMembersVerified=True,allEvidenceRefsVerified=True,allOriginalStreamsVerified=True,rawFullCellRecomputed=True,independentOwnerReceiptsVerified=True)
 return out
