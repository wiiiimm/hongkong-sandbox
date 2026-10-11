"""Immutable provenance/current-form adapter for the one reviewed Man Fuk envelope relationship.

No source or current actor edits. This identity-only adapter is deliberately
invalidated by any manifest/tile/source/provider/native-receipt change.
"""
import gzip,importlib.util,json,struct
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from original_source_ownership import document,graph_reasons
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from routed_original_cell_identity import verify_files as raw_verify
from man_fuk_named_original_envelope_identity_v3_20261010 import named_proof,UID,RELATED,EXACT,SOURCE_SHA,RELATED_SHA

DOC=ROOT/'docs/astra-city/government-import/government-xl-man-fuk-current-bound-envelope-inputs-20261010'
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
QUERIES={
 'exact-current-primary':(0,"BuildingCSUID IN ('3644619608P20050726','3647219454T20050430')",True),
 'exact-current-structure-relations':(1002,"BuildingCSUID IN ('3644619608P20050726','3647219454T20050430')",False),
}

def stream_pin(raw,model_id,faces):
 assert not graph_reasons(document(raw),model_id,faces),'Original complete source graph differs'
 data=gzip.decompress(raw);g=document(raw);length=struct.unpack_from('<I',data,12)[0];off=20+length;n,kind=struct.unpack_from('<II',data,off);assert kind==0x004e4942 and off+8+n==len(data)
 binary=data[off+8:];views=[]
 for i,v in enumerate(g['bufferViews']):
  start=v.get('byteOffset',0);end=start+v['byteLength'];assert 0<=start<=end<=len(binary)
  views.append({'index':i,'definition':v,'sha256':digest(binary[start:end])})
 return {'compressedSHA256':digest(raw),'decompressedSHA256':digest(data),'completeBinarySHA256':digest(binary),'graph':g,'allBufferViews':views,'completeWorldSHA256':digest(decode_original_world_triangles(raw).astype('<f8').tobytes())}

def checked_provider(name,load=read,read_bytes=lambda p:p.read_bytes()):
 table,where,geometry=QUERIES[name];p=DOC/(name+'.json');req=load(DOC/(name+'.request.json'));raw=read_bytes(p)
 params={'f':'json','where':where,'outFields':'*','returnGeometry':'true' if geometry else 'false','outSR':'2326','resultRecordCount':'1000','orderByFields':'OBJECTID'}
 assert req['url']==BASE+'/'+str(table)+'/query' and req['method']=='GET' and req['parameters']==params,'Provider query differs'
 assert req['decodedSHA256']==digest(raw),'Decoded provider bytes differ'
 if req['gzipDecoded']:
  original=read_bytes(DOC/(name+'.provider-original.gz'));assert digest(original)==req['sha256'] and gzip.decompress(original)==raw
 else:assert digest(raw)==req['sha256']
 obj=json.loads(raw);assert not obj.get('error') and not obj.get('exceededTransferLimit') and 'features' in obj
 if geometry:assert obj['spatialReference'].get('latestWkid',obj['spatialReference'].get('wkid'))==2326
 return obj['features']

def verify_receipt(receipt,read_bytes=lambda p:p.read_bytes()):
 assert receipt['batch']==DOC.name and receipt['identityAccepted'] is False and receipt['newlyInstalled']==0
 refs=receipt['evidenceRefs'];assert len(refs)==len({r['path'] for r in refs})
 for ref in refs:
  p=(ROOT/ref['path']).resolve();assert p.is_relative_to(ROOT.resolve());assert digest(read_bytes(p))==ref['sha256'],'Frozen evidence reference changed: '+ref['path']
 return refs

def current_binding(row,context,tri,capture,load_forms,read_bytes=lambda p:p.read_bytes()):
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(read_bytes(manifest))==capture['manifestSHA256'],'Current manifest differs'
 lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));loaded=load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 forms=[b for b,_,_ in loaded];hashes={u:digest(read_bytes(ROOT/'3d-viewer'/u)) for _,_,u in loaded}
 assert hashes==context['neighbourTileHashes']==capture['tileHashes'],'Complete current tile inventory differs'
 assert forms==capture['forms'],'Complete current actor inventory differs'
 assert next(b for b in forms if b['uid']==UID)==row['source']['building']
 return forms

def native_rows(connection):
 return [{'sourceKey':k+'/'+m['modelId'],'model':m,'sheet':s,'resultSHA256':h} for k,m,s,h in connection.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key),LATERAL jsonb_array_elements(r.result->'models') m WHERE m->>'modelId' IN ('B364461960802063C0','B364721945401063C0') ORDER BY m->>'modelId'").fetchall()]

def verify_files(row,context,local):
 receipt=read(DOC/'result.json');verify_receipt(receipt)
 capture=read(DOC/'current-inputs.json.gz');source=read(DOC/'original-source-lookup.json.gz');pins=read(DOC/'complete-original-stream-pins.json.gz')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt),'Frozen Neon receipt differs'
  assert native_rows(c)==source['rows'],'Exact current native source versions differ'
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 assert len(source['rows'])==2 and row['native']['model']==source['rows'][0]['model'] and row['native']['resultSha']==source['rows'][0]['resultSHA256']
 own_path=ROOT/row['candidate']['path'];related_path=ROOT/capture['relatedOriginalPath'];traw=own_path.read_bytes();praw=related_path.read_bytes();assert digest(traw)==SOURCE_SHA and digest(praw)==RELATED_SHA
 assert pins=={'own':stream_pin(traw,row['modelId'],10661),'related':stream_pin(praw,'B364721945401063C0',2160)},'Complete source root/streams differ'
 t,p=decode_original_world_triangles(traw),decode_original_world_triangles(praw)
 s=importlib.util.spec_from_file_location('man_fuk_complete_current_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 forms=current_binding(row,context,t,capture,m.load_forms)
 dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==traw
 else:dest.write_bytes(traw)
 previous=raw_verify(row,context,local)
 evidence={**source,'rows':source['rows'],'primaryRecords':checked_provider('exact-current-primary'),'exactRelations':checked_provider('exact-current-structure-relations'),'exactStructures':[]}
 assert source['primaryPlanSHA256']==digest((DOC/'ha-estate-layout.pdf').read_bytes()) and source['primaryFloorPlanSHA256']==digest((DOC/'ha-man-oi-block-k.pdf').read_bytes())
 assert source['primaryBlockAPlanSHA256']==digest((DOC/'ha-man-fuk-block-a.pdf').read_bytes())
 assert evidence==source,'Captured primary/source evidence differs'
 out=named_proof(previous,row,t,p,forms,evidence)
 out.update(currentBinding={'manifestSHA256':capture['manifestSHA256'],'completeCurrentTileHashes':capture['tileHashes'],'completeCurrentFormsSHA256':digest(json.dumps(forms,sort_keys=True,separators=(',',':')).encode()),'sourceEvidenceJobId':receipt['jobId'],'allEvidenceRefsVerified':True,'allOriginalStreamsVerified':True,'rawFullCellRecomputed':True},providerObjectIdRevisions=[{'uid':uid,'currentViewerObjectId':next(b for b in forms if b['uid']==uid)['objectId'],'currentPrimaryObjectId':next(b for b in evidence['primaryRecords'] if b['attributes']['BuildingCSUID']==EXACT[uid][0])['attributes']['OBJECTID']} for uid in [UID,RELATED]])
 return out
