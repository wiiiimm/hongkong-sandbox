"""Current Market source/terrain/actor rebind after disjoint Miami publication."""
import json,subprocess,copy,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_bounds_20261009 import packed_world_bounds
from exact_original_georef_cell_identity_20261009 import verify_files
from verified_disjoint_manifest_rebind_20261009 import verify,disjoint
BATCH='xl-terrain-recovery-20261009-market-six-disjoint-current-rebind-v2'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009'
GEOMETRY=HERE/'local/government-xl-terrain-recovery-market-six-original-physical-v5-20261009/runtime-geometry.json.gz'
MANIFEST='3d-viewer/city/data/manifest.json'
OLD_SHA='7de92c4dada1917ab6e37271d84f6134bd2517393f7156614d39530db35fbc03'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def bounds_patch(p):
 g=p['meta']['georef'];xs=[g['bE']-834500,g['bE']+(p['w']-1)*g['aE']-834500];zs=[816500-g['bN'],816500-g['bN']-(p['h']-1)*g['aN']]
 b=[min(xs),min(zs),max(xs),max(zs)]
 if p.get('nativeMesh'):
  v=np.asarray(p['nativeMesh']['position'],float).reshape(-1,3);assert len(v) and np.isfinite(v).all()
  b=[min(b[0],float(v[:,0].min())),min(b[1],float(v[:,2].min())),max(b[2],float(v[:,0].max())),max(b[3],float(v[:,2].max()))]
 for child in p.get('patches',[]):
  c=bounds_patch(child);b=[min(b[0],c[0]),min(b[1],c[1]),max(b[2],c[2]),max(b[3],c[3])]
 return b
def compute():
 archived=DOC/'historical-manifest.json';oldraw=archived.read_bytes();assert digest(oldraw)==OLD_SHA
 old=json.loads(oldraw);current=read(ROOT/MANIFEST);current_sha=digest((ROOT/MANIFEST).read_bytes());g=read(GEOMETRY)
 current_hashes={p:digest((ROOT/p).read_bytes()) for p in g['inputHashes']}
 region=list(read(PHYSICAL/'terrain-candidates.json')[0]['bounds']);neighbours=read(PHYSICAL/'neighbour-inputs.json.gz')
 for r in neighbours['rows']:
  v=np.asarray([p for ring in r['building']['rings'] for p in ring],float);assert v.shape[1]==2 and np.isfinite(v).all()
  region=[min(region[0],float(v[:,0].min())),min(region[1],float(v[:,1].min())),max(region[2],float(v[:,0].max())),max(region[3],float(v[:,1].max()))]
 refs=[ref(archived),ref(ROOT/MANIFEST),ref(GEOMETRY),ref(PHYSICAL/'neighbour-inputs.json.gz'),ref(PHYSICAL/'terrain-candidates.json'),ref(Path(__file__)),ref(HERE/'verified_disjoint_manifest_rebind_20261009.py')]
 def native_entries(manifest):
  entries={}
  for url in manifest['officialModelCatalogues']:
   path=ROOT/'3d-viewer'/url;refs.append(ref(path))
   for e in read(path)['models']:
    assert e['uid'] not in entries
    entries[e['uid']]=dict(entry=e,catalogue=url)
  return entries
 a,b=native_entries(old),native_entries(current);old_native=[];new_native=[]
 for uid in sorted(set(a)|set(b)):
  changed=a.get(uid)!=b.get(uid)
  for entries,out in [(a,old_native),(b,new_native)]:
   if uid not in entries:continue
   row=entries[uid];e=row['entry'];bounds=None
   if changed:
    path=(ROOT/'3d-viewer'/row['catalogue']).parent/e['asset'];proof=packed_world_bounds(path.read_bytes());assert proof['sourceSHA256']==e['sha256'];bb=proof['originalWholeSourceBounds'];bounds=[bb[0][0],bb[0][2],bb[1][0],bb[1][2]];refs.append(ref(path))
   out.append(dict(id=uid,sourceBinding=row,completeWorldXZBounds=bounds))
 old_terrain=[];new_terrain=[];ta={r['url']:r for r in old['terrainPatches']};tb={r['url']:r for r in current['terrainPatches']}
 assert len(ta)==len(old['terrainPatches']) and len(tb)==len(current['terrainPatches'])
 for url in sorted(set(ta)|set(tb)):
  changed=ta.get(url)!=tb.get(url)
  for entries,out in [(ta,old_terrain),(tb,new_terrain)]:
   if url not in entries:continue
   path=ROOT/'3d-viewer'/url;raw=path.read_bytes();relative=str(path.relative_to(ROOT));expected=entries[url].get('sha256',g['inputHashes'].get(relative));actual=digest(raw)
   if expected is None:assert disjoint(bounds_patch(json.loads(raw)),region),'Unpinned historical terrain touches regional input'
   else:assert actual==expected
   refs.append(ref(path))
   out.append(dict(id=url,sourceBinding=entries[url],completeWorldXZBounds=bounds_patch(json.loads(raw)) if changed else None))
 proof=verify(old,current,dict(terrain=old_terrain,native=old_native),dict(terrain=new_terrain,native=new_native),region,expected_old_hashes=g['inputHashes'],current_old_input_hashes=current_hashes,manifest_path=MANIFEST,old_manifest_sha=OLD_SHA,new_manifest_sha=current_sha)
 selected=read(PHYSICAL/'selection.json.gz');context=read(HERE/'local'/PHYSICAL.name/'frozen-inputs/context.json.gz');identities=[]
 for row in selected['rows']:
  ctx=next(c for c in context['rows'] if c['uid']==row['uid']);identity=verify_files(row,ctx,HERE/'local'/BATCH/'identity-recheck'/row['uid'].split('/')[1].replace(':','-'));assert identity['passed'] and identity['exactRouteManifestSHA256']==current_sha;identities.append(identity)
 proof.update(completeCurrentIdentities=identities,immutableRuntimeGeometry=ref(GEOMETRY),completeOldInputHashes=g['inputHashes'],completeCurrentOldInputHashes=current_hashes,evidenceRefs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']),sourceGeometryChanges=0,qualification='Only unrelated global manifest additions/removals are rebound. Every frozen source/world/current-ground/runtime input file is exactly unchanged except the explicitly archived global manifest. All changed native original whole bounds and complete terrain grids/native/descendant bounds are strictly disjoint from the full candidate patch and every42 neighbour footprint. Six independent provider/current-route identity proofs are freshly recomputed; all numerical/source roles and physical gates remain independently replayed.')
 return proof
def main():
 assert not DOC.exists();raw=subprocess.check_output(['git','show','03799b01:'+MANIFEST],cwd=ROOT);assert digest(raw)==OLD_SHA;DOC.mkdir(parents=True);(DOC/'historical-manifest.json').write_bytes(raw)
 try:
  proof=compute();save(DOC/'diagnostic.json.gz',proof);print(json.dumps(dict(currentManifestSHA256=proof['currentManifestSHA256'],rebindPassed=True,identities=len(proof['completeCurrentIdentities']),changedActors=len(proof['changedCompleteInventory']))),flush=True)
 except Exception as e:
  save(DOC/'guard-failure.json',dict(error=repr(e),publication=False));raise
if __name__=='__main__':main()
