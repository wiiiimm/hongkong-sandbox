"""Exact source/terrain context for the retained estimated canopy; no geometry edits."""
from pathlib import Path
import numpy as np,subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from wave_estimated_bases_proposal_v1_20261017 import measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-apex222887-source-context-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();prior=BASE/'government-xl-apex227942-current-parent-neighbours-v1-20261018';r=read(prior/'result.json');pins={};refs=[Path(__file__),prior/'result.json',HERE/'wave_estimated_bases_proposal_v1_20261017.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 b=next(x['building']for x in read(prior/'neighbour-inputs.json.gz')['rows']if x['building']['uid']=='landsd/222887:0');poly=Polygon(b['rings'][0],b['rings'][1:]);metrics={}
 for mode,batch in [('before','government-xl-apex227942-current-capture-v3-20261017'),('after','government-xl-apex227942-original-terrain-capture-v3-20261018')]:
  p=HERE/'local'/batch/'runtime-geometry.json.gz';g=read(p)['rows'][0];refs.append(p);terrain=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);metrics[mode]=measure(terrain,poly)
 source=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];metrics['originalBuilding']=measure(source,poly)
 save(DOC/'surface-context.json.gz',dict(uid=b['uid'],sourceBefore=b,measurements=metrics,fullAcceptance=False))
 save(DOC/'input.json',dict(rows=[dict(uid=b['uid'],sourceBefore=b,update={})]))
 tool=HERE/'wave_private_basic_estimates_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);geometry=read(DOC/'geometry.json.gz');parts=geometry['rows'][0]['beforeParts'];summary={k:{f:v[f]for f in ['minimum','maximum','footprintAreaM2','uncoveredAreaM2','overlapAreaM2']}for k,v in metrics.items()};summary['parts']=[{k:p.get(k)for k in ['kind','bottom','top','illustrative']}for p in parts];summary['fullAcceptance']=False
 for p,h in geometry['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 save(DOC/'summary.json',summary);print(summary,flush=True)
 out=module('apex_canopy_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-retained-canopy-complete-source-terrain-context-v1',list(set(refs)),dict(uids=[b['uid'],'landsd/227942:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
