"""Read-only pointer-scoped closure of one completed plain-source staged/live installation.

Global archived metadata is byte-bound but does not import unrelated raw caches.
Current source physics remains in the independently verified source scope.
"""
import argparse,json,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from original_disjoint_routing_metadata_scope_20261010 import canonical,verify_boundaries
from original_complete_role_routing_metadata_scope_20261010 import verify_role_boundaries

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--installed-batch',required=True);p.add_argument('--source-scope',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
 assert all(Path(x).name==x for x in [a.installed_batch,a.batch]);base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
 config=(ROOT/a.config).resolve();source_scope=(ROOT/a.source_scope).resolve();assert config.is_relative_to(ROOT) and source_scope.is_relative_to(ROOT)
 cfg=read(config);assert cfg['schema']=='plain-single-source-original-stage-v1' and len(cfg['sources'])==1
 doc=base/a.installed_batch;stage_doc=base/cfg['batch'];stage=HERE/'accepted'/cfg['batch'];r=read(doc/'result.json');uid=next(iter(cfg['sources']))
 assert r['publication'] and r['newlyInstalled']==1 and r['installedUids']==[uid] and r['sourceSHA256s']==cfg['sources'];sync=read(doc/'neon-sync.json');assert sync['jobId']==r['jobId'] and sync['resultVerified']
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(r['snapshotId'],uid)).fetchone()==('installed-verified',cfg['sources'][uid])
 scope=read(source_scope);pointer_rows=list(scope.get('metadataLeafJsonPointers',[]));pointer_map={}
 # Staged/live byte-identical copies retain the same independently declared pointers.
 final_role=cfg['currentTypedRole'];template=[x for x in pointer_rows if x['documentSHA256']==final_role['sha256']]
 role_data=read(ROOT/final_role['path'])
 if 'completeCurrentTerrainRouting' in role_data:assert template or not pointer_rows
 else:assert not template,'A role without routing data must not have invented role routing boundaries'
 for copy_path in [stage_doc/'typed-role-publication-recheck.json.gz',doc/'complete-current-role.json.gz']:
  assert copy_path.is_file() and digest(copy_path.read_bytes())==final_role['sha256']
  pointer_rows.extend(dict(x,path=str(copy_path.relative_to(ROOT))) for x in template)
 for item in pointer_rows:
  path=item['path'];assert path.startswith('docs/astra-city/government-import/') and (path.endswith('/current-source-terrain-preflight.json') or path.endswith('/typed-role.json.gz') or path.endswith('/typed-role-publication-recheck.json.gz') or path.endswith('/complete-current-role.json.gz')) and digest((ROOT/path).read_bytes())==item['documentSHA256'];pointer_map.setdefault(path,[]).append(item['boundary'])
 for path,declared in pointer_map.items():
  preflight=read(ROOT/path);role_mode=declared[0].get('documentType')=='complete-current-original-role-routing-provenance-v1';sha=preflight['manifestSHA256'] if role_mode else preflight['currentManifest']['sha256'];matching=[x for x in scope['historicalManifestAliases'] if x['sha256']==sha];assert len(matching)==1;frozen=ROOT/matching[0]['archive']['path'];assert digest(frozen.read_bytes())==matching[0]['sha256']
  if role_mode:
   candidate_ref=declared[0]['boundCandidateRef'];candidate=ROOT/candidate_ref['path'];assert ref(candidate)==candidate_ref;verify_role_boundaries(preflight,read(frozen),read(candidate),declared,candidate_ref=candidate_ref,manifest_ref=dict(path='3d-viewer/city/data/manifest.json',sha256=sha),expected_uids=sorted(cfg['sources']))
  else:verify_boundaries(preflight,read(frozen),declared)
 leaf=set(scope['metadataLeafPaths']);paths=set();versions=[];queue=[];seen=set();backup=HERE/'local'/a.installed_batch/'manifest-before-installation.json';assert digest(backup.read_bytes())==r['manifestBeforeSHA256']
 aliases=[*scope['historicalManifestAliases'],dict(originalPath='3d-viewer/city/data/manifest.json',sha256=r['manifestBeforeSHA256'],archive=ref(backup))];alias={(x['originalPath'],x['sha256']):ROOT/x['archive']['path'] for x in aliases}
 def add(f):
  f=Path(f).resolve();assert f.is_relative_to(ROOT) and f.is_file(),str(f);rel=str(f.relative_to(ROOT))
  if rel not in paths:paths.add(rel);queue.append(f)
 for parent in [doc,stage_doc,stage]:
  assert parent.exists()
  for f in parent.rglob('*'):
   if f.is_file():add(f)
 for f in [config,source_scope,backup,Path(__file__),HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-v1.py',HERE/'xl-terrain-recovery-20261010-plain-single-source-live-v1.py',HERE/'xl-terrain-recovery-20261010-plain-single-source-live-v2.py',HERE/'test_plain_single_source_stage_interface_20261010.py',HERE/'original_disjoint_routing_metadata_scope_20261010.py',HERE/'test_original_disjoint_routing_metadata_scope_20261010.py',HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-live-closure-v1.py',HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-live-closure-v2.py',HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-live-closure-v3.py',HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-live-closure-v4.py',HERE/'original_complete_role_routing_metadata_scope_20261010.py',HERE/'test_original_complete_role_routing_metadata_scope_20261010.py']:add(f)
 # Scope lists and archived whole-manifest snapshots are declared metadata leaves.
 leaf.update([str(source_scope.relative_to(ROOT)),str(backup.relative_to(ROOT))])
 # Interrupted whole-manifest archival bytes are metadata, never numeric input.
 interrupted=doc/'interrupted-applied-manifest.json'
 if interrupted.exists():
  assert interrupted.is_file() and read(interrupted).get('officialModelCatalogues') and read(interrupted).get('terrainPatches')
  recovery=doc/'interrupted-live-recovery.json';assert recovery.is_file()
  recovery_data=read(recovery);assert recovery_data['installedCreditGranted'] is False and recovery_data['interruptedAppliedManifestSHA256']==digest(interrupted.read_bytes()) and recovery_data['restoredManifestSHA256']==digest(backup.read_bytes())
  # Explicit archival copy remains in closedPaths/presentFileBindings. Its
  # routing provenance may reference unrelated historical raw caches.
  add(interrupted);add(recovery);leaf.add(str(interrupted.relative_to(ROOT)))
 assets_recovery=doc/'interrupted-assets-recovery.json'
 if assets_recovery.exists():
  add(assets_recovery);recovered_assets=read(assets_recovery)
  assert recovered_assets['installedCreditGranted'] is False and recovered_assets['sourceBytesChanged'] is False and recovered_assets['manifestRestoredSHA256']==digest(backup.read_bytes())
  for entry in recovered_assets['unpublishedAssetsPreserved']:
   preserved=ROOT/entry['preservedPath'];current=ROOT/entry['previousPath'];assert digest(preserved.read_bytes())==digest(current.read_bytes())==entry['sha256'];add(preserved)
  archive=HERE/'local'/a.installed_batch/'interrupted-published-assets';assert archive.is_dir()
  for f in archive.rglob('*'):
   if f.is_file():add(f)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';inventory=ROOT/read(pointer)['inventory']
 for f in [pointer,inventory,ROOT/'3d-viewer/city/data/manifest.json',ROOT/'3d-viewer/city/data/building-progress.json',ROOT/'3d-viewer/data/building-progress.json',ROOT/'3d-viewer/scripts/building-progress/review-proof.json',ROOT/'3d-viewer/scripts/building-progress/screening-proof.json',ROOT/'docs/astra-city/landmark-completion-audit/neon-snapshot.json']:
  if f.exists():add(f);leaf.add(str(f.relative_to(ROOT)))
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')==r['manifest'],'Installation is no longer current; a separately named historical closure is required'
 plan=read(doc/'atomic-plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
 for area in plan['areas']:
  cat=ROOT/'3d-viewer'/area['destination'];add(cat);models=read(cat)['models'];assert len(models)==1 and models[0]['uid']==uid
  for model in models:
   f=cat.parent/model['asset'];assert digest(f.read_bytes())==model['sha256']==cfg['sources'][uid];add(f)
 for terrain in plan['topLevelTerrainPatches']:
  assert not terrain.get('replaces') and not terrain.get('replacesMany');f=ROOT/'3d-viewer'/terrain['destination'];assert digest(f.read_bytes())==terrain['sha256'];add(f)
 def references(v,document,pointer=""):
  declared={x["pointer"]:x for x in pointer_map.get(document,[])}
  if pointer in declared:
   assert canonical(v)==declared[pointer]["canonicalSHA256"];return
  if isinstance(v,dict):
   if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:
    e=dict(path=v['path'],sha256=v['sha256']);f=ROOT/e['path'];actual=digest(f.read_bytes()) if f.is_file() else None
    if actual!=e['sha256']:f=alias.get((e['path'],e['sha256']));assert f is not None and digest(f.read_bytes())==e['sha256'],'Unbound changed reference:'+e['path']
    versions.append(e);add(f)
   for key,x in v.items():references(x,document,pointer+"/"+str(key).replace("~","~0").replace("/","~1"))
  elif isinstance(v,list):
   for i,x in enumerate(v):references(x,document,pointer+"/"+str(i))
 while queue:
  f=queue.pop();rel=str(f.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaf:continue
  if f.name.endswith('.json') or f.name.endswith('.json.gz'):references(read(f),rel)
 tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines());result=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/f) for f in sorted(paths)],referenceVersions=sorted({(e['path'],e['sha256']):e for e in versions}.values(),key=lambda e:(e['path'],e['sha256'])),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),metadataLeafJsonPointers=pointer_rows,newFiles=[f for f in sorted(paths) if f not in tracked],installedNeon=r['jobId'],snapshotId=r['snapshotId'],sourceScope=ref(source_scope),qualification='Complete solid staged/live exports, guarded original-source publisher, deployed exact source/native terrain and installed Neon readback. Full numeric source proof separately closed; byte-bound archived global metadata does not recursively import unrelated raw cache files.')
 save(out/'closed-scope.json',result);print(json.dumps(dict(paths=len(paths),referenceVersions=len(result['referenceVersions']),newFiles=len(result['newFiles']),jobId=r['jobId'])),flush=True)
if __name__=='__main__':main()
