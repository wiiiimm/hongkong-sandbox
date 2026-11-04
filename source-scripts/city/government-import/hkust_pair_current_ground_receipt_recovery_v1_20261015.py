"""Freeze completed HKUST capture after its supervisor released the conflicting same-resource lease."""
from pathlib import Path
from run import ROOT,HERE,read,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-hkust-pair-current-ground-v1-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH
lease=read(HERE/'local'/BATCH/'lease.json');assert not reservations.owns(lease);assert not (DOC/'result.json').exists()
g=read(DOC/'ground.json.gz');assert g['startEndInputsVerified'] and g['completeTraversedDrawnGroundFaces']==8388740
paths=[Path(__file__)]
for p,h in g['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
s=read(DOC/'summary.json');assert len(g['originalRimGroundSamples'])==s['samples']==227
module('hkust_recovered_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hkust-current-ground-original-rim-context-v1',paths,{**s,'receiptRecovery':'Numeric capture completed; nested freezer encountered own source-context lease. Supervisor terminal1 and lease released; all capture pins reverified before receipt-only recovery. No numerical replay.'})
print(s,flush=True)
