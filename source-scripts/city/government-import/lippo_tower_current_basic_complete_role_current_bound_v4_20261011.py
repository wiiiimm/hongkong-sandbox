"""Current byte-bound composition for unchanged Lippo Tower and actual BASIC.
No terrain construction, geometry edits, foreign omissions or publication.
"""
from lippo_exact_own_pending_preapply_phase_guard_v1_20261011 import verify as verify_pending_phase
from exact_current_delta_catalogue_reference_binding_20261011 import verify_delta_catalogue_refs
from exact_complete_owned_bounds_runtime_ground_binding_20261011 import verify as ground_binding,sha_array,bounds_sha
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as ordinary_identity
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from complete_actual_native_position_bounds_separation_20261011 import verify as bounds_verify
from lippo_tower_current_basic_mainbody_join_actual_fixture_v1_20261011 import fixture,INPUT as HISTORICAL
from lippo_tower_current_basic_mainbody_join_role_v1_20261011 import verify as role_verify,TOWER,CARRIER,SOURCE,WORLD
from lippo_tower_current_basic_complete_role_policy_v2_20261011 import validate_semantics,staged_entry
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-lippo-tower-only-current-complete-inputs-v5-20261011'
IDENTITY=BASE/'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v5-20261011'
PHYSICAL=BASE/'government-xl-lippo-tower-only-unchanged-current-ordinary-physical-v3-20261011'
ROLE=BASE/'government-xl-lippo-mainbody-current-basic-join-source-proposal-v1-20261011'
SEPARATION=BASE/'government-xl-lippo-tower-all-current-native-actual-position-separation-v2-20261011'
DELTA=BASE/'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011'
BASELINE=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011'
PHYSICAL_LOCAL=HERE/'local'/PHYSICAL.name
SEMANTIC_GEOMETRY_KEYS=['row','completeCurrentBasicGeometry','completeNearbyNativeGeometry','completeCurrentDrawnTerrain']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt_pins(receipt,reader=lambda p:p.read_bytes()):
 refs=receipt['evidenceRefs'];assert refs and len(refs)==len({r['path'] for r in refs})
 for r in refs:
  p=(ROOT/r['path']).resolve();assert p.is_relative_to(ROOT.resolve())
  assert digest(reader(p))==r['sha256'],'Immutable evidence changed: '+r['path']
 return True
def geometry_equivalence(current,historical):
 assert current['startAndEndInputHashesVerified'] is True
 assert current['sourceGeometryChanges']==current['terrainGeometryChanges']==0
 assert current['originalGovernmentPodiumUsedAsSupport'] is False
 assert current['row']['uid']==TOWER and current['row']['sourceSHA256']==SOURCE
 assert current['row']['completeFaces']==3597 and current['completeCurrentBasicPodiumFaces']==284
 for key in SEMANTIC_GEOMETRY_KEYS:assert current[key]==historical[key],'Changed complete semantic geometry: '+key
 assert len(current['completeCurrentBasicGeometry'])==19 and len(current['completeNearbyNativeGeometry'])==1
 return True
def assert_live(inp,geo):
 assert ref(ROOT/inp['currentManifest']['path'])==inp['currentManifest']
 manifest=read(ROOT/inp['currentManifest']['path'])
 assert [r['path'] for r in inp['currentCatalogueRefs']]==['3d-viewer/'+p for p in manifest['officialModelCatalogues']]
 entries={}
 for r in inp['currentCatalogueRefs']:
  assert ref(ROOT/r['path'])==r
  for e in read(ROOT/r['path'])['models']:
   assert e['uid'] not in entries;entries[e['uid']]=e
 assert len(entries)==6639 and TOWER not in entries and CARRIER not in entries
 for path,sha in geo['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 for path,sha in inp['currentTileHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 assert len(inp['completeCurrentForms'])==len({r['building']['uid'] for r in inp['completeCurrentForms']})==21
 for r in inp['completeCurrentForms']:
  assert inp['currentAllSourceForms'][r['building']['uid']]==r['building']
  assert r['existingNative']==(r['building']['uid'] in entries)
 return entries
PENDING_CONTEXT=BASE/'government-xl-lippo-exact-preapply-pending-attempt-context-v1-20261011/capture.json.gz'
PENDING_CONTEXT_SHA256='7e7a20f10290182433e7a89ce1ee9763ae4d07e2af800b380b819c2a74b04fbd'
def verify_pending_live(c,path):
 assert Path(path).resolve()==PENDING_CONTEXT.resolve()
 assert digest(PENDING_CONTEXT.read_bytes())==PENDING_CONTEXT_SHA256
 context=read(PENDING_CONTEXT);current_refs={};current_files={}
 for key,pin in context['exactLiveFiles'].items():
  current_refs[key]=ref(ROOT/pin['path']);assert current_refs[key]==pin
  current_files[key]=read(ROOT/pin['path'])
 for pin in current_files['attemptAcceptance']['evidenceRefs']:
  assert ref(ROOT/pin['path'])==pin
 receipt=current_files['completeRoleReceipt']
 assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 queried={}
 for table,order in [('model_reviews','snapshot_id'),('model_review_events','id')]:
  cursor=c.execute('SELECT * FROM astra_modelling.'+table+' WHERE uid=%s ORDER BY '+order,(TOWER,))
  names=[field.name for field in cursor.description]
  queried[table]=json.loads(json.dumps([dict(zip(names,row))for row in cursor.fetchall()],default=str))
 proof=verify_pending_phase(context,queried['model_reviews'],queried['model_review_events'],current_refs,current_files)
 assert proof['exactOwnApprovedPendingAttemptRecognised'] and not proof['numericOrPhysicalExemption']
 return proof
def verify_files(local,*,pending_attempt=None):
 inp=read(INPUT/'input.json.gz');geo=read(INPUT/'complete-current-geometry.json.gz')
 folders=[INPUT,IDENTITY,PHYSICAL,ROLE,SEPARATION,DELTA];receipts=[read(p/'result.json') for p in folders]
 for receipt in receipts:receipt_pins(receipt)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  row=inp['rows'][0];assert len(inp['rows'])==1 and row['uid']==TOWER and row['sourceSHA256']==SOURCE
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  if pending_attempt is None:
   assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(TOWER,)).fetchone()
  else:
   verify_pending_live(c,pending_attempt)
 entries=assert_live(inp,geo);historical=read(HISTORICAL/'complete-current-geometry.json.gz');geometry_equivalence(geo,historical)
 oldinput=read(HISTORICAL/'input.json.gz')
 assert inp['completeCurrentForms']==oldinput['completeCurrentForms'] and inp['currentAllSourceForms']==oldinput['currentAllSourceForms']
 final=module('lippo_bound_current_forms','xl-final-script-pass.py');forms=final.load_forms(inp['geographicScope'])
 assert [dict(building=b,existingNative=b['uid'] in entries,tile=t) for b,_,t in forms]==inp['completeCurrentForms']
 assert {str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms}==inp['currentTileHashes']
 context=next(r for r in read(IDENTITY/'context.json.gz')['rows'] if r['uid']==TOWER)
 identity=ordinary_identity(row,context,Path(local)/'complete-ordinary-identity-replay')
 assert identity==read(IDENTITY/'identity.json') and identity['passed'] and identity['reasons']==[]
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE
 original=decode_original_world_triangles(raw);packed=packed_world_bounds(raw)
 assert packed['allOriginalPositionVerticesAccounted'] and packed['completeOriginalTriangles']==3597
 ix=np.asarray(geo['row']['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
 worlds={'providerOriginal':original};keys=[('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]
 for mode,key in keys:worlds[mode]=np.asarray(geo['row'][key],dtype='<f8').reshape(-1,3)[ix]
 data=fixture();data['worlds']=worlds;data['sourceSHA256']=SOURCE;data['towerCurrentForm']=row['source']['building']
 carrier=next(b for b in geo['completeCurrentBasicGeometry'] if b['uid']==CARRIER)
 data['carrierCurrentForm']=carrier['currentForm'];data['carrierIdentityModelMatrix']=carrier['identityModelMatrix']
 data['basic']=np.asarray(carrier['position'],dtype='<f8').reshape(-1,3)[np.asarray(carrier['index'],dtype=np.int64).reshape(-1,3)]
 data['groundSHA256']=geo['completeCurrentDrawnTerrain']['worldSHA256']
 role=role_verify(data);assert role==read(ROLE/'diagnostic.json.gz')
 physical=read(PHYSICAL/'diagnostic.json.gz');assert physical['currentManifest']==inp['currentManifest']
 runtime=read(PHYSICAL_LOCAL/'runtime-geometry.json.gz')['rows'];assert len(runtime)==1 and runtime[0]['uid']==TOWER
 r=runtime[0];actual=np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)]
 ground=np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 drawn=geo['completeCurrentDrawnTerrain'];drawn_tri=np.asarray(drawn['position'],dtype='<f8').reshape(-1,3)[np.asarray(drawn['index'],dtype=np.int64).reshape(-1,3)]
 assert np.array_equal(actual,worlds['actualLiteral'])
 runtime_owned_bounds={'providerOriginal':packed['originalWholeSourceBounds']}
 for mode,key in keys:
  pos=np.asarray(geo['row'][key],dtype='<f8').reshape(-1,3);assert len(pos)==packed['completeOriginalPositionVertices']
  runtime_owned_bounds[mode]=[pos.min(0).tolist(),pos.max(0).tolist()]
 runtime_ground_binding=ground_binding(drawn_tri,ground,runtime_owned_bounds,regional_sha=drawn['worldSHA256'],runtime_sha=sha_array(ground),owned_bounds_sha=bounds_sha(runtime_owned_bounds))
 assert runtime_ground_binding['completeRegionalGroundFacets']==1713 and runtime_ground_binding['completeRuntimeGroundFacets']==320

 foundation=read(PHYSICAL/'foundation.json')['rows'];assert len(foundation)==1 and foundation[0]['uid']==TOWER and foundation[0]['strictFoundationAccepted'] is True
 assert foundation[0]['sourceSHA256']==SOURCE
 current=read(DELTA/'input.json.gz');composition=read(DELTA/'composition.json.gz');bindings=read(DELTA/'complete-unchanged-baseline-bindings.json.gz')
 assert current['currentManifest']==composition['currentManifest']==bindings['currentManifest']==inp['currentManifest']
 verify_delta_catalogue_refs(current['currentCatalogueRefs'],inp['currentCatalogueRefs'],read(ROOT/inp['currentManifest']['path']))
 old=read(BASELINE/'inventory.json.gz');delta=read(DELTA/'inventory.json.gz');assert old['successfullyCapturedActors']==6637 and delta['successfullyCapturedActors']==2 and not old['errors'] and not delta['errors']
 assert composition['baselineInventory']==ref(BASELINE/'inventory.json.gz') and composition['actualCurrentDelta']==ref(DELTA/'inventory.json.gz')
 assert composition['baselineCurrentExactBinding']==ref(DELTA/'complete-unchanged-baseline-bindings.json.gz')
 oldby={a['uid']:a for a in old['rows']};assert len(oldby)==len(bindings['rows'])==6637 and {b['uid'] for b in bindings['rows']}==set(oldby)
 for b in bindings['rows']:
  assert b['unchangedActualCompleteBoundsRowSHA256']==digest(json.dumps(oldby[b['uid']],sort_keys=True,separators=(',',':')).encode())
  assert ref(ROOT/b['source']['path'])==b['source']
 assert [a['uid'] for a in delta['rows']]==['landsd/255438:0','landsd/256116:0']
 actors=old['rows']+delta['rows'];assert {a['uid'] for a in actors}==set(entries)
 owned={'providerOriginal':packed['originalWholeSourceBounds']}
 for mode,key in keys:
  pos=np.asarray(geo['row'][key],dtype='<f8').reshape(-1,3);assert len(pos)==packed['completeOriginalPositionVertices'];owned[mode]=[pos.min(0).tolist(),pos.max(0).tolist()]
 separation=read(SEPARATION/'diagnostic.json.gz');assert separation['completeNativeActualBoundsCertificate']==bounds_verify(owned,actors)
 assert separation['completeOwnedWorldBounds']==owned and separation['currentBaselineAndDeltaExactBindings']==ref(DELTA/'composition.json.gz')
 result=validate_semantics(identity,physical,separation,role,inp['currentManifest'])
 result.update(exactCompleteRuntimeGroundScopeBinding=runtime_ground_binding,currentManifest=inp['currentManifest'],sourceSHA256=SOURCE,currentBoundOriginalAndLiteralAndTwoFloat32Proofs=True,completeCurrentBasicFaces=284,completeCurrentForeignActors=19,completeCurrentNativeActualPositionActors=6639,terrainProposal=None,unmockedProductionIdentityNativeAndNeonReplay=True,sourceRoleReplay=role,completeDrawnGroundSHA256=drawn['worldSHA256'],ordinaryPhysicalReceipt=ref(PHYSICAL/'result.json'),sourceRoleReceipt=ref(ROLE/'result.json'),completeNativeSeparationReceipt=ref(SEPARATION/'result.json'))
 assert_live(inp,geo)
 for receipt in receipts:receipt_pins(receipt)
 if pending_attempt is not None:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');verify_pending_live(c,pending_attempt)
 return result,staged_entry(row['candidate']['entry'])
