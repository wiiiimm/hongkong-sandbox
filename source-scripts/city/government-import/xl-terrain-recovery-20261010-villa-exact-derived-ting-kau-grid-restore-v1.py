"""Restore an exact historical derived-grid path from its SHA-identical source copy."""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-villa-exact-derived-ting-kau-grid-restore-v1';DOC=BASE/BATCH
SOURCE=ROOT/'source-scripts/city/tsing-ma/terrain/staged/10-NE-2B/terrain-source-5m.json'
TARGET=ROOT/'source-scripts/city/ting-kau/combined/terrain/staged/10-NE-2B/terrain-source-5m.json'
EXPECTED='881405fe815aae69bdde9ba4ef249866f8d407023e782e10b36bfd892892c441'
CONTEXTS=[ROOT/'source-scripts/city/ting-kau/foundation-candidate/terrain-tsing-ma-ting-kau.json',ROOT/'source-scripts/city/ting-kau/foundation-candidate/hydro-tsing-ma-ting-kau.json']
def references(value):
 if isinstance(value,dict):
  if value.get('path')==str(TARGET.relative_to(ROOT)):yield value
  for v in value.values():yield from references(v)
 elif isinstance(value,list):
  for v in value:yield from references(v)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),bytes=p.stat().st_size)
def main():
 assert not DOC.exists();raw=SOURCE.read_bytes();assert len(raw)==427209 and digest(raw)==EXPECTED
 bindings=[]
 for p in CONTEXTS:
  rows=list(references(read(p)));assert len(rows)==1 and rows[0]['sha256']==EXPECTED and rows[0]['sheet']=='10-NE-2B';bindings.append(dict(context=ref(p),originalFrozenReference=rows[0]))
 if TARGET.exists():assert TARGET.read_bytes()==raw
 else:TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_bytes(raw)
 assert TARGET.read_bytes()==raw
 out=dict(uids=['landsd/89917:0'],files=[ref(TARGET)],exactExistingCopy=ref(SOURCE),frozenContexts=bindings,exactOriginalBytesRestored=True,modelGeometryChanges=0,terrainGeometryChanges=0,sourceOrClosureRulesChanged=False,qualification='Exact missing historical derived path restored only because both frozen terrain/hydro contexts bind the identical SHA of an existing 427209-byte source copy. No reconstruction, changed geometry, new acceptance or provenance exemption.')
 save(DOC/'restored-inputs.json',out)
 s=importlib.util.spec_from_file_location('derived_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'villa-exact-derived-ting-kau-grid-restore-v1',[Path(__file__),SOURCE,TARGET,*CONTEXTS],out)
if __name__=='__main__':main()
