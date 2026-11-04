"""Prove complete baseline occlusion of an unchanged retained BASIC canopy."""
from pathlib import Path
import numpy as np
from shapely.geometry import MultiPoint,Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from wave_estimated_bases_proposal_v1_20261017 import measure
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-apex222887-source-context-v1-20261018';BATCH='government-xl-apex222887-complete-burial-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json',HERE/'wave_estimated_bases_proposal_v1_20261017.py',HERE/'xl-final-script-pass.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 g=read(PRIOR/'geometry.json.gz')['rows'][0];v=np.asarray(g['position']).reshape(-1,3);t=v[np.asarray(g['index']).reshape(-1,3)];hull=MultiPoint(v[:,[0,2]]).convex_hull;b=g['sourceBefore'];final=module('apex_canopy_whole_foundation',HERE/'xl-final-script-pass.py');out={}
 for mode,batch in [('before','government-xl-apex227942-current-capture-v3-20261017'),('after','government-xl-apex227942-original-terrain-capture-v3-20261018')]:
  p=HERE/'local'/batch/'runtime-geometry.json.gz';ground=np.asarray(read(p)['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);refs.append(p);surface=measure(ground,hull);f=final.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));out[mode]=dict(foundation=f,completeHullTerrain=surface,maximumGeometryY=float(v[:,1].max()),globalMinimumTerrainAboveAllGeometryM=surface['minimum']-float(v[:,1].max()))
 save(DOC/'complete-context.json.gz',out)
 before=out['before'];proof=before['completeHullTerrain']['uncoveredAreaM2']<1e-8 and before['globalMinimumTerrainAboveAllGeometryM']>.5
 summary=dict(uid=b['uid'],faces=len(t),allBaselineGeometryStrictlyBelowGround=proof,baselineMinimumSeparationM=before['globalMinimumTerrainAboveAllGeometryM'],beforeBuried=out['before']['foundation']['fullyBuriedTriangles'],afterBuried=out['after']['foundation']['fullyBuriedTriangles'],fullAcceptance=False,qualification='Whole convex-hull linear-surface bound proves baseline invisibility if true; does not approve source identity, suppression, terrain seams or publication.')
 save(DOC/'summary.json',summary);print(summary,flush=True)
 result=module('apex_canopy_whole_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-retained-canopy-whole-baseline-occlusion-v1',list(set(refs)),dict(uids=[b['uid'],'landsd/227942:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
