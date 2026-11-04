"""Current/provider/native/source binding for a mandatory two-original assembly.

A positive upper identity is unusable without the complete unchanged lower
platform. This adapter grants no standalone physical/import/installation credit.
"""
import gzip,importlib.util,json,numpy as np
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin
from lei_tung_named_original_lower_platform_identity_20261010 import UID,PLATFORM,SOURCE_SHA,PLATFORM_SHA,named_proof
DOC=ROOT/'docs/astra-city/government-import/government-xl-lei-tung-two-original-platform-current-inputs-v2-20261010'
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
MODELS={UID:('B341701135801063C0',SOURCE_SHA,874),PLATFORM:('B341711135802063C0',PLATFORM_SHA,432)}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def native_rows(c):
 return [{'sourceKey':k+'/'+m['modelId'],'model':m,'sheet':s,'resultSHA256':h} for k,m,s,h in c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE m->>'modelId' IN ('B341701135801063C0','B341711135802063C0') ORDER BY m->>'modelId'").fetchall()]
def verify_native_rows(rows):
 assert len(rows)==2 and len({r['sourceKey'] for r in rows})==2
 expected={mid:sha for mid,sha,_ in MODELS.values()};assert {r['model']['modelId'] for r in rows}==set(expected)
 for r in rows:assert r['sourceKey'].endswith('/'+r['model']['modelId']) and len(r['sourceKey'].split('/'))==2 and r['model']['asset']['sha256']==expected[r['model']['modelId']]
 return True
def verify_receipt(receipt,read_bytes=lambda p:p.read_bytes()):
 assert receipt['batch']==DOC.name and receipt['identityAccepted'] is False and receipt['newlyInstalled']==0
 assert len(receipt['evidenceRefs'])==len({r['path'] for r in receipt['evidenceRefs']})
 for ref in receipt['evidenceRefs']:
  p=(ROOT/ref['path']).resolve();assert p.is_relative_to(ROOT.resolve());assert digest(read_bytes(p))==ref['sha256'],'Frozen evidence reference changed: '+ref['path']
 return True
def checked_provider(name,table,geometry,load=read,read_bytes=lambda p:p.read_bytes()):
 p=DOC/(name+'.json');req=load(DOC/(name+'.request.json'));raw=read_bytes(p);params={'f':'json','where':"BuildingCSUID IN ('3417311416T20050430','3417111358P20060312','3417011358T20050430')",'outFields':'*','returnGeometry':'true' if geometry else 'false','outSR':'2326','resultRecordCount':'1000','orderByFields':'OBJECTID'}
 assert req['method']=='GET' and req['url']==BASE+'/'+str(table)+'/query' and req['parameters']==params and req['decodedSHA256']==digest(raw)
 if req['gzipDecoded']:
  original=read_bytes(DOC/(name+'.provider-original.gz'));assert digest(original)==req['sha256'] and gzip.decompress(original)==raw
 else:assert digest(raw)==req['sha256']
 obj=json.loads(raw);assert not obj.get('error') and not obj.get('exceededTransferLimit')
 if geometry:assert obj['spatialReference'].get('latestWkid',obj['spatialReference'].get('wkid'))==2326
 return obj['features']
def current_binding(rows,contexts,tri,capture,load_forms,read_bytes=lambda p:p.read_bytes()):
 assert digest(read_bytes(ROOT/'3d-viewer/city/data/manifest.json'))==capture['manifestSHA256'],'Current manifest differs'
 lo,hi=tri.min((0,1)),tri.max((0,1));loaded=load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded];hashes={u:digest(read_bytes(ROOT/'3d-viewer'/u)) for _,_,u in loaded}
 assert hashes==capture['tileHashes'] and forms==capture['forms'],'Complete current pair scope differs'
 assert len(rows)==len(contexts)==2 and {r['uid'] for r in rows}=={UID,PLATFORM} and {c['uid'] for c in contexts}=={UID,PLATFORM}
 for r in rows:
  assert next(b for b in forms if b['uid']==r['uid'])==r['source']['building'];assert next(c for c in contexts if c['uid']==r['uid'])['neighbourTileHashes']==hashes
 return forms

def verify_files(row,context,local):
 receipt=read(DOC/'result.json');verify_receipt(receipt);source=read(DOC/'source-lookup.json.gz');verify_native_rows(source['rows']);capture=read(DOC/'current-inputs.json.gz');pins=read(DOC/'complete-original-stream-pins.json.gz');selection=read(DOC/'selection.json.gz');rows=selection['rows'];contexts=read(DOC/'context.json.gz')['rows'];assert row==next(r for r in rows if r['uid']==row['uid']) and context==next(c for c in contexts if c['uid']==row['uid'])
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  actual=native_rows(c);verify_native_rows(actual);assert actual==source['rows']
  for r in rows:
   n=next(n for n in actual if n['model']['modelId']==r['modelId']);assert r['native']['model']==n['model'] and r['native']['resultSha']==n['resultSHA256'] and r['native']['cacheKey']==n['sourceKey'].rsplit('/',1)[0]
   assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
 worlds={};actual_pins={}
 for r in rows:
  mid,sha,count=MODELS[r['uid']];raw=(ROOT/r['candidate']['path']).read_bytes();assert r['modelId']==mid and digest(raw)==sha==r['sourceSHA256'];worlds[r['uid']]=decode_original_world_triangles(raw);actual_pins[r['uid']]=stream_pin(raw,mid,count)
 assert actual_pins==pins
 forms=current_binding(rows,contexts,np.concatenate(list(worlds.values())),capture,module('lei_tung_complete_actual_forms','xl-final-script-pass.py').load_forms)
 raw={r['uid']:raw_verify(r,next(c for c in contexts if c['uid']==r['uid']),local/r['uid'].split('/')[1]) for r in rows}
 primary=checked_provider('exact-current-primary',0,True);assert not checked_provider('exact-current-structure-relations',1002,False),'No unsupported permit/structure relation claim'
 upper=next(r for r in rows if r['uid']==UID);platform=next(r for r in rows if r['uid']==PLATFORM);proof=named_proof(raw[UID],upper,platform,worlds[UID],worlds[PLATFORM],forms,primary)
 # The platform's independent ordinary identity must also pass. A positive
 # upper assembly proof never erases a separate lower-source reason.
 if not raw[PLATFORM]['passed']:
  proof['passed']=False;proof['reasons']=sorted(set(proof['reasons']+['mandatory-lower-original:'+r for r in raw[PLATFORM]['reasons']]))
 if row['uid']==PLATFORM:
  platform_proof=dict(raw[PLATFORM]);platform_proof.update(mandatoryOriginalRuntimeUIDs=[UID,PLATFORM],standaloneOriginalImportAccepted=False,physicalAccepted=False,installationApproved=False,mandatoryPairedUpperIdentityPassed=proof['passed'])
  if not proof['passed']:platform_proof['passed']=False;platform_proof['reasons']=sorted(set(platform_proof['reasons']+['mandatory-upper-assembly-identity-failed']))
  proof=platform_proof
 proof.update(currentBinding={'manifestSHA256':capture['manifestSHA256'],'completeCurrentTileHashes':capture['tileHashes'],'completeCurrentFormsSHA256':digest(json.dumps(forms,sort_keys=True,separators=(',',':')).encode()),'sourceEvidenceJobId':receipt['jobId'],'bothNativeRunMembershipsVerified':True,'allEvidenceRefsVerified':True,'allOriginalStreamsVerified':True,'rawBothFullCellsRecomputed':True},rawIndependentOriginalIdentities=raw,mandatoryCompleteOriginalRuntimeAssemblyOnly=True)
 return proof
