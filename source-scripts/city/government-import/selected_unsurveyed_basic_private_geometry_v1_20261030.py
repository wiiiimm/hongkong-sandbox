"""Exercise eligible BASIC-only estimates through unchanged production geometry."""
import argparse,subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from wave_multicore_estimated_bases_v4_20261017 import measure

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','proposals','runtime']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()and all(n.startswith('government-xl-')and'/'not in n for n in vars(a).values());refs=[Path(__file__),HERE/'wave_multicore_estimated_bases_v4_20261017.py'];cache={}
 def take(batch,path):
  if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  assert digest(path.read_bytes())==cache[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 proposal=take(a.proposals,base/a.proposals/'summary.json');selection=take(a.runtime,base/a.runtime/'selection.json.gz');runtime=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz');assert len(runtime['rows'])==1
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 rows=[dict(uid=r['uid'],sourceBefore=r['sourceBefore'],update=r['update'])for r in proposal['proposals']if r['uniformBaseCandidate']];assert rows
 for r in rows:assert set(r['update'])=={'base'}and r['sourceBefore']['baseSource']=='terrain-estimated'and r['sourceBefore']['heightSource']=='estimated'
 save(out/'input.json',dict(rows=rows,publication=False));tool=HERE/'wave_private_basic_estimates_v1_20261017.mjs';subprocess.run(['node',str(tool),str(out.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(tool)
 data=read(out/'geometry.json.gz');ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);results=[]
 for r in data['rows']:
  checks=[]
  for part in r['afterParts']:
   terrain=measure(ground,Polygon(part['rings'][0],part['rings'][1:]));roof=part['kind']=='roof';covered=terrain['uncoveredAreaM2']<1e-8;feet=None if roof else part['bottom']<=terrain['minimum']+.002;clear=part['bottom']>terrain['maximum']+.02 if roof else part['top']-terrain['maximum']>1.8
   checks.append(dict(kind=part['kind'],fullTerrainCoverage=covered,baseReachesAllGround=feet,roofOrTopClear=clear,terrain=terrain))
  save(out/(r['uid'].split('/')[1]+'-parts.json'),dict(parts=checks));results.append(dict(uid=r['uid'],allXZExactlyUnchanged=r['allXZExactlyUnchanged'],estimatedHeightUnchanged=r['sourceBefore']['height']==r['privateAfter']['height'],allPartGroundChecksPass=all(t['fullTerrainCoverage']and t['roofOrTopClear']and t['baseReachesAllGround']is not False for t in checks),parts=len(checks)))
 for path,sha in data['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 result=dict(uids=proposal['uids'],rows=results,privateEstimatedBaseChanges=len(rows),allPartGroundChecksPass=all(r['allPartGroundChecksPass']for r in results),productionChanges=0,governmentGeometryChanges=0,installationApproved=False,publication=False,qualification='Actual unchanged production BASIC constructor, complete part/terrain clipping, XZ/height invariants. Only privately estimated base changed; joint original/foreign finite contacts, fallback lifecycle and visual acceptance remain separate.')
 save(out/'summary.json',result);module('private_estimated_basic_geometry',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-production-private-unsurveyed-basic-estimate-geometry',refs,result)
 print(results,flush=True)
if __name__=='__main__':main()
