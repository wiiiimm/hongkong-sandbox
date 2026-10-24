"""Exact full-facet fixed-band diagnostic for two residual original Tower 3A components."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-tower3a-finite-host-band-v1-20261021';DOC=BASE/BATCH
FOUND=BASE/'government-xl-tko-complete-foundations-v2-20261021';JOIN=BASE/'government-xl-tko-residual-component-joins-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={};summary=[]
 for folder in [FOUND,JOIN]:
  _,bound=authenticate(folder);pins[folder]=bound;refs.append(folder/'result.json')
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 for mode in ['original','literal','leftF32','balancedF32']:
  inp=take(FOUND,FOUND/mode/'32024:0/input.json.gz');r=inp['rows'][0];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
  joins=take(JOIN,JOIN/mode/'32024:0-joins.json.gz');assert digest(t.tobytes())==joins['sourceWorldSHA256']
  excluded={i for c in joins['components']for i in c['componentFaces']};hosts=sorted(set(range(len(t)))-excluded);rows=[]
  for f in sorted(excluded):
   proof=verify(t[f],t[hosts]);rows.append(dict(sourceFace=f,proof=proof));print(mode,f,proof['wholeFacetAssociated'],flush=True)
  save(DOC/(mode+'.json.gz'),dict(sourceWorldSHA256=digest(t.tobytes()),hostFaceIds=hosts,excludedFaceIds=sorted(excluded),rows=rows,installationApproved=False))
  summary.append(dict(mode=mode,faces=len(rows),wholeFacetAssociated=sum(x['proof']['wholeFacetAssociated']for x in rows)))
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['china_ferry_current_foundations_v1_20261020.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_slab_projection_coverage_20261010.py'])
 result=dict(uids=['landsd/32024:0'],rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Exact finite association only; excludes both residual components from hosts. Host grounding, source role, physical attachment and installation remain unapproved; no band changes.')
 save(DOC/'summary.json',result);module('tko_finite_band_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'residual-original-full-facet-finite-host-fixed-band',refs,result)
if __name__=='__main__':main()
