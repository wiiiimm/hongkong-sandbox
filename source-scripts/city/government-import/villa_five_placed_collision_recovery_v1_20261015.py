"""Persist completed numeric evidence after the producer released its nested lease."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-five-placed-canopy-collision-v1-20261015';DOC=B/NAME
assert not (DOC/'result.json').exists()
capture=read(DOC/'placed.json.gz');summary=read(DOC/'summary.json');rows=read(DOC/'contacts.json.gz')['rows']
assert len(rows)==15 and len(summary['rows'])==15
for a,b in zip(rows,summary['rows']):
 assert a['uid']==b['uid'] and a['mode']==b['mode'] and a['completeFaces']==b['completeFaces'] and len(a['contacts']['contacts'])==b['contacts']==0
for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
old=B/'government-xl-villa-private-canopy-collision-v2-20261015';receipt=read(old/'result.json');rendered=old/'rendered.json';pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']};assert digest(rendered.read_bytes())==pins[str(rendered.relative_to(ROOT))]
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
shutil.copyfile('/tmp/villa-five-placed-canopy-collision-v1-20261015.log',DOC/'producer-terminal.log')
save(DOC/'recovery.json',dict(reason='Producer completed all numeric comparisons but attempted freezer while holding its same source-context lease. Producer finally released; recovery invokes ordinary guarded freezer.',numericReplay=False,currentInputHashesVerified=True,originalProducerPreserved=True))
paths=[Path(__file__),HERE/'villa_five_placed_canopy_collision_v1_20261015.py',rendered,old/'result.json']+[ROOT/p for p in capture['inputHashes']]
module('villa_placed_recovery_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'complete-placed-original-canopy-surfaces',paths,summary)
