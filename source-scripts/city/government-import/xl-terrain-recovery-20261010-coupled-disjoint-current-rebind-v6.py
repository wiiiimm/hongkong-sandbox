"""Coupled original source/terrain/actor rebind after disjoint publication."""
import json,subprocess,copy,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_bounds_20261009 import packed_world_bounds
from exact_original_georef_cell_identity_20261009 import verify_files
from verified_disjoint_manifest_rebind_20261009 import verify,disjoint
import argparse
p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);p.add_argument('--historical-git-ref',required=True);p.add_argument('--retained-native',action='append',default=[]);args=p.parse_args()
BATCH=args.batch;DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/args.physical;GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
MANIFEST='3d-viewer/city/data/manifest.json'
OLD_SHA=read(PHYSICAL/'selection.json.gz')['manifestSHA256']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def bounds_patch(p):
 g=p['meta']['georef'];xs=[g['bE']-834500,g['bE']+(p['w']-1)*g['aE']-834500];zs=[816500-g['bN'],816500-g['bN']-(p['h']-1)*g['aN']]
 xs=xs+[float(np.float32(v))for v in xs];zs=zs+[float(np.float32(v))for v in zs];b=[min(xs),min(zs),max(xs),max(zs)]
 if p.get('nativeMesh'):
  v=np.asarray(p['nativeMesh']['position'],float).reshape(-1,3);assert len(v) and np.isfinite(v).all();v=np.concatenate([v,v.astype(np.float32).astype(float)]);assert np.isfinite(v).all()
  b=[min(b[0],float(v[:,0].min())),min(b[1],float(v[:,2].min())),max(b[2],float(v[:,0].max())),max(b[3],float(v[:,2].max()))]
 for child in p.get('patches',[]):
  c=bounds_patch(child);b=[min(b[0],c[0]),min(b[1],c[1]),max(b[2],c[2]),max(b[3],c[3])]
 return b
def compute():
 archived=DOC/'historical-manifest.json';oldraw=archived.read_bytes();assert digest(oldraw)==OLD_SHA
 old=json.loads(oldraw);current=read(ROOT/MANIFEST);current_sha=digest((ROOT/MANIFEST).read_bytes());g=read(GEOMETRY)
 current_hashes={p:digest((ROOT/p).read_bytes()) for p in g['inputHashes']}
 candidates=read(PHYSICAL/'terrain-candidates.json');neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');scope_asset_refs=[]
 protected_scope=[];scope_arrays=[]
 selected=read(PHYSICAL/'selection.json.gz');assert [r['uid']for r in selected['rows']]==[r['uid']for r in g['rows']]
 if candidates:
  assert len(candidates)==1 and args.retained_native,'Explicit complete retained-dependency scope is mandatory';region=list(candidates[0]['bounds'])
 else:
  assert args.retained_native==['landsd/22089:0'] and [r['uid']for r in g['rows']]==['landsd/89613:0'],'Only reviewed unchanged-terrain HKDI B retained-native route supported'
  region=[float('inf'),float('inf'),float('-inf'),float('-inf')]
 for selected_row,runtime in zip(selected['rows'],g['rows']):
  source_path=ROOT/selected_row['candidate']['path'];original=packed_world_bounds(source_path.read_bytes());entry=selected_row['candidate']['entry'];assert original['sourceSHA256']==selected_row['sourceSHA256']==entry['sha256'] and original['completeOriginalTriangles']==entry['triangles']
  positions=np.asarray(runtime['position'],float).reshape(-1,3);indices=np.asarray(runtime['index']);assert np.isfinite(positions).all() and len(positions)==entry['indexedVertices'] and len(indices)==3*entry['triangles'] and runtime['sourceSHA256']==entry['sha256']
  cast=positions.astype(np.float32).astype(float);assert np.isfinite(cast).all();measured=[original['originalWholeSourceBounds'],[positions.min(0).tolist(),positions.max(0).tolist()],[cast.min(0).tolist(),cast.max(0).tolist()]];scope_arrays.extend(np.asarray(bb,float)for bb in measured)
  protected_scope.append(dict(kind='owned',uid=selected_row['uid'],sourceSHA256=entry['sha256'],completeOriginalLiteralAndFloat32Bounds=measured,allOriginalVerticesAccounted=True));scope_asset_refs.extend([ref(source_path),ref(PHYSICAL/'selection.json.gz'),ref(HERE/'exact_packed_world_bounds_20261009.py')])
 helper=HERE/'xl-terrain-recovery-20261010-current-original-literal-actor-bounds-readonly-v3.mjs';native_input=DOC/'protected-retained-native-bounds-input.json';native_output=DOC/'protected-retained-native-bounds.json'
 assert len(args.retained_native)==len(set(args.retained_native)) and not set(args.retained_native)&set(r['uid']for r in selected['rows'])
 save(native_input,dict(uids=args.retained_native,manifest=dict(path=MANIFEST,sha256=current_sha),catalogueManifest=ref(archived)))
 subprocess.run(['node',str(helper),'--input',str(native_input.relative_to(ROOT)),'--out',str(native_output.relative_to(ROOT))],cwd=ROOT,check=True)
 native_bounds=read(native_output);assert native_bounds['acceptance']is False and native_bounds['geometryChanges']==0 and [r['uid']for r in native_bounds['rows']]==args.retained_native
 for path,sha in native_bounds['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;scope_asset_refs.append(ref(ROOT/path))
 scope_asset_refs.extend([ref(native_input),ref(native_output),ref(helper)])
 matches={}
 for url in old['officialModelCatalogues']:
  catalogue=ROOT/'3d-viewer'/url
  for entry in read(catalogue)['models']:
   if entry['uid']in args.retained_native:assert entry['uid']not in matches;matches[entry['uid']]=(catalogue,entry)
 assert set(matches)==set(args.retained_native)
 for literal in native_bounds['rows']:
  catalogue,entry=matches[literal['uid']];source_path=catalogue.parent/entry['asset'];original=packed_world_bounds(source_path.read_bytes());assert original['sourceSHA256']==entry['sha256']==literal['sourceSHA256'] and original['completeOriginalTriangles']==entry['triangles']==literal['completeOriginalTriangles'] and entry==literal['rawCurrentEntry']
  measured=[original['originalWholeSourceBounds'],literal['completeLiteralWorldBounds'],literal['completeFloat32CastWorldBounds']];scope_arrays.extend(np.asarray(bb,float)for bb in measured);protected_scope.append(dict(kind='retained-native',uid=literal['uid'],sourceSHA256=entry['sha256'],completeOriginalLiteralAndFloat32Bounds=measured,allOriginalVerticesAccounted=True));scope_asset_refs.extend([ref(source_path),ref(catalogue)])
 assert scope_arrays;joined=np.concatenate(scope_arrays);region=[min(region[0],float(joined[:,0].min())),min(region[1],float(joined[:,2].min())),max(region[2],float(joined[:,0].max())),max(region[3],float(joined[:,2].max()))]
 for measured in scope_arrays:assert region[0]<=measured[:,0].min() and region[1]<=measured[:,2].min() and region[2]>=measured[:,0].max() and region[3]>=measured[:,2].max(),'Protected original/literal/F32 source strip omitted'


 for r in neighbours['rows']:
  v=np.asarray([p for ring in r['building']['rings'] for p in ring],float);assert v.shape[1]==2 and np.isfinite(v).all()
  region=[min(region[0],float(v[:,0].min())),min(region[1],float(v[:,1].min())),max(region[2],float(v[:,0].max())),max(region[3],float(v[:,1].max()))]
 refs=scope_asset_refs+[ref(archived),ref(ROOT/MANIFEST),ref(GEOMETRY),ref(PHYSICAL/'neighbour-inputs.json.gz'),ref(PHYSICAL/'terrain-candidates.json'),ref(Path(__file__)),ref(HERE/'verified_disjoint_manifest_rebind_20261009.py')]
 def native_entries(manifest):
  entries={}
  for url in manifest['officialModelCatalogues']:
   path=ROOT/'3d-viewer'/url;refs.append(ref(path))
   for e in read(path)['models']:
    assert e['uid'] not in entries
    entries[e['uid']]=dict(entry=e,catalogue=url)
  return entries
 a,b=native_entries(old),native_entries(current);old_native=[];new_native=[]
 changed_uids=sorted(uid for uid in set(a)|set(b) if a.get(uid)!=b.get(uid));literal_bounds={}
 helper=HERE/'xl-terrain-recovery-20261010-current-original-literal-actor-bounds-readonly-v3.mjs'
 for label,entries in [('old',a),('current',b)]:
  uids=[uid for uid in changed_uids if uid in entries]
  if not uids:continue
  input_path=DOC/('changed-'+label+'-actor-bounds-input.json');output_path=DOC/('changed-'+label+'-actor-bounds.json')
  payload=dict(uids=uids,manifest=dict(path=MANIFEST,sha256=current_sha))
  if label=='old':payload['catalogueManifest']=ref(archived)
  save(input_path,payload)
  subprocess.run(['node',str(helper),'--input',str(input_path.relative_to(ROOT)),'--out',str(output_path.relative_to(ROOT))],cwd=ROOT,check=True)
  measured=read(output_path);assert measured['acceptance']is False and measured['geometryChanges']==0 and [r['uid']for r in measured['rows']]==uids
  for relative,sha in measured['inputHashes'].items():assert digest((ROOT/relative).read_bytes())==sha;refs.append(ref(ROOT/relative))
  refs.extend([ref(input_path),ref(output_path),ref(helper),ref(HERE/'original_literal_complete_actor_bounds_20261010.mjs')])
  for row in measured['rows']:
   e=entries[row['uid']]['entry'];assert row['sourceSHA256']==e['sha256'] and row['rawCurrentEntry']==e and row['completeOriginalTriangles']==e['triangles'] and row['completeIndexedVertices']==e['indexedVertices'] and row['allOriginalVerticesIncluded']is True
   literal_bounds[(label,row['uid'])]=row

 for uid in sorted(set(a)|set(b)):
  changed=a.get(uid)!=b.get(uid)
  for label,entries,out in [('old',a,old_native),('current',b,new_native)]:
   if uid not in entries:continue
   row=entries[uid];e=row['entry'];bounds=None
   if changed:
    path=(ROOT/'3d-viewer'/row['catalogue']).parent/e['asset'];proof=packed_world_bounds(path.read_bytes());assert proof['sourceSHA256']==e['sha256'];measured=literal_bounds[(label,uid)]
    all_bounds=np.asarray([proof['originalWholeSourceBounds'],measured['completeLiteralWorldBounds'],measured['completeFloat32CastWorldBounds']],float);assert all_bounds.shape==(3,2,3) and np.isfinite(all_bounds).all()
    bounds=[float(all_bounds[:,0,0].min()),float(all_bounds[:,0,2].min()),float(all_bounds[:,1,0].max()),float(all_bounds[:,1,2].max())]
    for bb in all_bounds:assert bounds[0]<=bb[0,0] and bounds[1]<=bb[0,2] and bounds[2]>=bb[1,0] and bounds[3]>=bb[1,2],'Changed remote original/literal/F32 strip omitted'
    refs.append(ref(path))
   out.append(dict(id=uid,sourceBinding=row,completeWorldXZBounds=bounds))
 old_terrain=[];new_terrain=[];ta={r['url']:r for r in old['terrainPatches']};tb={r['url']:r for r in current['terrainPatches']}
 assert len(ta)==len(old['terrainPatches']) and len(tb)==len(current['terrainPatches'])
 for url in sorted(set(ta)|set(tb)):
  changed=ta.get(url)!=tb.get(url)
  for entries,out in [(ta,old_terrain),(tb,new_terrain)]:
   if url not in entries:continue
   path=ROOT/'3d-viewer'/url;raw=path.read_bytes();relative=str(path.relative_to(ROOT));expected=g['inputHashes'].get(relative,entries[url].get('sha256'));actual=digest(raw)
   if changed:assert entries[url].get('sha256')==actual,'Changed terrain must have exact active metadata SHA'
   if expected is None:assert disjoint(bounds_patch(json.loads(raw)),region),'Unpinned historical terrain touches regional input'
   else:assert actual==expected
   refs.append(ref(path))
   out.append(dict(id=url,sourceBinding=entries[url],completeWorldXZBounds=bounds_patch(json.loads(raw)) if changed else None))
 proof=verify(old,current,dict(terrain=old_terrain,native=old_native),dict(terrain=new_terrain,native=new_native),region,expected_old_hashes=g['inputHashes'],current_old_input_hashes=current_hashes,manifest_path=MANIFEST,old_manifest_sha=OLD_SHA,new_manifest_sha=current_sha)
 selected=read(PHYSICAL/'selection.json.gz');context=read(HERE/'local'/PHYSICAL.name/'frozen-inputs/context.json.gz');identities=[]
 for row in selected['rows']:
  ctx=next(c for c in context['rows'] if c['uid']==row['uid']);identity=verify_files(row,ctx,HERE/'local'/BATCH/'identity-recheck'/row['uid'].split('/')[1].replace(':','-'));assert identity['passed'] and identity['exactRouteManifestSHA256']==current_sha;identities.append(identity)
 proof.update(completeProtectedOriginalLiteralFloat32Scope=protected_scope,completeChangedNativeOriginalLiteralFloat32Bounds={label:{uid:r for (kind,uid),r in literal_bounds.items()if kind==label}for label in ['old','current']},noTerrainWholeOriginalAndLiteralScopeBounds=region if not candidates else None,completeCurrentFormsCount=len(neighbours['rows']),completeOwnedOriginalCount=len(selected['rows']),completeCurrentIdentities=identities,immutableRuntimeGeometry=ref(GEOMETRY),completeOldInputHashes=g['inputHashes'],completeCurrentOldInputHashes=current_hashes,evidenceRefs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']),sourceGeometryChanges=0,qualification='Only unrelated global manifest additions/removals are rebound. Every frozen source/world/current-ground/runtime input file is exactly unchanged except the explicitly archived global manifest. All changed native whole original plus independently loaded current literal/Float32 bounds and complete terrain grids/native/descendant bounds are strictly disjoint from the full candidate patch plus every complete owned and retained original/literal/Float32 projection and every independently enumerated current form footprint. Independent provider/current-route identity proofs are freshly recomputed; all numerical/source roles and physical gates remain independently replayed.')
 return proof
def main():
 assert not DOC.exists();raw=subprocess.check_output(['git','show',args.historical_git_ref+':'+MANIFEST],cwd=ROOT);assert digest(raw)==OLD_SHA;DOC.mkdir(parents=True);(DOC/'historical-manifest.json').write_bytes(raw)
 try:
  proof=compute();save(DOC/'diagnostic.json.gz',proof)
  import importlib.util
  spec=importlib.util.spec_from_file_location('coupled_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-coupled-disjoint-current-regional-rebind-v6',[ROOT/r['path'] for r in proof['evidenceRefs']],dict(uids=[r['uid'] for r in read(PHYSICAL/'selection.json.gz')['rows']],currentManifestSHA256=proof['currentManifestSHA256'],completeCurrentFormsCount=proof['completeCurrentFormsCount'],completeOwnedOriginalCount=proof['completeOwnedOriginalCount'],rebindPassed=True,fullAcceptance=False))
  print(json.dumps(dict(currentManifestSHA256=proof['currentManifestSHA256'],rebindPassed=True,identities=len(proof['completeCurrentIdentities']),changedActors=len(proof['changedCompleteInventory']))),flush=True)
 except Exception as e:
  save(DOC/'guard-failure.json',dict(error=repr(e),publication=False));raise
if __name__=='__main__':main()
