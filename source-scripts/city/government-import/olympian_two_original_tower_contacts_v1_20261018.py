"""Actual original tower lower-rim versus original podium, diagnostic only."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_tin_point_diagnostic import indexed_surface,point_heights
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-restored-components-v2-20261018';CAP=BASE/'government-xl-olympian-two-source-local-terrain-20261008';BATCH='government-xl-olympian-two-original-tower-contacts-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=read(CAP/'selection.json.gz')['rows'][0];asset=ROOT/selection['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==selection['sourceSHA256'];podium=decode_original_world_triangles(raw);surface=indexed_surface(podium);results=[]
 for row in read(PRIOR/'restored.json')['rows']:
  tri=decode_original_world_triangles((ROOT/row['assetPath']).read_bytes());v=np.unique(tri.reshape(-1,3),axis=0);points=v[v[:,1]<=v[:,1].min()+.35];_,_,heights=point_heights(points,surface);finite=np.isfinite(heights);gap=points[:,1]-heights
  samples=[dict(point=p.tolist(),podiumHeight=float(h)if np.isfinite(h)else None,gap=float(d)if np.isfinite(d)else None)for p,h,d in zip(points,heights,gap)];out=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],samples=len(points),missing=int((~finite).sum()),contacts=int((finite&(gap>=-.1)&(gap<=.1)).sum()),minGap=float(gap[finite].min())if finite.any()else None,maxGap=float(gap[finite].max())if finite.any()else None,originalBounds=row['worldBounds']);save(DOC/(row['uid'].split('/')[1]+'-samples.json.gz'),dict(summary=out,points=samples));results.append(out);print(out,flush=True)
 save(DOC/'summary.json',dict(rows=results,podiumUID=selection['uid'],podiumSHA256=selection['sourceSHA256'],fullAcceptance=False,qualification='Every unique original vertex in lowest0.35m band against original podium height surface. Diagnostic only: no full lower-floor coverage, identity or foundation approval.'))
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins],CAP/'selection.json.gz',asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_tin_point_diagnostic.py'];out=module('olympian_actual_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-original-tower-low-rim-podium-contact-v1',refs,dict(uids=[x['uid']for x in results],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
