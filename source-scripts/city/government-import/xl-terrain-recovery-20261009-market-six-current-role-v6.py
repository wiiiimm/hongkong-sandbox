"""Current original assembly support, sole podium wall role and all independent gates."""
import json,importlib.util,subprocess,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from xl_source_stream_binding_20261009 import source_stream_binding
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from unchanged_authored_crossing_wall_role_20261009 import verify_wall_role
from original_wall_rim_accounting_20261009 import verify as verify_rim
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_20261009 import packed_world_bounds
BATCH='xl-terrain-recovery-20261009-market-six-current-role-v6';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009'
GEOMETRY=HERE/'local/government-xl-terrain-recovery-market-six-original-physical-v5-20261009/runtime-geometry.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-current-face-context-v6'
PROVIDER=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-provider-role-v6'
SUPPORT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-complete-support-accounting-v3'
SUPPORT_RECEIPT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-complete-support-checkpoint-v3'
LEASE='/tmp/xl-terrain-recovery-20261009-market-six-face-context-lease.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck():
 physical=read(PHYSICAL/'result.json');selected=read(PHYSICAL/'selection.json.gz');uidset={r['uid'] for r in selected['rows']};assert len(uidset)==6
 assert read(PHYSICAL/'neon-sync.json')=={'jobId':physical['jobId'],'resultVerified':True}
 support=read(SUPPORT/'diagnostic.json.gz');sr=read(SUPPORT_RECEIPT/'result.json');assert sr['supportAccountingAccepted'] and read(SUPPORT_RECEIPT/'neon-sync.json')=={'jobId':sr['jobId'],'resultVerified':True}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [physical,sr]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 # Replay source-bound composition, including every exact graph contact, actual
 # nonrendering clearance, full under-deck facet and rooted vertex attachments.
 spec=importlib.util.spec_from_file_location('current_assembly_support_v3',HERE/'xl-terrain-recovery-20261009-market-six-complete-support-accounting-v3.py');assembly=importlib.util.module_from_spec(spec);spec.loader.exec_module(assembly)
 from original_multi_actor_support_graph_20261009 import verify as verify_graph
 from original_nonrendering_component_accounting_20261009 import verify as verify_zero
 from exact_original_source_surface_contact_band_20261009 import verify_contact
 geometry=read(GEOMETRY);gs={r['uid']:r for r in geometry['rows']};meshes={u:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for u,g in gs.items()}
 original_graph=support['strictGroundRootedOriginalContactGraph'];gd=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-exact-assembly-support/diagnostic.json.gz');alltri=np.concatenate([meshes[a['uid']] for a in support['actors']])
 assert verify_graph(alltri,gd['actors'],gd['components'],gd['groundInterfaces'],gd['contactWitnesses'],expected_binding=gd['binding'],current_binding=gd['binding'])==original_graph
 assert verify_zero(alltri,[support['components'][72]],support['continuousOriginalNonrenderingContexts'],expected_binding=support['nonrenderingBinding'],current_binding=support['nonrenderingBinding'])==support['originalNonrenderingAccounting']
 membership={f:i for i,c in enumerate(gd['components']) for f in c['globalOriginalFaces']}
 for b in support['sourceSpecificUnderDeckFacetBands']:
  i=b['originalFace'];j=b['groundRootedOriginalSupportFace'];assert membership[j] in original_graph['resolvedOriginalComponents'];assert support['components'][membership[j]]['actorUID']==support['components'][membership[i]]['actorUID']=='landsd/313033:0'
  assert verify_contact(alltri[i],alltri[j:j+1],.1)==b['proof'] and b['proof']['verifiedCompleteFacetContactBand']
 for attachment in support['exactOriginalVertexAttachments']:
  i,j=attachment['originalFaces'];assert membership[j] in original_graph['resolvedOriginalComponents'] and support['components'][membership[i]]['actorUID']==support['components'][membership[j]]['actorUID']
  assert set(map(tuple,attachment['sharedUnchangedOriginalVertices']))==set(map(tuple,alltri[i]))&set(map(tuple,alltri[j]))
 assert set(support['resolvedOriginalComponents'])==set(range(84)) and len(alltri)==40100
 refs=physical['evidenceRefs']+support['evidenceRefs']+sr['evidenceRefs']+read(PROVIDER/'original-source-provenance.json')['evidenceRefs']
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);manifestsha=digest(manifest_path.read_bytes());assert manifestsha==selected['manifestSHA256']==support['manifestSHA256']
 contexts={}
 for row in selected['rows']:
  p=CONTEXT/(row['uid'].split('/')[1].replace(':','-'))/'diagnostic.json.gz';d=read(p);refs+=d['evidenceRefs']+[ref(p)];contexts[row['uid']]=d
  assert d['sourceSHA256']==row['sourceSHA256'] and d['wholeSourceFaces']==len(meshes[row['uid']]) and d['wholeSourceUncoveredFaces']==0 and not d['otherAffectedFaces']
  if row['uid']!='landsd/313033:0':assert not d['continuousAffectedFaces'],'Other original source has unresolved ordinary continuous burial'
 role=read(PROVIDER/'expected-role.json');uid=role['uid'];assert uid=='landsd/313033:0';d=contexts[uid];tri=meshes[uid];assert d['affectedWallFaces']==role['wallFaces'] and len(tri)==18265
 row=next(r for r in selected['rows'] if r['uid']==uid);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();binding=source_stream_binding(raw);assert digest(raw)==role['sourceSHA256'] and binding==role['providerExteriorProvenanceBinding']['exactPackedSourceStreams']
 ground=np.asarray(gs[uid]['drawnGroundGeometry'],float).reshape(-1,3,3);xz=ground[:,:,[0,2]];area=(xz[:,1,0]-xz[:,0,0])*(xz[:,2,1]-xz[:,0,1])-(xz[:,2,0]-xz[:,0,0])*(xz[:,1,1]-xz[:,0,1]);ground=ground[np.abs(area)>2e-10]
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');tile_hashes=neighbours['inputHashes'];forms={}
 for p,sha in tile_hashes.items():assert digest((ROOT/p).read_bytes())==sha;forms.update({f['uid']:f for f in read(ROOT/p)['buildings']})
 for nr in neighbours['rows']:assert forms[nr['building']['uid']]==nr['building']
 assert set(neighbours['candidateIds'])==uidset
 catalogue_hashes={};entries={};native_bounds=[];touching=[]
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogue_hashes[str(path.relative_to(ROOT))]=digest(path.read_bytes());refs.append(ref(path))
  for e in read(path)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all();entries[e['uid']]=(path,e)
   native_bounds.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],originalWholeBounds=b.tolist()))
   if any(not(np.any(b[0]>f.max(axis=0)) or np.any(b[1]<f.min(axis=0))) for f in tri[role['wallFaces']]):touching.append(e['uid'])
 actor_forms={nr['building']['uid']:nr for nr in neighbours['rows']};scope_uids=set(actor_forms)|set(touching);actors=[];actor_manifest=[]
 for other in sorted(scope_uids-{uid}):
  form=forms.get(other);source=dict(currentFormSHA256=canonical_sha(form) if form else None,currentTileHashes=tile_hashes,completeNeighbourInputs=ref(PHYSICAL/'neighbour-inputs.json.gz'))
  if other in uidset:
   rr=next(r for r in selected['rows'] if r['uid']==other);source.update(originalCandidateAsset=ref(ROOT/rr['candidate']['path']),currentIndependentIdentity=ref(PHYSICAL/'owned-source-identity.json'),completeRuntimeGeometry=ref(GEOMETRY));refs.append(ref(ROOT/rr['candidate']['path']))
   actor=dict(uid=other,proofType='exact-world-triangles',worldTriangles=meshes[other].tolist(),currentSourceBinding=source)
  elif other in entries:
   catalogue,e=entries[other];path=catalogue.parent/e['asset'];data=path.read_bytes();proof=packed_world_bounds(data);assert proof['sourceSHA256']==e['sha256'];source.update(originalNativeAsset=ref(path),currentCatalogue=ref(catalogue),completeNativeNeighbourChecks=ref(PHYSICAL/'native-neighbour-checks.json'));refs.append(ref(path))
   if other in touching:actor=dict(uid=other,proofType='exact-world-triangles',worldTriangles=decode_original_world_triangles(data).tolist(),currentSourceBinding=source)
   else:actor=dict(uid=other,proofType='complete-original-native-bounds',originalWholeSourceBounds=proof['originalWholeSourceBounds'],currentSourceBinding=source)
  else:
   assert form and not actor_forms[other]['existingNative'] and not form.get('modelGeometry')
   actor=dict(uid=other,proofType='current-basic-full-footprint',originalCurrentRings=form['rings'],currentSourceBinding=source)
  actors.append(actor);record=dict(uid=other,proofType=actor['proofType'],currentSourceBinding=source)
  if actor['proofType']=='exact-world-triangles':record['worldTrianglesSHA256']=digest(np.asarray(actor['worldTriangles'],float).tobytes())
  elif actor['proofType']=='complete-original-native-bounds':record['originalWholeSourceBoundsSHA256']=canonical_sha(actor['originalWholeSourceBounds'])
  else:record['originalCurrentRingsSHA256']=canonical_sha(actor['originalCurrentRings'])
  actor_manifest.append(record)
 boundary=dict(candidateUID=uid,ownedUIDs=[uid],currentScopeUIDs=sorted(scope_uids),manifestSHA256=manifestsha,currentFormInputHashes=tile_hashes,nativeCatalogueInputHashes=catalogue_hashes,allNativeOriginalBoundsSHA256=canonical_sha(native_bounds),allNativeOriginalBoundsCount=len(native_bounds),nativeOriginalBoundsTouchingCreditedWalls=touching,currentPhysicalSelection=ref(PHYSICAL/'selection.json.gz'),completeOriginalRuntimeGeometry=ref(GEOMETRY))
 scope=dict(completeCurrentActorScope=True,actors=actors,expectedActorManifest=actor_manifest,currentGroupBoundaryBinding=boundary)
 binding.update(decodedWorldTrianglesSHA256=digest(tri.tobytes()),drawnGroundSHA256=digest(ground.tobytes()),continuousFaceContextsSHA256=canonical_sha(d['faces']),reviewedOriginalWallRoleSHA256=canonical_sha(role),currentForeignScopeSHA256=canonical_sha({k:scope[k] for k in ['completeCurrentActorScope','expectedActorManifest','currentGroupBoundaryBinding']}))
 typed=verify_wall_role(tri,ground,d['faces'],expected_binding=binding,current_binding=binding,expected_role=role,foreign_scope=scope);assert typed['verifiedWallRole'],typed['reasons']
 metrics=read(PHYSICAL/'metrics.json');foundation=read(PHYSICAL/'foundation.json');validation=read(PHYSICAL/'validation.json');identities=read(PHYSICAL/'owned-source-identity.json')['rows']
 assert len(metrics['rows'])==len(foundation['rows'])==len(identities)==6 and all(r['passed'] for r in identities)
 for f in foundation['rows']:assert f['strictFoundationAccepted'] and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==len(meshes[f['uid']]) and f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
 assert validation['checksPassed']==validation['loaderAccepted']==6 and not validation['exceptions']
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==len(neighbours['rows'])==42 and not any(r['reasons'] for r in checks['rows'])
 native=read(PHYSICAL/'native-neighbour-checks.json');assert not(set(native['blocked'])-set(native['resolved'])) and all(r['passed'] for r in native['rows'])
 rimpath=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-podium-rim-attribution-v6/diagnostic.json';rimraw=json.loads(subprocess.check_output(['node',str(HERE/'xl-terrain-recovery-20261009-market-six-podium-rim-attribution-v6.mjs'),'--recheck'],cwd=ROOT,text=True));assert rimraw==read(rimpath)
 metric=next(r for r in metrics['rows'] if r['uid']==uid);rim=verify_rim(gs[uid]['position'],gs[uid]['index'],float(tri[:,:,1].min()),rimraw['allSamples'],wall_faces=role['wallFaces'],verified_wall_role=typed['verifiedWallRole'],expected_metric=metric)
 spec=importlib.util.spec_from_file_location('market_current_numeric_policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);resolved=[];remaining=[]
 for r in metrics['rows']:
  u=r['uid'];assert r['sourcePreserved'] and not r['missingTerrain'] and r['maxSamplerDelta']<=.004
  identity=next(i for i in identities if i['uid']==u);numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=r['sourceSHA256'],identityProof=identity['proof']),r,metrics['profiles']['mobile'])
  eligible={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom'} if u!=uid else {'terrain-intersects-source-over-0.5m','sampled-terrain-above-model-bottom'}
  ownraw=[x.split(':0:',1)[1] for x in physical['reasons'] if x.startswith(u+':')];allreasons=set(numeric+ownraw);remaining.extend(u+':'+x for x in sorted(allreasons-eligible));resolved.append(dict(uid=u,freshNumericReasons=numeric,rawPhysicalReasons=ownraw,sourceBoundResolvedReasons=sorted(allreasons&eligible)))
 remaining.extend(x for x in physical['reasons'] if not any(x.startswith(u+':') for u in uidset))
 refs+=rimraw['evidenceRefs']+[ref(rimpath)]+[ref(p) for p in [Path(__file__),SUPPORT/'diagnostic.json.gz',SUPPORT_RECEIPT/'result.json',SUPPORT_RECEIPT/'neon-sync.json',GEOMETRY,PROVIDER/'expected-role.json',PROVIDER/'original-source-provenance.json',HERE/'unchanged_authored_crossing_wall_role_20261009.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_packed_world_bounds_20261009.py',HERE/'acceptance-policy.py']]
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']);assert all(ref(ROOT/r['path'])==r for r in refs)
 return dict(uids=sorted(uidset),manifestSHA256=manifestsha,verifiedPodiumWallRole=typed,completeOriginalAssemblySupport=ref(SUPPORT/'diagnostic.json.gz'),originalPodiumRimAccounting=rim,sourceDecisions=resolved,unresolvedIndependentPhysicalReasons=sorted(set(remaining)),independentPhysicalChecksPassed=not remaining,evidenceRefs=refs,currentNeighbourFormsAccounted=42,completeOriginalFaces=40100,completeOriginalComponents=84,sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Every original actor/source remains independent. Complete assembly support replaces only ground-to-elevated-original proxy flags; sole17 original podium crossing walls have separately verified source/current foreign roles. Whole foundations, every ordinary/upward face, sampler/runtime limits and42basic/two existingnative neighbours remain strict. Browser/publication still mandatory.')
def main():
 assert not DOC.exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok'];typed=recheck();save(DOC/'typed-role.json.gz',typed)
 stage='complete-current-original-six-actor-support-and-podium-role-v1';payload=dict(uids=typed['uids'],evidenceRefs=typed['evidenceRefs']);jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result=dict(**payload,jobId=jid,batch=BATCH,typedRole=ref(DOC/'typed-role.json.gz'),independentPhysicalChecksPassed=typed['independentPhysicalChecksPassed'],unresolvedIndependentPhysicalReasons=typed['unresolvedIndependentPhysicalReasons'],newlyInstalled=0,publication=False,sourceGeometryChanges=0)
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for r in typed['evidenceRefs']:assert ref(ROOT/r['path'])==r
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True));print(json.dumps(dict(jobId=jid,independentPhysicalChecksPassed=typed['independentPhysicalChecksPassed'],unresolved=typed['unresolvedIndependentPhysicalReasons'])),flush=True)
if __name__=='__main__':main()
