"""Exact HSBC current replay scope, global archived manifest is leaf metadata."""
import json,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261009-hsbc-three-current-replay-scope-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
ROLE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-hsbc-three-current-role-v3/typed-role.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();role=read(ROLE);sha=role['manifestSHA256'];current=ROOT/'3d-viewer/city/data/manifest.json';backup=HERE/'local/government-xl-hsbc-three-atomic-installed-v2-20261009/manifest-before-installation.json';source=current if digest(current.read_bytes())==sha else backup;raw=source.read_bytes();assert digest(raw)==sha;save(DOC/'manifest-alias.json',dict(originalPath='3d-viewer/city/data/manifest.json',sha256=sha,archivePath=str((DOC/'preinstallation-manifest.json').relative_to(ROOT))));(DOC/'preinstallation-manifest.json').write_bytes(raw)
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));inputs=[]
 for r in role['evidenceRefs']:
  p=ROOT/r['path']
  if r['path']=='3d-viewer/city/data/manifest.json':p=DOC/'preinstallation-manifest.json'
  assert digest(p.read_bytes())==r['sha256'];inputs.append(dict(**r,actualVerifiedPath=str(p.relative_to(ROOT)),bytes=p.stat().st_size,alreadyTracked=str(p.relative_to(ROOT)) in tracked,verification='actual-file-bytes'))
 closed=[];base=ROOT/'docs/astra-city/government-import'
 for directory in sorted(base.iterdir()):
  if directory.name.startswith(('xl-terrain-recovery-20261009-hsbc-','government-xl-terrain-recovery-hsbc-three-')) or directory.name in ['xl-terrain-recovery-20261009-265848-three-current-complete-context-v2','xl-terrain-recovery-20261009-337075-current-complete-context-v1','xl-terrain-recovery-20261009-337079-current-complete-context-v1']:
   closed.extend(str(p.relative_to(ROOT)) for p in directory.rglob('*') if p.is_file() and directory!=DOC)
 for p in (HERE/'accepted/government-xl-terrain-recovery-hsbc-three-typed-stage-v1-20261009').rglob('*'):
  if p.is_file():closed.append(str(p.relative_to(ROOT)))
 for p in HERE.iterdir():
  if p.is_file() and ('hsbc' in p.name and p.name.startswith(('xl-terrain-recovery-20261009-','hsbc_mounted_','test_hsbc_mounted_'))):closed.append(str(p.relative_to(ROOT)))
 archive=base/'xl-terrain-recovery-20261009-hsbc-three-current-role-v2-test-archive/test-v2-original-18.py';assert digest(archive.read_bytes())=='358f3bafd686f23b97c86c0683171873163c67b2388ce83223642f98d915c2d2'
 save(DOC/'scope.json',dict(immutableCurrentRole=ref(ROLE),scopeScript=ref(Path(__file__)),currentReplayInputs=inputs,closedProofAndStagePaths=sorted(set(closed)),historicalManifestAlias=ref(DOC/'preinstallation-manifest.json'),historicalSupersededTestAlias=dict(originalPath='source-scripts/city/government-import/test_hsbc_mounted_visual_panel_accounting_v2_20261009.py',originalSHA256=digest(archive.read_bytes()),verifiedArchive=ref(archive),notCurrentAcceptanceInput=True,currentTest='source-scripts/city/government-import/test_hsbc_mounted_visual_panel_accounting_v3_20261009.py'),globalManifestAndSerializedTerrainMetadataAreLeafBindings=True,noFrozenRefsRewritten=True,qualification='674 explicit complete current replay refs independently byte verified, plus closed source/provider/role/stage assets and screenshots. Original cached terrain acquisition metadata preserves provider hashes/URLs as lineage; do not recursively import unrelated territorial raw caches from whole global manifest/terrain archives. Only v3 test/current-role proof receives current acceptance credit.'))
 print(json.dumps(dict(currentReplayInputs=len(inputs),untrackedInputs=sum(not r['alreadyTracked'] for r in inputs),untrackedMB=sum(r['bytes'] for r in inputs if not r['alreadyTracked'])/1048576,closedProofPaths=len(set(closed)))),flush=True)
if __name__=='__main__':main()
