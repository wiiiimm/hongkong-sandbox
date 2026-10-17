"""Enumerate and restore every historical Ting Kau derived grid from identical saved bytes."""
from pathlib import Path
import importlib.util,subprocess
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-villa-exact-derived-ting-kau-grid-batch-restore-v2';DOC=BASE/BATCH
PREFIX='source-scripts/city/ting-kau/combined/terrain/staged/'
CONTEXTS=[ROOT/'source-scripts/city/ting-kau/foundation-candidate/terrain-tsing-ma-ting-kau.json',ROOT/'source-scripts/city/ting-kau/foundation-candidate/hydro-tsing-ma-ting-kau.json']
def refs(v):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str) and v['path'].startswith(PREFIX) and v['path'].endswith('/terrain-source-5m.json'):
   assert len(v['sha256'])==64;yield v
  for x in v.values():yield from refs(x)
 elif isinstance(v,list):
  for x in v:yield from refs(x)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),bytes=p.stat().st_size)
def main():
 assert not DOC.exists();expected={};bindings=[]
 for p in CONTEXTS:
  rows=list(refs(read(p)));assert len(rows)==5 and len({r['path']for r in rows})==5
  for r in rows:
   if r['path']in expected:assert expected[r['path']]==r
   expected[r['path']]=r
  bindings.append(dict(context=ref(p),completeFrozenSourceGrids=rows))
 assert len(expected)==5
 files=[ROOT/p for p in subprocess.check_output(['rg','--files','-uuu','source-scripts/city'],cwd=ROOT,text=True).splitlines()if p.endswith('/terrain-source-5m.json')];planned=[]
 for path,row in sorted(expected.items()):
  target=ROOT/path;assert target.parent.name==row['sheet']
  matches=[p for p in files if p.parent.name==row['sheet'] and digest(p.read_bytes())==row['sha256']]
  assert matches,'No SHA-identical saved original for '+path
  source=min(matches,key=lambda p:len(str(p)));raw=source.read_bytes()
  if target.exists():assert target.read_bytes()==raw
  planned.append((source,target,raw))
 # All five references and all saved copies are proved before writing any missing path.
 restored=[]
 for source,target,raw in planned:
  existed=target.exists()
  if not existed:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  assert target.read_bytes()==raw
  restored.append(dict(**ref(target),exactExistingCopy=ref(source),alreadyPresent=existed,originalFrozenReference=expected[str(target.relative_to(ROOT))],exactOriginalBytesRestored=True));print(target.parent.name,len(raw),'EXACT',flush=True)
 out=dict(uids=['landsd/89917:0'],completeExpectedGridCount=5,files=restored,frozenContexts=bindings,allEnumeratedOriginalFilesRestored=True,remaining=[],modelGeometryChanges=0,terrainGeometryChanges=0,numericalExceptions=0,sourceOrClosureRulesChanged=False,qualification='All five frozen foundation terrain/hydro sourceGrids enumerated and each missing historical path restored only from independently SHA-identical saved bytes. No reconstruction, geometry change, new acceptance or provenance exemption.')
 save(DOC/'restored-inputs.json',out);s=importlib.util.spec_from_file_location('grid_batch_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'villa-exact-derived-ting-kau-complete-grid-batch-restore-v2',[Path(__file__),*CONTEXTS,*[p for source,target,raw in planned for p in [source,target]]],out)
if __name__=='__main__':main()
