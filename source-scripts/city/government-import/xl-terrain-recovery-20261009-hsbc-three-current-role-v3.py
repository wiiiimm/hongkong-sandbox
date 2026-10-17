"""Complete current unchanged HSBC originals, strict support plus mounted panel."""
import json,importlib.util,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
from hsbc_mounted_visual_panel_accounting_v2_20261009 import verify as verify_panel,canonical_sha
from original_ordinary_ground_root_graph_20261009 import verify as verify_graph
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_20261009 import packed_world_bounds
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='xl-terrain-recovery-20261009-hsbc-three-current-role-v3';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-hsbc-three-retained-physical-v1-20261009'
SUPPORT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-hsbc-three-current-ordinary-support-v1'
PROVIDER=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-hsbc-three-provider-panel-v1'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
UIDS=['landsd/265848:0','landsd/337075:0','landsd/337079:0']
CONTEXTS={UIDS[0]:'xl-terrain-recovery-20261009-265848-three-current-complete-context-v2',UIDS[1]:'xl-terrain-recovery-20261009-337075-current-complete-context-v1',UIDS[2]:'xl-terrain-recovery-20261009-337079-current-complete-context-v1'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def normalized(d):return json.loads(json.dumps(d))
def recheck():
 physical=read(PHYSICAL/'result.json');support=read(SUPPORT/'diagnostic.json.gz');sr=read(SUPPORT/'result.json');selected=read(PHYSICAL/'selection.json.gz');rows=selected['rows'];assert [r['uid'] for r in rows]==UIDS
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for doc,r in [(PHYSICAL,physical),(SUPPORT,sr)]:
   assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for r in rows:assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
 geometry=read(GEOMETRY);gs={g['uid']:g for g in geometry['rows']};assert set(gs)==set(UIDS)
 for p,sha in geometry['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha,'Changed current numeric input:'+p
 refs=physical['evidenceRefs']+support['evidenceRefs']+read(PROVIDER/'original-source-provenance.json')['evidenceRefs'];meshes={};indexed=[];streams={};contexts={}
 for r in rows:
  u=r['uid'];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256']==gs[u]['sourceSHA256'];stream=source_stream_binding(raw);streams[u]=stream
  g=gs[u];positions=np.asarray(g['position'],float).reshape(-1,3);indices=np.asarray(g['index'],np.uint32).reshape(-1,3);tri=positions[indices];decoded=decode_original_world_triangles(raw);assert decoded.shape==tri.shape and np.max(np.abs(decoded-tri))<=1e-9
  meshes[u]=tri;indexed.append(dict(uid=u,sourceSHA256=r['sourceSHA256'],position=positions.reshape(-1).tolist(),index=indices.reshape(-1).tolist()))
  p=ROOT/'docs/astra-city/government-import'/CONTEXTS[u]/'diagnostic.json.gz';d=read(p);contexts[u]=d;refs+=d['evidenceRefs']+[ref(p)]
  assert d['sourceSHA256']==r['sourceSHA256'] and d['wholeSourceFaces']==len(tri) and d['wholeSourceUncoveredFaces']==0 and not d['continuousAffectedFaces']
  assert len(d['faces'])==len(tri) and [f['sourceFace'] for f in d['faces']]==list(range(len(tri)))
  assert all(f['groundProjectionCovered'] and f['minimum'] and f['minimum']['minimumGapM']>=-.5 for f in d['faces'])
  ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);xz=ground[:,:,[0,2]];area=(xz[:,1,0]-xz[:,0,0])*(xz[:,2,1]-xz[:,0,1])-(xz[:,2,0]-xz[:,0,0])*(xz[:,1,1]-xz[:,0,1]);ground=ground[np.abs(area)>2e-10]
  assert d['originalOpenExteriorPaths']['sourceAndPhysicalBindings']['drawnGroundSHA256']==digest(ground.tobytes())
 alltri=np.concatenate([meshes[u] for u in UIDS]);ground=np.unique(np.concatenate([np.asarray(gs[u]['drawnGroundGeometry'],float).reshape(-1,3,3) for u in UIDS]).reshape(-1,9),axis=0).reshape(-1,3,3)
 graph_binding=dict(completeOriginalWorldTrianglesSHA256=digest(alltri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=digest(GEOMETRY.read_bytes()),supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical_sha(indexed));assert graph_binding==support['binding']
 graph=normalized(verify_graph(alltri,support['actors'],support['components'],support['contactWitnesses'],indexed,ground,expected_binding=graph_binding,current_binding=graph_binding))
 assert all(graph[k]==support[k] for k in graph),'Saved original graph differs from independent replay'
 graph.update(components=support['components'],contactWitnesses=support['contactWitnesses'])
 role=read(PROVIDER/'expected-role.json');assert role['uid']==UIDS[0] and role['sourceSHA256']==rows[0]['sourceSHA256'] and role['originalFaces']==list(range(10036,10041)) and role['component']==29
 assert role['providerRootStreams']==streams[UIDS[0]] and role['completePodiumOriginalWorldTrianglesSHA256']==digest(meshes[UIDS[0]].tobytes())
 assert role['strictIndependentSupport']==ref(SUPPORT/'diagnostic.json.gz') and role['currentWholeFacetContext']==ref(ROOT/'docs/astra-city/government-import'/CONTEXTS[UIDS[0]]/'diagnostic.json.gz')
 assert support['actors'][0]['globalFaceRange']==[0,15336] and support['actors'][0]['uid']==UIDS[0] and len(alltri)==27904
 actualroundoff=float(np.max(np.abs(decode_original_world_triangles((ROOT/rows[0]['candidate']['path']).read_bytes())-meshes[UIDS[0]])));assert actualroundoff==role['independentlyVerifiedPackedWorldRoundoffM']
 panel=meshes[UIDS[0]][role['originalFaces']];projection=unary_union([Polygon(f[:,[0,2]]) if Polygon(f[:,[0,2]]).area>0 else LineString(f[:,[0,2]]) if len(set(map(tuple,f[:,[0,2]])))>1 else Point(f[0,[0,2]]) for f in panel])
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');forms={}
 for p,sha in neighbours['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha;forms.update({f['uid']:f for f in read(ROOT/p)['buildings']})
 for r in neighbours['rows']:assert forms[r['building']['uid']]==r['building']
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);assert digest(manifestpath.read_bytes())==selected['manifestSHA256'];entries={};cataloguehashes={};allbounds=[];touching=[]
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(ref(path));cataloguehashes[str(path.relative_to(ROOT))]=digest(path.read_bytes())
  for e in read(path)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all();entries[e['uid']]=(path,e);allbounds.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],bounds=b.tolist()))
   if any(np.all(b[1]>=f.min(axis=0)) and np.all(b[0]<=f.max(axis=0)) for f in panel):touching.append(e['uid'])
 scopeuids=sorted(({r['building']['uid'] for r in neighbours['rows']}|set(touching))-set(UIDS));separations=[]
 for u in scopeuids:
  if u in entries:
   catalogue,e=entries[u];asset=catalogue.parent/e['asset'];raw=asset.read_bytes();b=packed_world_bounds(raw);assert digest(raw)==e['sha256'];refs.append(ref(asset))
   if all(np.any(np.asarray(b['originalWholeSourceBounds'])[0]>f.max(axis=0)) or np.any(np.asarray(b['originalWholeSourceBounds'])[1]<f.min(axis=0)) for f in panel):mode='complete-original-native-bounds'
   else:
    mesh=decode_original_world_triangles(raw);lo=mesh.min(axis=1);hi=mesh.max(axis=1)
    for f in panel:
     for j in np.flatnonzero(np.all(hi>=f.min(axis=0),axis=1)&np.all(lo<=f.max(axis=0),axis=1)):assert not intersection_points(rational_face(f),rational_face(mesh[j])),'Panel intersects foreign original native'
    mode='complete-exact-original-native-triangles'
   separations.append(dict(uid=u,mode=mode,source=ref(asset),catalogue=ref(catalogue),wholeBoundsSHA256=canonical_sha(b['originalWholeSourceBounds'])))
  else:
   form=forms[u];assert not form.get('modelGeometry');p=Polygon(form['rings'][0],form['rings'][1:]);assert p.is_valid and p.area>0 and p.disjoint(projection),'Panel intersects foreign current basic footprint'
   separations.append(dict(uid=u,mode='complete-current-basic-footprint',formSHA256=canonical_sha(form),projectionDistanceM=p.distance(projection)))
 for u in UIDS[1:]:
  mesh=meshes[u];lo=mesh.min(axis=1);hi=mesh.max(axis=1)
  for f in panel:
   for j in np.flatnonzero(np.all(hi>=f.min(axis=0),axis=1)&np.all(lo<=f.max(axis=0),axis=1)):assert not intersection_points(rational_face(f),rational_face(mesh[j])),'Panel intersects another owned actor'
 foreign=dict(completeCurrentActorScope=True,currentForeignUIDs=scopeuids,currentOwnedUIDs=UIDS,currentTileHashes=neighbours['inputHashes'],nativeCatalogueHashes=cataloguehashes,allNativeWholeBoundsSHA256=canonical_sha(allbounds),nativeTouchingPanel=sorted(touching),strictSeparations=separations,completePhysicalInputs=ref(PHYSICAL/'neighbour-inputs.json.gz'),manifestSHA256=selected['manifestSHA256'])
 panelcontexts=[contexts[UIDS[0]]['faces'][i] for i in role['originalFaces']]
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(alltri.tobytes()),strictGraphSHA256=canonical_sha(graph),continuousContextsSHA256=canonical_sha(panelcontexts),frozenRoleSHA256=canonical_sha(role),providerRootStreamsSHA256=canonical_sha(streams[UIDS[0]]),fullCurrentPhysicalSHA256=digest((PHYSICAL/'result.json').read_bytes()),fullCurrentForeignScopeSHA256=canonical_sha(foreign))
 mounted=verify_panel(alltri,panelcontexts,graph,expected_role=role,expected_binding=binding,current_binding=binding);assert mounted['visualPanelAccounted']
 metrics=read(PHYSICAL/'metrics.json');foundation=read(PHYSICAL/'foundation.json');validation=read(PHYSICAL/'validation.json');identities=read(PHYSICAL/'owned-source-identity.json')['rows'];assert len(metrics['rows'])==len(foundation['rows'])==len(identities)==3 and all(r['passed'] for r in identities)
 for f in foundation['rows']:assert f['strictFoundationAccepted'] and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==len(meshes[f['uid']]) and f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
 assert validation['checksPassed']==validation['loaderAccepted']==3 and not validation['exceptions']
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==len(neighbours['rows'])==77 and not any(r['reasons'] for r in checks['rows'])
 native=read(PHYSICAL/'native-neighbour-checks.json');assert {r['uid'] for r in native['rows']}=={'landsd/227099:0','landsd/229310:0'} and all(r['passed'] for r in native['rows']) and not(set(native['blocked'])-set(native['resolved']))
 spec=importlib.util.spec_from_file_location('hsbc_numeric',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);resolved=[];remaining=[]
 for m in metrics['rows']:
  u=m['uid'];assert m['sourcePreserved'] and not m['missingTerrain'] and m['maxSamplerDelta']<=.004;identity=next(i for i in identities if i['uid']==u)
  numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=m['sourceSHA256'],identityProof=identity['proof']),m,metrics['profiles']['mobile']);raw=[x[len(u)+1:] for x in physical['reasons'] if x.startswith(u+':')]
  eligible={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom'} if u!=UIDS[0] else set();allreasons=set(numeric+raw);remaining.extend(u+':'+x for x in sorted(allreasons-eligible));resolved.append(dict(uid=u,freshNumericReasons=numeric,rawPhysicalReasons=raw,sourceBoundResolvedReasons=sorted(allreasons&eligible)))
 remaining.extend(x for x in physical['reasons'] if not any(x.startswith(u+':') for u in UIDS))
 refs+=[ref(p) for p in [Path(__file__),PHYSICAL/'result.json',PHYSICAL/'neon-sync.json',SUPPORT/'diagnostic.json.gz',SUPPORT/'result.json',SUPPORT/'neon-sync.json',GEOMETRY,PROVIDER/'expected-role.json',PROVIDER/'original-source-provenance.json',HERE/'hsbc_mounted_visual_panel_accounting_v2_20261009.py',HERE/'test_hsbc_mounted_visual_panel_accounting_v3_20261009.py',HERE/'acceptance-policy.py',HERE/'exact_packed_world_bounds_20261009.py']]
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']);assert all(ref(ROOT/r['path'])==r for r in refs)
 return normalized(dict(uids=UIDS,manifestSHA256=selected['manifestSHA256'],verifiedMountedVisualPanel=mounted,completeOriginalSupportGraph=graph,completeCurrentForeignScope=foreign,completeCurrentIdentities=identities,sourceDecisions=resolved,unresolvedIndependentPhysicalReasons=sorted(set(remaining)),independentPhysicalChecksPassed=not remaining,evidenceRefs=refs,currentNeighbourFormsAccounted=77,completeOriginalFaces=27904,completeOriginalComponents=62,sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Named mounted visual panel only; no added load-bearing edges/root credit. Every other component roots independently through actual ordinary anchors and107 original positive-dimensional contacts. Every original facet retains strict ordinary clearance, whole foundation,77current forms/two retained native/runtime checks. Browser/publication still mandatory.'))
def main():
 assert not DOC.exists();claim=reservations.claim('hsbc-complete-current-role-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=json.loads(json.dumps(claim['reservation'],default=str))
 try:
  typed=recheck();save(DOC/'typed-role.json.gz',typed);stage='source-specific-current-hsbc-mounted-panel-and-complete-support-v1';payload=dict(uids=UIDS,evidenceRefs=typed['evidenceRefs']);jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result=dict(**payload,jobId=jid,batch=BATCH,typedRole=ref(DOC/'typed-role.json.gz'),independentPhysicalChecksPassed=typed['independentPhysicalChecksPassed'],unresolvedIndependentPhysicalReasons=typed['unresolvedIndependentPhysicalReasons'],newlyInstalled=0,publication=False,sourceGeometryChanges=0)
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for r in typed['evidenceRefs']:assert ref(ROOT/r['path'])==r
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True));print(json.dumps(dict(jobId=jid,independentPhysicalChecksPassed=typed['independentPhysicalChecksPassed'],unresolved=typed['unresolvedIndependentPhysicalReasons'])),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
