"""Freeze a completed production terrain capture without granting repair acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-harbourfront-tower-drawn-ground-v1-20261021'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
assert not DOC.exists()
p=HERE/'local'/BATCH/'drawn-ground.json.gz';data=read(p)
refs=[Path(__file__),HERE/'harbourfront_tower_drawn_ground_v1_20261021.mjs',p]
for name,h in data['inputHashes'].items():
 assert digest((ROOT/name).read_bytes())==h,name
 refs.append(ROOT/name)
summary=dict(uids=['landsd/118230:0'],triangles=len(data['position'])//9,bounds=data['bounds'],rootCoarseCells=[536,418,541,426],preservesWholeWhampoaCoarseDomain=True,installationApproved=False,qualification='Actual production drawn triangles intersecting the proposed root domain. Full descendants, packed extents, other overlapping patches, finite clipping, source support, complete neighbour regression and browser review remain required; not repair approval.')
save(DOC/'summary.json',summary)
r=module('harbourfront_drawn_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-rendered-whampoa-harbourfront-ground-capture',refs,summary)
print(dict(jobId=r['jobId'],**summary),flush=True)
