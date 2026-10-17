"""Block6 installed evidence scope draft; execute only after root live/export/Neon verification."""
import ast,json,subprocess,time,sys,struct
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import';DOC=B/'xl-terrain-recovery-20261011-parkview-block6-installed-scope-v1'
SOURCE=B/'xl-terrain-recovery-20261011-parkview-block6-stage-scope-v1'
ORIGINALSOURCE=B/'xl-terrain-recovery-20261011-parkview-block6-source-scope-v3'
INSTALLEDBATCH='government-xl-parkview-block6-unchanged-installed-v1-20261011'
INSTALLDOC=B/INSTALLEDBATCH;LOCAL=HERE/'local'/INSTALLEDBATCH
BEFORE_SHA='cb79525c2c95d96eb0c9868158bfe04c21a60135ec5a8e755ccea106c972b402'
BATCH='government-xl-parkview-block6-unchanged-current-stage-v1-20261011'
STAGEDOC=B/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/255438:0';RETAINED={'landsd/254491:0','landsd/255439:0','landsd/255647:0','landsd/256112:0','landsd/256114:0'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert '--live-export-review-complete'in sys.argv,'Root must finish actual live export and receipt review before execution';assert not DOC.exists();priorpath=SOURCE/'declared-scope.json';prior=read(priorpath);certificate=read(SOURCE/'root-closed-scope.json');assert certificate['independentlyVerified']is True;acceptance=read(STAGEDOC/'acceptance.json');assert acceptance['passed']is True and acceptance['publication']is False and acceptance['newlyInstalled']==0;installed=read(INSTALLDOC/'installed-acceptance.json');result=read(INSTALLDOC/'result.json');assert installed['publication']is True and installed['newlyInstalled']==1 and result['fullXLCurrentCounts']==dict(total=521,installedVerified=225,remaining=296);assert ref(ROOT/installed['manifest']['path'])==installed['manifest'];assert read(INSTALLDOC/'neon-sync.json')['resultVerified']is True;report=read(STAGEDOC/'live-browser.json');assert report['passed']is True and report['errors']==[];views=[v for v in report['views']if 'time'in v];retained=report['retainedNativeOwnViews'];assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']};assert len(retained)==20 and {(v['uid'],v['width'],v['time'])for v in retained}=={(u,w,t)for u in RETAINED for w in [1280,390]for t in ['15:00','22:00']};assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID};assert all(v['active']and v['visible']and v['fullyFramed']for v in views+retained);assert len({v['file']for v in views+retained})==24
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result);assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(result['snapshotId'],UID)).fetchone()==('installed-verified','363c8df82ecf39c7a9d1f6948e2b2aec06af28820642fdeeab45f9d08da36bae')
 for v in views+retained:
  image=STAGEDOC/v['file'];assert image.parent==STAGEDOC;raw=image.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack('>II',raw[16:24])[0]==v['width']
 aliases=list(prior['historicalManifestAliases']);assert len(aliases)==53;before=LOCAL/'manifest-before-installation.json';assert digest(before.read_bytes())==BEFORE_SHA;aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=BEFORE_SHA,archive=ref(before)));leaves=set(prior['metadataLeafPaths']);assert not prior['metadataLeafJsonPointers'];archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set();paths=set();queue=[];hashes={};versions={};cached={};unknown=[];audit={};seen=set()
 def hashed(p):
  if p not in hashes:hashes[p]=digest(p.read_bytes())if p.is_file()else None
  return hashes[p]
 def is_audit(p):return p.name in ['declared-scope.json','closed-scope.json','root-closed-scope.json']or p.name.startswith('source-review-inventory-')
 def initial_add(p):
  p=Path(p);assert p.is_file(),str(p);rel=str(p.relative_to(ROOT))
  if is_audit(p):audit[rel]=ref(p);return
  initial.add(rel)
 def add(p):
  p=Path(p);rel=str(p.relative_to(ROOT));assert p.is_file(),rel
  if is_audit(p):audit[rel]=ref(p);return
  if rel in tracked and rel not in initial:
   cached[rel]=dict(path=rel,sha256=hashed(p));return
  if rel not in paths:paths.add(rel);queue.append(p)
 def bind(path,h,origin):
  p=Path(path)if Path(path).is_absolute()else ROOT/path
  if not p.exists()and path.startswith('city/'):p=ROOT/'3d-viewer'/path
  rel=str(p.relative_to(ROOT))
  if hashed(p)!=h:
   p=archive.get((rel,h))
   if p is None:unknown.append(dict(path=rel,sha256=h,origin=origin));return
  assert hashed(p)==h;versions[(rel,h)]=dict(path=rel,sha256=h);add(p)
 def refs(v,origin):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:bind(v['path'],v['sha256'],origin)
   for k,x in v.items():
    if k in ['inputHashes','hashes','neighbourTileHashes','currentTileHashes','nativeCatalogueInputHashes','sourceInputHashes']and isinstance(x,dict):
     for p,h in x.items():
      if isinstance(p,str)and isinstance(h,str)and len(h)==64:bind(p,h,origin)
    else:refs(x,origin)
  elif isinstance(v,list):
   for x in v:refs(x,origin)
 # Source numerical closure stays explicitly initial; its declaration/certificate
 # are exact audit contracts, never recursive inventories of candidate inputs.
 for rel in prior['closedPaths']:initial_add(ROOT/rel)
 for directory in [STAGEDOC,STAGE,INSTALLDOC,LOCAL,ROOT/'3d-viewer/city/data/official-models'/BATCH]:
  assert directory.is_dir()
  for p in directory.rglob('*'):
   if p.is_file():initial_add(p)
 for p in [Path(__file__),HERE/'xl-terrain-recovery-20261011-parkview-block6-unchanged-current-stage-v1.py',HERE/'xl-parkview-block6-unchanged-live-install-v1-20261011.py',HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs',HERE/'candidate_native_support_witness_v1_20261010.mjs',HERE.parent/'landmark-preflight/browser-runtime.mjs',HERE.parent/'model-integration-20260909/publish.py']:
  initial_add(p)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointerdata=read(pointer);assert pointerdata['snapshotId']==result['snapshotId'];inventory=ROOT/pointerdata['inventory'];assert read(inventory)['snapshotId']==result['snapshotId'];initial_add(pointer);initial_add(inventory)
 for rel in ['3d-viewer/city/data/manifest.json','3d-viewer/city/data/building-progress.json','3d-viewer/scripts/building-progress/review-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json','source-scripts/city/building-progress/export.py','3d-viewer/scripts/build_progress.mjs','3d-viewer/scripts/building-progress/generate.mjs','source-scripts/city/government-import/xl-current-installed-count-audit.py']:
  initial_add(ROOT/rel)
 for p in [priorpath,SOURCE/'root-closed-scope.json',ORIGINALSOURCE/'declared-scope.json',ORIGINALSOURCE/'root-closed-scope.json']:
  audit[str(p.relative_to(ROOT))]=ref(p)
 for item in prior['auditDeclarationContextRefs']:
  assert ref(ROOT/item['path'])==item;audit[item['path']]=item
 for name in ['ROOT_REVIEW','ROOT_REVIEW.md','ROOT_REVIEW.json']:
  p=SOURCE/name
  if p.is_file():audit[str(p.relative_to(ROOT))]=ref(p)
 for rel in sorted(initial):add(ROOT/rel)
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaves:continue
  if p.name.endswith('.json')or p.name.endswith('.json.gz'):refs(read(p),rel)
  if p.suffix=='.py':
   for n in ast.walk(ast.parse(p.read_text())):
    names=([n.module]if isinstance(n,ast.ImportFrom)and n.module else[a.name for a in n.names]if isinstance(n,ast.Import)else[])
    for name in names:
     q=HERE/(name.split('.')[0]+'.py')
     if q.exists():add(q)
 current=installed['manifest'];assert ref(ROOT/current['path'])==current;assert not any('block6'in p for p in leaves);assert certificate['currentManifestSHA256']==BEFORE_SHA;assert ref(ROOT/acceptance['stagedBrowser']['path'])==acceptance['stagedBrowser'];assert ref(ROOT/installed['liveBrowser']['path'])==installed['liveBrowser'];assert read(INSTALLDOC/'full-xl-current-count.json')['counts']==result['fullXLCurrentCounts']
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),trackedCacheContract='Root contract: exact referenced tracked file hash verified; recurse only if explicitly initial. Full new Block6 source/numerical/current artifacts are explicitly initial even tracked.',historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=[],auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),auditDeclarationsNotCandidateNumericInputs=True,unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,currentManifest=current,newMetadataLeaves=False,newHistoricalAliases=[aliases[-1]],inheritedAliasCount=53,currentAcceptance=False,installationApproved=False,newlyInstalled=0,fullNumericalSourceClosureRequired=True,stagedBrowserExportsIncluded=True,stagedOwnedViews=4,stagedRetainedOwnViews=20,failedDownloadRetryIncluded=True,rootLiveExportReviewComplete=True,recordsRootPublication=True,installedSnapshotId=result['snapshotId'],installedNeonJobId=result['jobId'],installedCounts=result['fullXLCurrentCounts'],liveWritesExcluded=True,sourceCertificate=ref(SOURCE/'root-closed-scope.json'),explicitInitialPaths=sorted(initial),elapsedSeconds=time.monotonic()-start,qualification='Audit of root-completed publication only. Every independently closed source/stage numerical input remains explicitly initial, plus complete staged/live raw exports, installed asset/config/catalogue/plan, current role and identity rechecks, retained terrain/native preservation snapshots, installed acceptance/Neon receipt, current counts, progress proofs and current ledger pointer. Four owned and twenty retained own-camera live views plus failed download/retry and root actual export review are required. The new before-manifest alias is added only after exact cb795 SHA verification; all53 prior aliases and metadata contracts remain unchanged. Source-review inventory and prior declarations/certificates/failure inventories are exact audit context pins, never numerical source inputs or deeply unfolded histories. This builder writes no live state, invokes no publisher, grants no whole-native reapproval, and does not waive original raw failures.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),exactTrackedDependencies=len(cached),versions=len(versions),elapsedSeconds=out['elapsedSeconds'],unboundCount=len(unknown),firstUnbound=unknown[:5])),flush=True)
if __name__=='__main__':main()
