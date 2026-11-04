"""Unexecuted fresh T/P whole attributes/four-world/actual-ground input draft.
The current production loader and terrain closures are independently pinned before
and after both actual loads. No historical rendered proof, root or support credit.
"""
import argparse,copy,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-heya-aqua-184286-current-owned-identity-v1-20261011'
OLD=BASE/'government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json'
BATCH='government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
JS=HERE/'xl-heya-aqua-184286-184285-current-actual-ground-geometry-v1-20261011.mjs'
UIDS=['landsd/184286:0','landsd/184285:0']
EXPECTED={UIDS[0]:('f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155',17910),UIDS[1]:('46add0484e7cedd20b7de12c9843a2cba8bb419f5824dde27fb9b41fb8efa1b2',3844)}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 assert not DOC.exists(),'Immutable completed/failed attempt'
 receipt=read(INPUT/'result.json');assert receipt['identityAccepted'] and not receipt['physicalAccepted']
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert before==(INPUT/'captured-manifest.json').read_bytes()
 if not args.owned:
  assert not LOCAL.exists();claim=reservations.claim('heya-actual-source-ground-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  status=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode
  assert status==0,status;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selected=read(INPUT/'selection.json.gz');assert len(selected['rows'])==1 and selected['rows'][0]['uid']==UIDS[0]
 support=read(INPUT/'installed-support-entry.json');assert ref(ROOT/support['catalogue']['path'])==support['catalogue'] and ref(ROOT/support['asset']['path'])==support['asset']
 old_support=[r for r in read(OLD)['sources']if r['uid']==UIDS[1]];assert len(old_support)==1
 rows=[copy.deepcopy(selected['rows'][0]),copy.deepcopy(old_support[0])]
 rows[1]['candidate']=dict(path=support['asset']['path'],entry=support['entry'])
 originals={};position_proofs={}
 for row in rows:
  sha,n=EXPECTED[row['uid']];assert row['sourceSHA256']==sha and row['triangles']==n
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==sha
  originals[row['uid']]=decode_original_world_triangles(raw);assert originals[row['uid']].shape==(n,3,3) and np.isfinite(originals[row['uid']]).all()
  position_proofs[row['uid']]=packed_world_bounds(raw)
 bounds=[p['originalWholeSourceBounds']for p in position_proofs.values()]
 # Nomination only; actual exporter proves its closed all-four-world +/-2 ground
 # rectangles lie inside this complete current-form fetch rectangle.
 form_bounds=[min(b[0][0]for b in bounds)-4,min(b[0][2]for b in bounds)-4,max(b[1][0]for b in bounds)+4,max(b[1][2]for b in bounds)+4]
 final=module('heya_fresh_complete_forms','xl-final-script-pass.py');forms=final.load_forms(form_bounds)
 assert len(forms)==len({b['uid']for b,_,_ in forms});by_uid={b['uid']:(b,t)for b,_,t in forms}
 assert rows[0]['source']['building']==by_uid[UIDS[0]][0]
 b,t=by_uid[UIDS[1]];assert b['buildingCSUID']=='3394422191P20151008'
 rows[1]['source']=dict(building=b,tile=t,tileSHA256=digest((ROOT/'3d-viewer'/t).read_bytes()))
 tile_pins={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms}
 catalogue_refs=read(INPUT/'all-current-catalogues.json')['rows']
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 initial=[Path(__file__),JS,OLD,INPUT/'result.json',INPUT/'selection.json.gz',INPUT/'context.json.gz',INPUT/'installed-support-entry.json',INPUT/'all-current-catalogues.json',INPUT/'complete-two-native-source-memberships.json',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_packed_world_bounds_v3_20261010.py']
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in initial}
 DOC.mkdir()
 save(DOC/'capture-inputs.json.gz',dict(rows=rows,completeCurrentForms=[b for b,_,_ in forms],completeCurrentFormBounds=form_bounds,neighbourTileHashes=tile_pins,completeCurrentCatalogueRefs=catalogue_refs,inputHashes=pins,manifestSHA256=digest(before),physicalAccepted=False,installationApproved=False))
 for uid,p in position_proofs.items():save(DOC/('whole-original-position-proof-'+uid.split('/')[1].replace(':','-')+'.json'),p)
 captures={};streams_out={};all_refs=list(initial)
 for row in rows:
  uid=row['uid'];slug=uid.split('/')[1].replace(':','-');status=subprocess.run(['node',str(JS),uid],cwd=ROOT,capture_output=True,text=True)
  save(DOC/('export-'+slug+'-log.json'),dict(exitCode=status.returncode,stdout=status.stdout,stderr=status.stderr));assert status.returncode==0,status.stderr
  capture=read(DOC/('complete-current-actual-source-and-ground-'+slug+'.json.gz'));sha,n=EXPECTED[uid]
  assert capture['uid']==uid and capture['sourceSHA256']==sha and capture['entry']==row['candidate']['entry'] and capture['completeFaces']==n and capture['startAndEndInputsVerified']
  assert capture['completeOriginalPOSITIONProof']==position_proofs[uid]
  index=np.asarray(capture['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'providerOriginal':originals[uid]}
  for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(capture[key],dtype='<f8').reshape(-1,3)[index]
  assert all(w.shape==(n,3,3)and np.isfinite(w).all()for w in worlds.values())
  ground=np.asarray(capture['currentDrawnGround']['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3)
  assert len(ground)==capture['currentDrawnGround']['completeRegionalFaces']and np.isfinite(ground).all()and digest(ground.tobytes())==capture['currentDrawnGround']['worldTriangleSHA256']
  for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  captures[uid]=capture;streams_out[uid]=dict(uid=uid,sourceSHA256=sha,completeWorldStreams={m:dict(completeFaces=n,completeWorldTriangleSHA256=digest(w.astype('<f8').tobytes()),completeWorldTriangles=w.tolist())for m,w in worlds.items()},completeDrawnGround=ground.tolist(),completeDrawnGroundSHA256=digest(ground.tobytes()),sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False)
  all_refs.extend(ROOT/p for p in capture['inputHashes'])
 assert captures[UIDS[0]]['completeRecursiveLoaderModuleClosure']==captures[UIDS[1]]['completeRecursiveLoaderModuleClosure']
 assert captures[UIDS[0]]['completeRecursiveTerrainModuleClosure']==captures[UIDS[1]]['completeRecursiveTerrainModuleClosure']
 save(DOC/'complete-two-actor-four-stream-ground-inputs.json.gz',dict(rows=streams_out,allSlopesAndZeroProjectionGroundRetained=True,noHistoricalRuntimeProofTransfer=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False))
 assert manifest.read_bytes()==before and reservations.owns(lease)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 for t,h in tile_pins.items():assert digest((ROOT/'3d-viewer'/t).read_bytes())==h
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 freezer=module('heya_actual_ground_freezer','xl-popcorn-source-investigations-checkpoints-20261009.py')
 r=freezer.freeze(BATCH,'heya-complete-two-actual-source-four-world-current-ground-no-role-credit',all_refs+[p for p in DOC.rglob('*')if p.is_file()],dict(uids=UIDS,completeSourceFaces={u:EXPECTED[u][1]for u in UIDS},completeCurrentForms=len(forms),currentAcceptance=False,physicalAccepted=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 print(json.dumps(dict(jobId=r['jobId'],currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
