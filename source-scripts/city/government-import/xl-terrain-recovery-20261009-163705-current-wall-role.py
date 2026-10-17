"""Replay the independently frozen original exterior role on fresh complete current physics."""
import json,numpy as np,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_packed_world_bounds_20261009 import packed_world_bounds
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from unchanged_authored_crossing_wall_role_20261009 import verify_wall_role
BATCH='xl-terrain-recovery-20261009-163705-current-wall-role';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-163705-current-physical-20261009'
GEOMETRY=HERE/'local/government-xl-terrain-recovery-163705-current-physical-20261009/runtime-geometry.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-163705-current-wall-context/diagnostic.json.gz'
PROVIDER=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-163705-provider-role'
LEASE='/tmp/xl-terrain-recovery-20261009-163705-current-role-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def recheck():
 physical=read(PHYSICAL/'result.json');assert read(PHYSICAL/'neon-sync.json')=={'jobId':physical['jobId'],'resultVerified':True}
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(physical['jobId'],)).fetchone()==('complete',physical)
 d=read(CONTEXT);role=read(PROVIDER/'expected-role.json');selected=read(PHYSICAL/'selection.json.gz');assert len(selected['rows'])==1;row=selected['rows'][0]
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==d['sourceSHA256']==role['sourceSHA256']==row['sourceSHA256'];binding=source_stream_binding(raw)
 assert binding==role['providerExteriorProvenanceBinding']['exactPackedSourceStreams']
 provenance=read(PROVIDER/'original-source-provenance.json');refs=provenance['evidenceRefs']+d['evidenceRefs']+physical['evidenceRefs']
 geometry=read(GEOMETRY);g=next(r for r in geometry['rows'] if r['uid']==role['uid']);tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
 area=(ground[:,1,0]-ground[:,0,0])*(ground[:,2,2]-ground[:,0,2])-(ground[:,2,0]-ground[:,0,0])*(ground[:,1,2]-ground[:,0,2]);ground=ground[np.abs(area)>2e-10]
 assert d['wholeSourceFaces']==len(tri)==11911 and d['affectedWallFaces']==role['wallFaces'] and d['wholeSourceUncoveredFaces']==0
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');current_manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(current_manifest.read_bytes());assert manifest_sha==selected['manifestSHA256']
 tile_hashes=neighbours['inputHashes'];forms={}
 for path,sha in tile_hashes.items():
  assert digest((ROOT/path).read_bytes())==sha
  forms.update({f['uid']:f for f in read(ROOT/path)['buildings']})
 for nr in neighbours['rows']:assert forms[nr['building']['uid']]==nr['building']
 assert set(neighbours['candidateIds'])=={role['uid']}
 # Independently scan every current native whole-source bound, including actors
 # whose current GIS footprint could miss a native overhang. Missing bounds reject.
 catalogue_hashes={};native_bounds=[];native_uids=set();touching=[];native_entries={}
 for url in read(current_manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogue_hashes[str(path.relative_to(ROOT))]=digest(path.read_bytes());refs.append(ref(path))
  for e in read(path)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all() and e['sha256']
   native_uids.add(e['uid']);native_entries[e['uid']]=(path,e);native_bounds.append({'uid':e['uid'],'catalogue':url,'sourceSHA256':e['sha256'],'originalWholeBounds':b.tolist()})
   if any(not(np.any(b[0]>f.max(axis=0)) or np.any(b[1]<f.min(axis=0))) for f in tri[role['wallFaces']]):touching.append(e['uid'])
 assert not touching,'Fresh native original bound touches wall: complete native export required'
 actors=[];actor_manifest=[]
 for nr in neighbours['rows']:
  form=nr['building'];uid=form['uid']
  if uid==role['uid']:continue
  assert not form.get('modelGeometry'),'Embedded actor export required'
  source={'currentFormSHA256':canonical_sha(form),'currentTileHashes':tile_hashes,'completeNeighbourInputs':ref(PHYSICAL/'neighbour-inputs.json.gz')}
  if uid in native_uids:
   catalogue,entry=native_entries[uid];asset_path=catalogue.parent/entry['asset'];proof=packed_world_bounds(asset_path.read_bytes())
   assert proof['sourceSHA256']==entry['sha256'] and proof['completeOriginalTriangles']==entry['triangles']
   assert np.max(np.abs(np.asarray(proof['originalWholeSourceBounds'])-np.asarray(entry['worldBounds'])))<.002
   source.update(originalNativeAsset=ref(asset_path),currentCatalogue=ref(catalogue),completeNativeNeighbourChecks=ref(PHYSICAL/'native-neighbour-checks.json'),completePackedWorldGeometryProof=proof);refs.append(ref(asset_path))
   actor={'uid':uid,'proofType':'complete-original-native-bounds','originalWholeSourceBounds':proof['originalWholeSourceBounds'],'currentSourceBinding':source};actors.append(actor)
   actor_manifest.append({'uid':uid,'proofType':actor['proofType'],'originalWholeSourceBoundsSHA256':canonical_sha(proof['originalWholeSourceBounds']),'currentSourceBinding':source})
  else:
   assert not nr['existingNative'],'Uncatalogued native actor'
   actor={'uid':uid,'proofType':'current-basic-full-footprint','originalCurrentRings':form['rings'],'currentSourceBinding':source};actors.append(actor)
   actor_manifest.append({'uid':uid,'proofType':actor['proofType'],'originalCurrentRingsSHA256':canonical_sha(form['rings']),'currentSourceBinding':source})
 boundary={'candidateUID':role['uid'],'ownedUIDs':[role['uid']],'currentScopeUIDs':sorted(nr['building']['uid'] for nr in neighbours['rows']),'manifestSHA256':manifest_sha,'currentFormInputHashes':tile_hashes,'nativeCatalogueInputHashes':catalogue_hashes,'allNativeOriginalBoundsSHA256':canonical_sha(native_bounds),'allNativeOriginalBoundsCount':len(native_bounds),'nativeOriginalBoundsTouchingCreditedWalls':touching,'currentPhysicalSelection':ref(PHYSICAL/'selection.json.gz'),'completeOriginalRuntimeGeometry':ref(GEOMETRY)}
 scope={'completeCurrentActorScope':True,'actors':actors,'expectedActorManifest':sorted(actor_manifest,key=lambda x:x['uid']),'currentGroupBoundaryBinding':boundary}
 binding.update(decodedWorldTrianglesSHA256=digest(tri.tobytes()),drawnGroundSHA256=digest(ground.tobytes()),continuousFaceContextsSHA256=canonical_sha(d['faces']),reviewedOriginalWallRoleSHA256=canonical_sha(role),currentForeignScopeSHA256=canonical_sha({k:scope[k] for k in ['completeCurrentActorScope','expectedActorManifest','currentGroupBoundaryBinding']}))
 typed=verify_wall_role(tri,ground,d['faces'],expected_binding=binding,current_binding=binding,expected_role=role,foreign_scope=scope)
 assert typed['verifiedWallRole'],typed['reasons']
 raw_reasons=physical['reasons'];eligible={'terrain-intersects-source-over-0.5m'}
 metrics=read(PHYSICAL/'metrics.json');foundation=read(PHYSICAL/'foundation.json');validation=read(PHYSICAL/'validation.json')
 spec=importlib.util.spec_from_file_location('wall_numeric_policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
 identity=read(PHYSICAL/'owned-source-identity.json');assert identity['passed']
 metric=metrics['rows'][0];f=foundation['rows'][0];v=validation['results'][0]
 assert metric['uid']==f['uid']==v['uid']==role['uid'] and metric['sourceSHA256']==f['sourceSHA256']==role['sourceSHA256']
 assert f['strictFoundationAccepted'] is True and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==len(tri)==11911
 assert f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
 numeric=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':role['sourceSHA256'],'identityProof':identity['proof']},metric,metrics['profiles']['mobile'])
 # A preserved cached stratified warning cannot override complete fresh source
 # evidence. It is resolved here only if not itself a fresh numeric failure,
 # all strict rim/sampler limits pass, all ordinary/upward faces remain strict,
 # and the only fresh clearance failures have this exact verified wall role.
 cached_warning='sampled-terrain-above-model-bottom'
 strict_rim=(metric['sourcePreserved'] is True and not metric['missingTerrain'] and metric['lowRimChecks']>0 and -.1<=metric['minLowGap']<=.1 and metric['maxLowGap']<=1 and metric['maxSamplerDelta']<=.004)
 cached_resolved=(cached_warning not in numeric and cached_warning in v.get('concerns',[]) and strict_rim and f['strictFoundationAccepted'] is True and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==len(tri) and f['foundation']['fullyBuriedUpwardTriangles']==0 and f['foundation']['fullyBuriedTriangles']==0)
 if cached_resolved:eligible.add(cached_warning)
 remaining=sorted(set(raw_reasons+numeric)-eligible)
 native=read(PHYSICAL/'native-neighbour-checks.json');assert not(set(native['blocked'])-set(native['resolved']))
 assert set(native['resolved'])=={'landsd/12851:0','landsd/12852:0','landsd/12854:0'} and all(r['passed'] for r in native['rows'])
 neighbour_checks=read(PHYSICAL/'neighbour-checks.json');assert len(neighbour_checks['rows'])==len(neighbours['rows']) and not any(r['reasons'] for r in neighbour_checks['rows'])
 assert validation['checksPassed']==1 and validation['loaderAccepted']==1 and not validation['exceptions']
 assert len(metrics['rows'])==1 and len(foundation['rows'])==1
 assert foundation['rows'][0]['foundation']['fullyBuriedTriangles']==0
 for report in [metrics,validation,read(PHYSICAL/'native-neighbour-checks.json')]:
  refs.extend({'path':p,'sha256':sha} for p,sha in (report.get('inputHashes') or report.get('hashes') or {}).items())
 paths=[Path(__file__),CONTEXT,GEOMETRY,PROVIDER/'expected-role.json',PROVIDER/'original-source-provenance.json',PHYSICAL/'result.json',PHYSICAL/'neighbour-inputs.json.gz',PHYSICAL/'selection.json.gz',PHYSICAL/'metrics.json',PHYSICAL/'foundation.json',PHYSICAL/'validation.json',PHYSICAL/'owned-source-identity.json',PHYSICAL/'neighbour-checks.json',PHYSICAL/'native-neighbour-checks.json',PHYSICAL/'neon-sync.json',asset,HERE/'unchanged_authored_crossing_wall_role_20261009.py',HERE/'test_unchanged_authored_crossing_wall_role_20261009.py',HERE/'unchanged_open_exterior_paths_v2_20261009.py',HERE/'unchanged_closed_column_role_v2_20261009.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'acceptance-policy.py',HERE/'exact_packed_world_bounds_20261009.py']
 refs.extend(ref(p) for p in paths);refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
 for item in refs:assert ref(ROOT/item['path'])==item,'Current replay binding changed: '+item['path']
 typed.update(uid=role['uid'],sourceSHA256=role['sourceSHA256'],evidenceRefs=refs,currentNeighbourFormsAccounted=len(neighbours['rows']),currentForeignBasicActors=sum(a['proofType']=='current-basic-full-footprint' for a in actors),currentForeignNativeActors=sum(a['proofType']=='complete-original-native-bounds' for a in actors),allCurrentNativeOriginalBoundsChecked=len(native_bounds),rawPhysicalReasons=raw_reasons,freshNumericReasons=numeric,cachedBottomWarningResolvedByCompleteTypedContext=cached_resolved,strictLowRimAndSamplerPass=strict_rim,typedWallOnlyResolvedReasons=[r for r in raw_reasons if r in eligible],unresolvedIndependentPhysicalReasons=remaining,independentPhysicalChecksPassed=not remaining,sourceEvidenceInterpretationUsedAI=True,modelGeometryAI=False,publication=False,installationApproved=False)
 return typed

def main():
 assert not DOC.exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok'];typed=recheck();save(DOC/'typed-role.json.gz',typed)
 stage='current-original-provider-exterior-wall-complete-foreign-role-v1';payload={'uid':typed['uid'],'sourceSHA256':typed['sourceSHA256'],'evidenceRefs':typed['evidenceRefs']};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'typedRole':ref(DOC/'typed-role.json.gz'),'verifiedWallRole':typed['verifiedWallRole'],'rawPhysicalReasons':typed['rawPhysicalReasons'],'unresolvedIndependentPhysicalReasons':typed['unresolvedIndependentPhysicalReasons'],'independentPhysicalChecksPassed':typed['independentPhysicalChecksPassed'],'humanStatus':'in-process' if typed['independentPhysicalChecksPassed'] else 'held-unknown','nextStep':'Complete staged and live browser checks plus guarded installer replay; source, wall context, native scope and all ordinary gates remain hash-bound.','newlyInstalled':0,'sourceGeometryChanges':0,'modelGeometryAI':False,'sourceEvidenceInterpretationUsedAI':True,'requiresAI':False,'requiresHumanDecision':False,'publication':False,'installationApproved':False}
 try:
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in typed['evidenceRefs']:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'verifiedWallRole':True,'independentPhysicalChecksPassed':typed['independentPhysicalChecksPassed'],'unresolved':typed['unresolvedIndependentPhysicalReasons']}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
