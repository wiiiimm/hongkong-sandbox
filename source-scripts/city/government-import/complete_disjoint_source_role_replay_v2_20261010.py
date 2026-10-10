"""Read-only replay of a fenced full source role after a disjoint global publish.

Only exact old-manifest references resolve to the separately byte-pinned archive.
Every numerical/source/ground/kernel reference remains a current byte check.
Existing numerical acceptance is reused, never newly inferred or recomputed.
"""
from pathlib import Path
import json,importlib.util,numpy as np
from run import ROOT,HERE,read,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from verified_disjoint_manifest_rebind_20261009 import verify,disjoint
from original_literal_rebound_role_accounting_20261010 import account
MANIFEST='3d-viewer/city/data/manifest.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def module(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def recheck(*,physical,context_path,old_role_folder,old_role_sha,rebind_folder,owned_sources,retained_sources):
 physical=Path(physical);rebind_folder=Path(rebind_folder);old_role_folder=Path(old_role_folder)
 manifest=ROOT/MANIFEST;start=ref(manifest);archive=rebind_folder/'historical-manifest.json';oldraw=archive.read_bytes();oldsha=digest(oldraw);old=json.loads(oldraw);current=read(manifest)
 proofs=[]
 def pin(item):
  path=ROOT/item['path'];assert path.resolve().is_relative_to(ROOT)
  if item['path']==MANIFEST and item['sha256']==oldsha:assert digest(archive.read_bytes())==oldsha;return
  assert ref(path)==item,'Changed numerical/source/ground/kernel input: '+item['path']
 def receipt(folder):
  result=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  for item in result['evidenceRefs']:pin(item)
  proofs.append(ref(folder/'result.json'));return result
 priorreceipt=receipt(old_role_folder);regionalreceipt=receipt(rebind_folder)
 rolepath=old_role_folder/'typed-role.json.gz';assert ref(rolepath)['sha256']==old_role_sha
 role=read(rolepath);regional=read(rebind_folder/'diagnostic.json.gz');assert role['currentManifest']==dict(path=MANIFEST,sha256=oldsha)
 for item in role['evidenceRefs']:pin(item)
 for item in regional['evidenceRefs']:pin(item)
 assert priorreceipt['currentTypedPhysicalAccepted']is True and priorreceipt['typedRole']==ref(rolepath)
 assert regionalreceipt['rebindPassed']is True and regionalreceipt['currentManifestSHA256']==start['sha256']
 assert regional['oldManifestSHA256']==oldsha and regional['currentManifestSHA256']==start['sha256'] and regional['verifiedDisjointGlobalManifestRebind']is True
 geometry=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(geometry);selection=read(physical/'selection.json.gz');neighbours=read(physical/'neighbour-inputs.json.gz');candidates=read(physical/'terrain-candidates.json')
 assert selection['manifestSHA256']==oldsha and {r['uid']:r['sourceSHA256']for r in selection['rows']}==owned_sources
 assert [r['uid']for r in runtime['rows']]==[r['uid']for r in selection['rows']]
 hashes={p:digest((ROOT/p).read_bytes())for p in runtime['inputHashes']};assert runtime['inputHashes']==regional['completeOldInputHashes'] and hashes==regional['completeCurrentOldInputHashes']
 refs=[ref(Path(__file__)),ref(HERE/'original_literal_rebound_role_accounting_20261010.py'),ref(HERE/'verified_disjoint_manifest_rebind_20261009.py'),ref(archive),start,ref(rolepath),ref(geometry),ref(context_path),*proofs]
 # The complete closure was independently captured before production import.
 def bound_snapshot(path):
  snap=read(path);assert snap['acceptance']is False and snap['geometryChanges']==0 and snap['manifest']==start
  closure=snap['productionModuleClosure'];assert closure['completeAuditedLiteralImportClosure']is True and closure['unsupportedDynamicImports']==0
  assert len(closure['modules'])==len(closure['inputHashes']) and set(closure['inputHashes']).issubset(snap['inputHashes'])
  for p,sha in snap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha;refs.append(dict(path=p,sha256=sha))
  assert all(snap['inputHashes'][p]==sha for p,sha in closure['inputHashes'].items());refs.append(ref(path));return snap
 native_snapshot=bound_snapshot(rebind_folder/'protected-retained-native-bounds.json');assert {r['uid']:r['sourceSHA256']for r in native_snapshot['rows']}==retained_sources
 arrays=[];scope=[]
 for row,rt in zip(selection['rows'],runtime['rows']):
  source=ROOT/row['candidate']['path'];proof=packed_world_bounds(source.read_bytes());entry=row['candidate']['entry'];assert proof['sourceSHA256']==owned_sources[row['uid']]==entry['sha256'] and proof['completeOriginalTriangles']==entry['triangles']
  pos=np.asarray(rt['position'],float).reshape(-1,3);index=np.asarray(rt['index']);assert len(pos)==entry['indexedVertices'] and len(index)==entry['triangles']*3 and np.isfinite(pos).all()
  cast=pos.astype(np.float32).astype(float);assert np.isfinite(cast).all();bounds=[proof['originalWholeSourceBounds'],[pos.min(0).tolist(),pos.max(0).tolist()],[cast.min(0).tolist(),cast.max(0).tolist()]];arrays.extend(np.asarray(b,float)for b in bounds)
  scope.append(dict(kind='owned',uid=row['uid'],sourceSHA256=entry['sha256'],completeOriginalLiteralAndFloat32Bounds=bounds,allOriginalVerticesAccounted=True));refs.append(ref(source))
 def inventory(m):
  out={}
  for url in m['officialModelCatalogues']:
   catalogue=ROOT/'3d-viewer'/url;refs.append(ref(catalogue))
   for e in read(catalogue)['models']:assert e['uid']not in out;out[e['uid']]=dict(entry=e,catalogue=url)
  return out
 a,b=inventory(old),inventory(current);assert not set(owned_sources)&set(b)
 for literal in native_snapshot['rows']:
  e=a[literal['uid']]['entry'];assert a[literal['uid']]==b[literal['uid']] and e==literal['rawCurrentEntry'] and e['sha256']==retained_sources[literal['uid']]
  source=(ROOT/'3d-viewer'/a[literal['uid']]['catalogue']).parent/e['asset'];proof=packed_world_bounds(source.read_bytes());assert proof['sourceSHA256']==e['sha256'] and proof['completeOriginalTriangles']==literal['completeOriginalTriangles']==e['triangles']
  bounds=[proof['originalWholeSourceBounds'],literal['completeLiteralWorldBounds'],literal['completeFloat32CastWorldBounds']];arrays.extend(np.asarray(v,float)for v in bounds);scope.append(dict(kind='retained-native',uid=literal['uid'],sourceSHA256=e['sha256'],completeOriginalLiteralAndFloat32Bounds=bounds,allOriginalVerticesAccounted=True));refs.append(ref(source))
 joined=np.concatenate(arrays);region=[float(joined[:,0].min()),float(joined[:,2].min()),float(joined[:,0].max()),float(joined[:,2].max())]
 if candidates:
  assert len(candidates)==1;cb=candidates[0]['bounds'];region=[min(region[0],cb[0]),min(region[1],cb[1]),max(region[2],cb[2]),max(region[3],cb[3])]
 for r in neighbours['rows']:
  points=np.asarray([p for ring in r['building']['rings']for p in ring],float);assert np.isfinite(points).all();region=[min(region[0],float(points[:,0].min())),min(region[1],float(points[:,1].min())),max(region[2],float(points[:,0].max())),max(region[3],float(points[:,1].max()))]
 assert scope==regional['completeProtectedOriginalLiteralFloat32Scope'] and region==regional['completeFrozenRegionWorldXZBounds']
 changed=sorted(uid for uid in set(a)|set(b)if a.get(uid)!=b.get(uid));literal={}
 for label,entries in [('old',a),('current',b)]:
  uids=[uid for uid in changed if uid in entries]
  if not uids:continue
  snap=bound_snapshot(rebind_folder/('changed-'+label+'-actor-bounds.json'));assert [r['uid']for r in snap['rows']]==uids
  for row in snap['rows']:literal[(label,row['uid'])]=row
 native_before=[];native_after=[]
 for uid in sorted(set(a)|set(b)):
  for label,entries,out in [('old',a,native_before),('current',b,native_after)]:
   if uid not in entries:continue
   bounds=None;e=entries[uid]['entry']
   if uid in changed:
    measured=literal[(label,uid)];assert measured['rawCurrentEntry']==e and measured['sourceSHA256']==e['sha256'] and measured['completeOriginalTriangles']==e['triangles'] and measured['completeIndexedVertices']==e['indexedVertices'] and measured['allOriginalVerticesIncluded']is True
    source=(ROOT/'3d-viewer'/entries[uid]['catalogue']).parent/e['asset'];proof=packed_world_bounds(source.read_bytes());assert proof['sourceSHA256']==e['sha256'];bb=np.asarray([proof['originalWholeSourceBounds'],measured['completeLiteralWorldBounds'],measured['completeFloat32CastWorldBounds']],float);bounds=[float(bb[:,0,0].min()),float(bb[:,0,2].min()),float(bb[:,1,0].max()),float(bb[:,1,2].max())];refs.append(ref(source))
   out.append(dict(id=uid,sourceBinding=entries[uid],completeWorldXZBounds=bounds))
 def terrain_inventory(m):return {p['url']:p for p in m['terrainPatches']}
 ta,tb=terrain_inventory(old),terrain_inventory(current);assert len(ta)==len(old['terrainPatches']) and len(tb)==len(current['terrainPatches']);before=[];after=[]
 def patch_bounds(p):
  g=p['meta']['georef'];xs=[g['bE']-834500,g['bE']+(p['w']-1)*g['aE']-834500];zs=[816500-g['bN'],816500-g['bN']-(p['h']-1)*g['aN']];xs+=list(map(float,np.asarray(xs,np.float32)));zs+=list(map(float,np.asarray(zs,np.float32)));bounds=[min(xs),min(zs),max(xs),max(zs)]
  if p.get('nativeMesh'):
   pos=np.asarray(p['nativeMesh']['position'],float).reshape(-1,3);pos=np.concatenate([pos,pos.astype(np.float32).astype(float)]);assert len(pos) and np.isfinite(pos).all();bounds=[min(bounds[0],float(pos[:,0].min())),min(bounds[1],float(pos[:,2].min())),max(bounds[2],float(pos[:,0].max())),max(bounds[3],float(pos[:,2].max()))]
  for child in p.get('patches',[]):
   cb=patch_bounds(child);bounds=[min(bounds[0],cb[0]),min(bounds[1],cb[1]),max(bounds[2],cb[2]),max(bounds[3],cb[3])]
  return bounds
 for url in sorted(set(ta)|set(tb)):
  changedterrain=ta.get(url)!=tb.get(url)
  for entries,out in [(ta,before),(tb,after)]:
   if url not in entries:continue
   path=ROOT/'3d-viewer'/url;raw=path.read_bytes();sha=digest(raw);expected=runtime['inputHashes'].get(str(path.relative_to(ROOT)),entries[url].get('sha256'));bounds=patch_bounds(json.loads(raw))
   if changedterrain:assert entries[url].get('sha256')==sha
   if expected is None:assert disjoint(bounds,region)
   else:assert sha==expected
   out.append(dict(id=url,sourceBinding=entries[url],completeWorldXZBounds=bounds if changedterrain else None));refs.append(ref(path))
 recomputed=verify(old,current,dict(terrain=before,native=native_before),dict(terrain=after,native=native_after),region,expected_old_hashes=runtime['inputHashes'],current_old_input_hashes=hashes,manifest_path=MANIFEST,old_manifest_sha=oldsha,new_manifest_sha=start['sha256'])
 for k,v in recomputed.items():assert regional[k]==v,'Regional proof differs: '+k
 # Recompute current identity without writing decoder caches.
 final=module('regional_replay_current_forms','xl-final-script-pass.py');from routed_original_cell_identity import verify as routed_verify
 from exact_original_georef_cell_identity_20261009 import apply_exact_cell
 contexts=read(context_path)['rows'];identities=[]
 for row in selection['rows']:
  raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);lo,hi=tri.min((0,1)),tri.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);ctx=next(c for c in contexts if c['uid']==row['uid']);sources=[];tiles={}
  for tile in current['tiles']:
   path=ROOT/'3d-viewer'/tile['url'];rawtile=path.read_bytes();matches=[f for f in json.loads(rawtile)['buildings']if str(f.get('buildingCSUID')or'')[:10]==row['modelId'][1:11]]
   if matches:tiles[tile['url']]=digest(rawtile);sources.extend(dict(building=f,tile=tile['url'],tileSHA256=digest(rawtile))for f in matches)
  for _,_,tile in forms:assert tile in ctx['neighbourTileHashes'] and digest((ROOT/'3d-viewer'/tile).read_bytes())==ctx['neighbourTileHashes'][tile]
  p=routed_verify(raw,row,ctx,tri,current_identity=final.identity_context(row,tri,forms),sources=sources);p.update(exactRouteTileHashes=tiles,exactRouteManifestSHA256=start['sha256']);binding=dict(uid=row['uid'],sourceSHA256=digest(raw),decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()));p=apply_exact_cell(p,tri,expected_binding=binding,current_binding=binding);assert p['passed'] and p==next(i for i in regional['completeCurrentIdentities']if i['uid']==row['uid']);identities.append(p)
 new=account(role,recomputed,identities,expected_owned=owned_sources,expected_retained=retained_sources,protected_scope=scope,old_manifest=oldsha,current_manifest=start)
 new['historicalNumericalNativeInventory']=new.pop('completeCurrentNativeWholeBoundsInventory',None)
 inventory_doc=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-complete-current-native-position-inventory-v2';inventory_receipt=receipt(inventory_doc);inventory=read(inventory_doc/'inventory.json.gz');assert inventory_receipt['inventory']==ref(inventory_doc/'inventory.json.gz') and inventory['currentManifest']==start and inventory['allOriginalPOSITIONVerticesIncluded']is True and inventory['completeNativeActors']==len(b)
 allnative={row['uid']:row for row in inventory['rows']};assert len(allnative)==len(inventory['rows']) and set(allnative)==set(b)
 whole=[]
 for uid,entry in sorted(b.items()):
  row=allnative[uid];e=entry['entry'];proof=row['completeOriginalPOSITIONProof'];source=(ROOT/'3d-viewer'/entry['catalogue']).parent/e['asset'];assert row['source']==ref(source) and row['rawCurrentEntry']==e and row['catalogue']==ref(ROOT/'3d-viewer'/entry['catalogue']) and proof['sourceSHA256']==row['sourceSHA256']==e['sha256'] and proof['allOriginalPositionVerticesAccounted']is True and proof['completeOriginalTriangles']==e['triangles'] and proof['completeOriginalPositionVertices']>=e['indexedVertices']
  whole.append(dict(uid=uid,sourceSHA256=e['sha256'],completeOriginalWorldBounds=proof['originalWholeSourceBounds'],completeOriginalPOSITIONProof=proof,catalogue=row['catalogue'],source=row['source']))
 new['completeCurrentNativeWholeBoundsInventory']=whole
 owned_arrays=np.concatenate([np.asarray(bb,float)for item in scope if item['kind']=='owned'for bb in item['completeOriginalLiteralAndFloat32Bounds']]);foreign_region=[float(owned_arrays[:,0].min()),float(owned_arrays[:,2].min()),float(owned_arrays[:,0].max()),float(owned_arrays[:,2].max())]
 if candidates:
  cb=candidates[0]['bounds'];foreign_region=[min(foreign_region[0],cb[0]),min(foreign_region[1],cb[1]),max(foreign_region[2],cb[2]),max(foreign_region[3],cb[3])]
 touching=[]
 for item in whole:
  lo,hi=item['completeOriginalWorldBounds']
  if not disjoint([lo[0],lo[2],hi[0],hi[2]],foreign_region):touching.append(item)
 assert {item['uid']for item in touching}==set(retained_sources),'New complete source-native region actor requires fresh physical checks'
 new['completeCurrentNativeWholeBoundsTouchingProposal']=touching
 new['completeCurrentOwnedSourceAndCandidateTerrainForeignBounds']=foreign_region
 refs+=[ref(inventory_doc/'inventory.json.gz'),ref(inventory_doc/'result.json')]+inventory_receipt['evidenceRefs']
 new.update(completeReadOnlyCurrentRegionReplay=True,completeCurrentRegionalManifestRebind=regional,immutableNumericalRole=ref(rolepath),historicalNumericalManifest=ref(archive),regionalReplayNumericAcceptanceRecomputed=False)
 refs+=[ref(HERE/f)for f in ['exact_packed_world_bounds_v3_20261010.py','exact_packed_world_geometry_20261009.py','routed_original_cell_identity.py','government_georef_cell_identity.py','component_type_resolution.py','exact_original_georef_cell_identity_20261009.py','xl-final-script-pass.py','run.py']]
 refs+=regional['evidenceRefs']+[ref(rebind_folder/'diagnostic.json.gz')]+role['evidenceRefs'];filtered=[]
 for item in refs:
  if item['path']==MANIFEST and item['sha256']==oldsha:item=ref(archive)
  filtered.append(item)
 new['evidenceRefs']=sorted({r['path']:r for r in filtered}.values(),key=lambda r:r['path']);assert ref(manifest)==start
 for item in new['evidenceRefs']:pin(item)
 return json.loads(json.dumps(new))
