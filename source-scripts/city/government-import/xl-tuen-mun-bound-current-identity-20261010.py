"""Capture/fence hospital identity inputs, then replay the named proof.

No source changes or physical/installation approval are granted here.
"""
import gzip,importlib.util,json,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from tuen_mun_current_bound_identity_20261010 import DOC,PARAMS,BASE,native_rows,verify_files
from tuen_mun_named_original_hospital_identity_20261010 import SPEC,UID,RELATED,OWNER
from yoho_eight_current_bound_identity_20261009 import stream_pin
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from run import connect
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
BATCH='government-xl-tuen-mun-bound-current-identity-promotion-20261010';OUT=DOC.parent/BATCH;LOCAL=HERE/'local'/BATCH
OLD=DOC.parent/'government-xl-tuen-mun-current-full-cell-preflight-20261009'
PAIR=DOC.parent/'government-xl-tuen-mun-special-primary-counterpart-20261009'
PLAN=DOC.parent/'government-xl-tuen-mun-official-site-plan-20261009'
ABOUT=DOC.parent/'government-xl-tuen-mun-hospital-owner-context-20261009'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not OUT.exists()
 claim=reservations.claim('tuen-mun-bound-identity-'+str(uuid.uuid4()),['building:'+UID,'building:'+RELATED],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  if not (DOC/'result.json').exists():
   assert not DOC.exists();DOC.mkdir(parents=True)
   raw,rec=request(BASE+'/0/query',PARAMS,json_expected=False);decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
   (DOC/'exact-current-primary.json').write_bytes(decoded)
   if raw!=decoded:(DOC/'exact-current-primary.provider-original.gz').write_bytes(raw)
   save(DOC/'exact-current-primary.request.json',{**rec,'decodedSHA256':digest(decoded),'gzipDecoded':raw!=decoded})
   primary=json.loads(decoded);assert not primary.get('error') and not primary.get('exceededTransferLimit') and len(primary['features'])==2
   row=read(OLD/'selection.json.gz')['rows'][0];tp=ROOT/row['candidate']['path'];pair_receipt=read(PAIR/'result.json');pp=next(ROOT/r['path'] for r in pair_receipt['evidenceRefs'] if r['sha256']==SPEC[RELATED][2] and '/assets/' in r['path'])
   original_paths={UID:str(tp.relative_to(ROOT)),RELATED:str(pp.relative_to(ROOT))};sources={uid:(ROOT/p).read_bytes() for uid,p in original_paths.items()}
   pins={uid:stream_pin(sources[uid],s[0],s[1]) for uid,s in SPEC.items()};assert all(pins[uid]['compressedSHA256']==s[2] and pins[uid]['completeWorldSHA256']==s[3] for uid,s in SPEC.items())
   with connect() as c:c.execute('SET TRANSACTION READ ONLY');models=native_rows(c)
   assert len(models)==2
   owner_paths={'official-site-plan-20150518.pdf':str((PLAN/'official-site-plan-20150518.pdf').relative_to(ROOT)),'official-hospital-about.html':str((ABOUT/'official-hospital-about.html').relative_to(ROOT))}
   assert {name:digest((ROOT/p).read_bytes()) for name,p in owner_paths.items()}==OWNER
   lookup=dict(rows=models,primaryRecords=primary['features'],ownerReceipts=[read(PLAN/'result.json')]);save(DOC/'original-source-lookup.json.gz',lookup);save(DOC/'complete-original-stream-pins.json.gz',pins)
   tri=decode_original_world_triangles(sources[UID]);final=module('tuen_mun_fresh_bound_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);own,_,tile=next(x for x in loaded if x[0]['uid']==UID)
   row['source']=dict(building=own,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
   manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());hashes={u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in loaded}
   ctx=dict(uid=UID,sourceSHA256=SPEC[UID][2],identity=final.identity_context(row,tri,loaded),neighbourTileHashes=hashes)
   save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'context.json.gz',dict(rows=[ctx]));save(DOC/'current-inputs.json.gz',dict(manifestSHA256=msha,tileHashes=hashes,forms=[f for f,_,_ in loaded],originalPaths=original_paths,ownerPaths=owner_paths))
   (DOC/'README.md').write_text('''# Tuen Mun Hospital Special Block identity input bindings

Two exact original government source models, every stream/root/world geometry,
both native-run memberships, fresh exact primary query bytes, all current forms
and tiles, and independently reviewed official owner-site documents are pinned.
The dated LegCo plan is explicitly not to scale and provides no coordinates.
The HA introduction and named Special/Main Block source interfaces corroborate
one narrowly named source relation; no occupation permit or legal certification
is invented. Neither this capture nor the podium source receives installation,
terrain, support, collision or runtime credit. All other actors remain foreign.

The complete separate hospital tower collection explains most podium projection
gaps, but that diagnostic does not independently accept any supporting actor.
The raw original/current full geographic cell must be replayed before identity.
''')
   paths=[Path(__file__),HERE/'tuen_mun_current_bound_identity_20261010.py',HERE/'tuen_mun_named_original_hospital_identity_20261010.py',HERE/'test_tuen_mun_named_original_hospital_identity_20261010.py',HERE/'test_tuen_mun_current_bound_identity_20261010.py',HERE/'yoho_eight_current_bound_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_source_ownership.py',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',HERE/'georef_projection_coverage.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_mesh_components.py',HERE/'xl-final-script-pass.py',OLD/'selection.json.gz',tp,pp,manifest,PLAN/'result.json',*[ROOT/r['path'] for r in lookup['ownerReceipts'][0]['evidenceRefs']],*[ROOT/p for p in owner_paths.values()],*[p for p in ABOUT.rglob('*') if p.is_file()],*[ROOT/'3d-viewer'/u for u in hashes]]
   fence=module('hospital_bound_input_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');fence.freeze(DOC.name,'complete-current-primary-native-original-owner-hospital-identity-inputs-v1',paths,dict(uids=[UID,RELATED],identityAccepted=False,scriptFullAcceptancePassed=False,manifestSHA256=msha,requiresAIModelGeometry=False,requiresHumanDecision=False,remainingReason='named-hospital-source-identity-awaiting-complete-bound-replay'))
  row=read(DOC/'selection.json.gz')['rows'][0];ctx=read(DOC/'context.json.gz')['rows'][0];proof=verify_files(row,ctx,LOCAL/'raw-full-cell-replay')
  save(OUT/'identity-proof.json.gz',proof);save(OUT/'selection.json.gz',dict(rows=[row]));save(OUT/'context.json.gz',dict(rows=[ctx]))
  print(json.dumps(dict(passed=proof['passed'],reasons=proof['reasons'],allOriginalFaces=proof['completeOriginalTowerFacesRetained'],physicalAccepted=False,installationApproved=False)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
