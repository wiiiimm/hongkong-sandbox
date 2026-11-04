"""Retain failed terrain candidate evidence; not a source rejection."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-murray-house-failed-terrain-context-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)]
for name in ['government-xl-murray-house-original-policy-v2-20261021','government-xl-murray-house-form-regression-v2-20261021']:
 receipt,pins=authenticate(BASE/name);p=BASE/name/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/name/'result.json',p])
log=Path('/tmp/murray-house-private-v3.log').read_bytes();assert b'Owned terrain core intersects a protected neighbour footprint' in log
DOC.mkdir(parents=True);(DOC/'private-v3-terminal.log').write_bytes(log)
refs.append(HERE/'murray_house_private_terrain_v3_20261021.py')
result=dict(uids=['landsd/61216:0'],installationApproved=False,permanentRejection=False,sourceGeometryChanges=0,reason='V2 neighbour-distance guard raised terrain inside owned core; V3 explicitly rejected overlapping 1m core and neighbour margin.',nextStep='Test V4 smaller source collar and core-to-neighbour distance transition; all original acceptance and visual checks retained.')
module('murray_failed_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'terrain-candidate-failure-context',refs,result)
