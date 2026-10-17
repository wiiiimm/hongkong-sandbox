"""Bind identical complete current model/ground arrays to historical numeric inputs, not approvals."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-villa-current-geometry-rebind-v1-20261015';OLD=B/'government-xl-villa-five-original-coupled-physical-v3-20261010';NEW=B/'government-xl-villa-five-current-physical-v4-20261015'
def main():
 assert not DOC.exists();paths=[Path(__file__)];reports=[]
 for d in [OLD,NEW]:
  receipt=read(d/'result.json');paths.append(d/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  p=HERE/'local'/d.name/'runtime-geometry.json.gz';assert {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} in receipt['evidenceRefs'];paths.append(p);reports.append(read(p))
 rows=[]
 for r in reports[1]['rows']:
  o=next(x for x in reports[0]['rows'] if x['uid']==r['uid']);fields={}
  for k in ['position','index','drawnGroundGeometry']:
   a,b=np.asarray(o[k]),np.asarray(r[k]);assert np.array_equal(a,b);fields[k]={'shape':list(a.shape),'numericValuesExactlyEqual':True,'canonicalFloat64SHA256':digest(a.astype('<f8').tobytes())}
  rows.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'fields':fields})
 for p,h in reports[1]['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 patchpath=ROOT/read(NEW/'terrain-candidates.json')[0]['path'];patch=read(patchpath);a=np.asarray(patch['nativeMesh']['position']).reshape(-1,3);scope=read(NEW/'full-current-scope.json');lo,hi=np.array(scope['wholeParentBounds'][:2]),np.array(scope['wholeParentBounds'][2:]);bounds=[]
 for v in [a,a.astype(np.float32).astype(float)]:
  low=v[:,[0,2]].min(0);high=v[:,[0,2]].max(0);assert (low>=lo).all() and (high<=hi).all();bounds.append([low.tolist(),high.tolist()])
 DOC.mkdir();out={'uids':[r['uid'] for r in rows],'rows':rows,'wholePackedTerrainWithinParentExtent':bounds,'currentSourceAndGroundArraysExactlyEqualHistorical':True,'historicalApprovalsTransferred':False,'fullAcceptance':False,'qualification':'Exact full source/index/drawn-ground equality permits reuse of applicable unchanged numeric calculations only. Current source role, corrected canopy collision, affected scope, module contracts and browser/publication acceptance remain separate.'};save(DOC/'rebind.json',out);paths.extend([patchpath,NEW/'full-current-scope.json',NEW/'terrain-candidates.json'])
 module('villa_rebind_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'complete-current-five-original-and-ground-exact-array-rebind-v1',paths,out)
if __name__=='__main__':main()
