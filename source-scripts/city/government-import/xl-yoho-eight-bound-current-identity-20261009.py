"""Capture new primary/source/current bindings, fence, then recompute identity."""
import gzip,importlib.util,json,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from yoho_eight_current_bound_identity_20261009 import DOC,QUERIES,BASE,native_rows,stream_pin,verify_files
from yoho_eight_related_original_podium_identity_20261009 import UID,RELATED,SOURCE_SHA,PODIUM_SHA
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
BATCH='government-xl-yoho-eight-current-bound-identity-promotion-20261009';OUT=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not OUT.exists();claim=reservations.claim('yoho-bound-identity-'+str(uuid.uuid4()),['building:'+UID,'building:'+RELATED],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  if not (DOC/'result.json').exists():
   assert not DOC.exists();DOC.mkdir(parents=True)
   for name,(table,where,geometry) in QUERIES.items():
    params={'f':'json','where':where,'outFields':'*','returnGeometry':'true' if geometry else 'false','outSR':'2326','resultRecordCount':'1000','orderByFields':'OBJECTID'}
    raw,rec=request(BASE+'/'+str(table)+'/query',params,json_expected=False);decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw;(DOC/(name+'.json')).write_bytes(decoded)
    if raw!=decoded:(DOC/(name+'.provider-original.gz')).write_bytes(raw)
    rec.update(decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded);save(DOC/(name+'.request.json'),rec)
   old=ROOT/'docs/astra-city/government-import/government-xl-yoho-eight-current-full-cell-preflight-20261009/selection.json.gz';row=read(old)['rows'][0]
   with connect() as c:c.execute('SET TRANSACTION READ ONLY');models=native_rows(c)
   assert len(models)==2;lookup={'rows':models,'primaryRecords':read(DOC/'exact-current-primary.json')['features'],'exactRelations':read(DOC/'exact-current-structure-relations.json')['features'],'exactStructures':read(DOC/'exact-current-structure-details.json')['features']};save(DOC/'original-source-lookup.json.gz',lookup)
   tp=ROOT/row['candidate']['path'];pp=HERE/'local/government-xl-five-more-original-supports-current-inputs-20261007/assets'/(PODIUM_SHA+'.glb.gz');traw,praw=tp.read_bytes(),pp.read_bytes();assert digest(traw)==SOURCE_SHA and digest(praw)==PODIUM_SHA
   save(DOC/'complete-original-stream-pins.json.gz',{'tower':stream_pin(traw,row['modelId'],14792),'podium':stream_pin(praw,'B218783363602062G0',7731)})
   tri=decode_original_world_triangles(traw);final=module('yoho_fresh_binding_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);own,_,tile=next(x for x in forms if x[0]['uid']==UID);row['source']={'building':own,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())}
   manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());hashes={u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms};ctx={'uid':UID,'sourceSHA256':SOURCE_SHA,'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':hashes}
   save(DOC/'selection.json.gz',{'rows':[row]});save(DOC/'context.json.gz',{'rows':[ctx]});save(DOC/'current-inputs.json.gz',{'manifestSHA256':msha,'tileHashes':hashes,'forms':[b for b,_,_ in forms],'podiumOriginalPath':str(pp.relative_to(ROOT))})
   (DOC/'README.md').write_text('''# Yoho Town Block8 immutable current/provider/source bindings

Three newly retrieved government queries capture the unique Active Tower8 and
Podium, their exact distinct structure relationships and NT21/2004(OP) roles.
Original provider response bytes, decoded bytes, request parameters and ETags
are preserved. Both native source versions and complete unchanged GLB roots,
all buffer views/attributes/index streams, binary payloads and world geometry
are pinned. Every nearby current form/tile and current manifest is captured.

This checkpoint grants no identity, physical or installation credit. The named
adapter must independently replay every evidence SHA/Neon native version and
recompute full current actor enumeration and the ordinary whole-cell check.
Current OBJECTID reindexing is recorded only; no viewer metadata changes.
All143 detached original parts and the actual current podium remain retained.
''')
   paths=[Path(__file__),HERE/'yoho_eight_current_bound_identity_20261009.py',HERE/'yoho_eight_related_original_podium_identity_20261009.py',HERE/'test_yoho_eight_related_original_podium_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_source_ownership.py',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',HERE/'georef_projection_coverage.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'source_closed_components.py',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',old,tp,pp,manifest,*[ROOT/'3d-viewer'/u for u in hashes]]
   fence=module('yoho_source_current_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');fence.freeze(DOC.name,'complete-current-primary-native-root-all-stream-identity-inputs-v1',paths,{'uids':[UID,RELATED],'identityAccepted':False,'scriptFullAcceptancePassed':False,'manifestSHA256':msha,'remainingReason':'reviewed-named-identity-awaiting-complete-bound-replay','requiresAIModelGeometry':False,'requiresHumanDecision':False})
  row=read(DOC/'selection.json.gz')['rows'][0];ctx=read(DOC/'context.json.gz')['rows'][0];proof=verify_files(row,ctx,LOCAL/'raw-full-cell-replay');save(OUT/'identity-proof.json.gz',proof);save(OUT/'selection.json.gz',{'rows':[row]});save(OUT/'context.json.gz',{'rows':[ctx]})
  print(json.dumps({'passed':proof['passed'],'reasons':proof['reasons'],'manifestSHA256':proof['currentBinding']['manifestSHA256'],'physicalAccepted':False,'installationApproved':False}),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
