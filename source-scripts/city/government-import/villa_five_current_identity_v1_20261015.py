"""Fresh complete-current identity replay for unchanged Villa originals."""
from pathlib import Path
import json,uuid,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from routed_original_cell_identity import verify
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
from villa_original_courtyard_upper_boundary_identity_20261010 import named_proof,UID
from villa_current_bound_courtyard_upper_boundary_identity_20261010 import primary_records
from villa_current_native_inventory_20261010 import native_rows,missing_profiles,verify_native_rows
BASE=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-five-current-identity-v1-20261015';DOC=BASE/NAME
SOURCE=BASE/'government-xl-villa-five-current-physical-v4-20261015';OLD=BASE/'government-xl-villa-current-bound-courtyard-edge-inputs-v1-20261010'
def main():
 assert not DOC.exists();receipt=read(SOURCE/'result.json');old=read(OLD/'result.json');refs={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for r in [receipt,old]:
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']:
    # Historical current-input hashes are checked through the exact archived receipt;
    # only use archived primary/source lookup data from OLD below.
    if r is receipt:refs[q['path']]=q['sha256']
  inventory=native_rows(db);verify_native_rows(inventory);assert missing_profiles(db)==[]
  rows=read(SOURCE/'selection.json.gz')['rows']
  for row in rows:
   found=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone();assert found and found[0]==row['native']['resultSha'];assert [m for m in found[1]['models']if m['modelId']==row['modelId']]==[row['native']['model']]
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h
 for q in old['evidenceRefs']:
  p=ROOT/q['path']
  if p.is_relative_to(OLD):assert digest(p.read_bytes())==q['sha256'];refs[q['path']]=q['sha256']
 lookup=read(OLD/'source-lookup.json.gz');assert inventory==lookup['rows'];primary=primary_records()
 claim=reservations.claim('villa-current-identity-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows],batch=NAME,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();f=module('villa_current_identity_context',HERE/'xl-final-script-pass.py');f.projection=lambda faces:shapely.union_all(shapely.polygons(np.asarray(faces)[:,:,[0,2]]))
  prefixes={r['modelId'][1:11] for r in rows};routes={p:[]for p in prefixes};route_hashes={}
  for tile in json.loads(before)['tiles']:
   p=ROOT/'3d-viewer'/tile['url'];raw=p.read_bytes();forms=json.loads(raw)['buildings'];matches=[b for b in forms if str(b.get('buildingCSUID')or'')[:10]in prefixes]
   if matches:
    route_hashes[tile['url']]=digest(raw)
    for b in matches:routes[b['buildingCSUID'][:10]].append(dict(building=b,tile=tile['url'],tileSHA256=digest(raw)))
  summary=[]
  for row in rows:
   raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);lo,hi=tri.min((0,1)),tri.max((0,1));forms=f.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=f.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms})
   proof=verify(raw,row,context,tri,current_identity=context['identity'],sources=routes[row['modelId'][1:11]]);binding=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()));proof=apply_exact_cell(proof,tri,expected_binding=binding,current_binding=binding);raw_proof=proof
   if row['uid']==UID:proof=named_proof(proof,row,tri,[b for b,_,_ in forms],primary,lookup['missingForeign'])
   save(DOC/(row['uid'].replace('/','-').replace(':','-')+'.json'),dict(context=context,rawIdentity=raw_proof,identity=proof));summary.append(dict(uid=row['uid'],passed=proof['passed'],reasons=proof['reasons'],rawReasons=raw_proof['reasons']));print(summary[-1],flush=True)
   for t,h in context['neighbourTileHashes'].items():refs['3d-viewer/'+t]=h
  assert manifest.read_bytes()==before
  for t,h in route_hashes.items():refs['3d-viewer/'+t]=h
  for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h
  save(DOC/'current-bindings.json',dict(manifestSHA256=digest(before),routeTileHashes=route_hashes,currentNativeInventory=inventory,primaryEvidenceDate='2026-10-10',completeSourceFaces=sum(r['triangles']for r in rows)))
  paths=[ROOT/p for p in refs]+[SOURCE/'result.json',OLD/'result.json',manifest,Path(__file__)]+[HERE/n for n in ['xl-final-script-pass.py','routed_original_cell_identity.py','government_georef_cell_identity.py','exact_original_georef_cell_identity_20261009.py','villa_original_courtyard_upper_boundary_identity_20261010.py','villa_current_bound_courtyard_upper_boundary_identity_20261010.py','villa_current_native_inventory_20261010.py','exact_packed_world_geometry_20261009.py']]
  module('villa_current_identity_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'five-complete-current-original-identities',paths,dict(uids=[r['uid']for r in rows],rows=summary,fullAcceptance=False,publication=False,qualification='Current whole-map routing and native membership; archived dated primary records. Podium identity uses exact named source roof-edge interpretation; physical and source-role acceptance remain separate.'))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
