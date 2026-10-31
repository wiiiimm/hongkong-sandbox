"""Reproduce exact runtime sampler failures from the saved actual scene capture."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-actual-samples-v2-20261021';DOC=BASE/BATCH;CAP=BASE/'government-xl-illumination-inset-runtime-v2-20261021'
assert not DOC.exists();receipt,pins=authenticate(CAP);rt=HERE/'local'/CAP.name/'runtime-geometry.json.gz';metrics=CAP/'metrics.json';refs=[Path(__file__),CAP/'result.json',rt,metrics]
for p in [rt,metrics]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
assert read(rt)['rows'][0]['uid']=='landsd/258737:0';DOC.mkdir();tool=HERE/'china_merchants_actual_samples_v1_20261021.mjs';subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(rt),str(DOC/'samples.json')],cwd=ROOT,check=True)
r=read(DOC/'samples.json');m=read(metrics)['rows'][0];assert r['checks']==m['checks']and r['missing']==m['missingTerrain']and abs(r['minGap']-m['minSurfaceGap'])<1e-12
refs.extend([tool,ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/exact-finite-triangle-projection.js'])
summary=dict(uids=['landsd/258737:0'],sourceSHA256=r['sourceSHA256'],checks=r['checks'],missing=r['missing'],minimumGapM=r['minGap'],failedSamples=len(r['rows']),sourceGeometryChanges=0,installationApproved=False)
module('china_actual_samples_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-actual-renderer-sample-residuals',refs,summary);print(summary,flush=True)
