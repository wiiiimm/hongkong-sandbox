"""Evaluate one guarded unsurveyed BASIC base update with the complete neighbour cohort."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-estimated-base-proposal-v1-20261020';DOC=BASE/BATCH
ENV=BASE/'government-xl-china-ferry-81118-base-diagnostic-v1-20261020';NEI=BASE/'government-xl-china-ferry-current-neighbours-v1-20261020'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [ENV,NEI]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
v=read(ENV/'terrain-envelope.json');b=v['building'];data=read(NEI/'neighbour-inputs.json.gz');assert next(x['building']for x in data['rows']if x['building']['uid']==b['uid'])==b
assert v['missingArea']<1e-7 and v['groundRange']<.5
estimate=dict(uid=b['uid'],objectId=b['objectId'],buildingCSUID=b['buildingCSUID'],previousBase=b['base'],base=v['possibleEstimatedBase'],height=b['height'],baseSource=b['baseSource'],heightSource=b['heightSource'],sourceBaseHeightHKPD=None,sourceTopHeightHKPD=None)
data['estimatedBaseUpdates']=[estimate];save(DOC/'neighbour-inputs.json.gz',data)
save(DOC/'proposal.json',dict(stagedOnly=True,buildings=[estimate],exactTerrainCandidates=data['patches'],terrainEnvelopeReceipt=read(ENV/'result.json')['jobId'],publicationApproved=False))
tool=HERE/'china_ferry_estimated_base_neighbours_v1_20261020.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);report=read(DOC/'neighbour-checks.json');target=next(x for x in report['rows']if x['uid']==b['uid']);assert not target['reasons'];assert target['afterGap'][0]>=-.5 and target['afterGap'][1]<=1
old=read(NEI/'neighbour-checks.json');assert len(report['rows'])==len(old['rows'])
for x,y in zip(report['rows'],old['rows']):
 if x['uid']!=b['uid']:assert x==y
for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
refs.extend([tool,ROOT/'source-scripts/city/island-detail-integration/publish.py'])
result=dict(uids=[b['uid']],target=target,remainingOrdinaryFlags=[x for x in report['rows']if x['reasons']],allOtherRowsUnchanged=True,stagedOnly=True,installationApproved=False,sourceGeometryChanges=0)
module('china_estimate_proposal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'guarded-estimated-basic-base-proposal-neighbour-regression',list(dict.fromkeys(refs)),result)
print(target,flush=True)
