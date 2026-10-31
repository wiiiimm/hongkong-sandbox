"""Conditional pair-scope original models against unchanged current terrain."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-private-runtime-v2-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-siu-hong-private-capture-v2-20261021'
def main():
 assert not DOC.exists();_,pins=authenticate(CAP);refs=[Path(__file__),CAP/'result.json'];used={}
 def take(p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k];used[k]=pins[k];refs.append(p);return read(p)
 terrainFolder=BASE/'government-xl-siu-hong-private-terrain-v2-20261021';_,terrainPins=authenticate(terrainFolder);refs.append(terrainFolder/'result.json')
 for name in ['summary.json','terrain-candidates.json']:
  p=terrainFolder/name;assert digest(p.read_bytes())==terrainPins[str(p.relative_to(ROOT))];refs.append(p)
 assert read(terrainFolder/'summary.json')['terrainValidationPassed']
 terrains=read(terrainFolder/'terrain-candidates.json')
 for terrain in terrains:
  assert digest((ROOT/terrain['path']).read_bytes())==terrain['sha256'];refs.append(ROOT/terrain['path']);used[terrain['path']]=terrain['sha256']
 save(DOC/'terrain-candidates.json',terrains)
 selection=take(CAP/'selection.json.gz');inp=take(CAP/'input.json.gz');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256'];forms={}
 for r in selection['rows']:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(p);used[str(p.relative_to(ROOT))]=r['sourceSHA256'];dest=LOCAL/r['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);refs.append(dest);forms[r['uid']]=r['source']
 save(LOCAL/'source-forms.json',forms);save(LOCAL/'conditional-scope.json',inp['conditionalScope']);save(DOC/'selection.json.gz',selection)
 tool=HERE/'siu_hong_current_metrics_v1_20261021.mjs';subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'metrics.json');assert len(report['rows'])==2 and not any(r.get('error')for r in report['rows'])
 for p,h in {**used,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([tool,LOCAL/'runtime-geometry.json.gz',HERE/'china_ferry_current_foundations_v1_20261020.py']);result=dict(uids=[r['uid']for r in selection['rows']],rows=report['rows'],installationApproved=False,geometryChanges=0,conditionalFootprintScope=True);save(DOC/'summary.json',result);module('siu_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'conditional-scope-current-terrain-renderer-diagnostic',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
