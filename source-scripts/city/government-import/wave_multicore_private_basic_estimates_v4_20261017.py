"""Validate private corrected unsurveyed forms through actual production geometry."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from wave_estimated_bases_proposal_v1_20261017 import measure
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-multicore-estimated-bases-v4-20261017';CAP=BASE/'government-xl-wave-verdant-multicore-ground-capture-v4-20261017';BATCH='government-xl-wave-multicore-private-basic-estimates-v4-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json',HERE/'wave_estimated_bases_proposal_v1_20261017.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 rows=[]
 for r in read(PRIOR/'proposals.json')['rows']:
  if r['uniformBaseCandidate']:update=dict(base=r['proposedBase'])
  else:assert r['uid']=='landsd/268957:0'and r['sourceBefore']['kind']=='roof';update=dict(foundationBase=r['proposedBase'])
  rows.append(dict(uid=r['uid'],sourceBefore=r['sourceBefore'],update=update))
 save(DOC/'input.json',dict(rows=rows,publication=False));tool=HERE/'wave_private_basic_estimates_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);data=read(DOC/'geometry.json.gz');ground=np.array(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);summary=[]
 for r in data['rows']:
  parts=[]
  for p in r['afterParts']:
   terrain=measure(ground,Polygon(p['rings'][0],p['rings'][1:]));topClearance=p['top']-terrain['maximum'];cover=terrain['uncoveredAreaM2']<1e-8;feet=p['bottom']<=terrain['minimum']+.002 if p['kind']!='roof'else None;clear=p['bottom']>terrain['maximum']+.02 if p['kind']=='roof'else topClearance>1.8;parts.append(dict(kind=p['kind'],fullTerrainCoverage=cover,baseReachesAllGround=feet,roofOrTopClear=clear,topClearanceM=topClearance,terrain=terrain))
  save(DOC/(r['uid'].split('/')[1]+'-parts.json'),dict(parts=parts));summary.append(dict(uid=r['uid'],allXZExactlyUnchanged=r['allXZExactlyUnchanged'],roofPartsExactlyUnchanged=r['roofPartsExactlyUnchanged'],allPartGroundChecksPass=all(p['fullTerrainCoverage']and p['roofOrTopClear']and p['baseReachesAllGround']is not False for p in parts),parts=len(parts)));print(summary[-1],flush=True)
 for p,h in data['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.append(tool);save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,publication=False,qualification='Private BASIC-only estimate correction; native assets untouched. Roof/footprint and complete-part terrain checks retained. Joint neighbour, collision and visual review still required.'))
 out=module('wave_private_basic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'production-private-basic-estimate-and-post-grounding-checks-v1',list(set(refs)),dict(uids=[r['uid']for r in rows],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
