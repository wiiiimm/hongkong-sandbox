"""Attribute all unresolved contacts to exact drawn terrain or original podium faces."""
from pathlib import Path
import subprocess
from collections import Counter
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-contact-context-v1-20261017';BATCH='government-xl-wave-verdant-surface-hits-v1-20261017';DOC=BASE/BATCH
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 DOC.mkdir();tool=HERE/'wave_verdant_surface_hits_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);data=read(DOC/'hits.json.gz');rows=[]
 for row in data['rows']:
  top={k:(v[-1]if v else None)for k,v in row['surfaces'].items()};choices=[(top[k]['height'],k)for k in ['candidateGround','originalPodium']if top[k]is not None];height,provider=max(choices);assert abs(row['position'][1]-height-row['gap'])<1e-7;rows.append(dict(position=row['position'],reason=row['reason'],gap=row['gap'],topProvider=provider,top=top))
 summary=dict(samples=len(rows),providers=dict(Counter(x['reason']+'/'+x['topProvider']for x in rows)),candidateTopFaces=sorted({x['top']['candidateGround']['faceIndex']for x in rows if x['reason']=='support-above-rim'and x['topProvider']=='candidateGround'}),fullAcceptance=False)
 save(DOC/'attribution.json.gz',dict(rows=rows));save(DOC/'summary.json',summary)
 for p,h in data['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 out=module('verdant_surface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-verdant-unresolved-drawn-surface-attribution-v1',list(set(refs)),dict(uids=['landsd/195000:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(summary,flush=True);print(out['jobId'],flush=True)
if __name__=='__main__':main()
