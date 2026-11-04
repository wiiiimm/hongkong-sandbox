"""Authenticate the complete current scope and archive actual renderer terrain."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,digest,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-drawn-parent-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();scope=BASE/'government-xl-central-piers-current-scope-v1-20261021';_,pins=authenticate(scope);p=scope/'scope.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
tool=HERE/'central_piers_drawn_parent_v1_20261021.mjs';subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool)],cwd=ROOT,check=True,timeout=900)
p=HERE/'local'/BATCH/'drawn-ground.json.gz';data=read(p);refs=[Path(__file__),tool,scope/'result.json',scope/'scope.json',p]
for name,h in data['inputHashes'].items():assert digest((ROOT/name).read_bytes())==h;refs.append(ROOT/name)
result=dict(uids=['landsd/213352:0','landsd/285475:0'],triangles=len(data['position'])//9,bounds=data['bounds'],installationApproved=False,qualification='Actual production makeTerrain drawn triangles intersecting the complete proposed replacement-child bounds; all native child faces retained. Not raster-resampled terrain or repair approval.')
save(DOC/'summary.json',result);r=module('pier_drawn_parent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-complete-drawn-parent-terrain',refs,result);print(r['jobId'],flush=True)
