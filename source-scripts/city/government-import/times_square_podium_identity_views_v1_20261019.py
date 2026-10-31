"""Complete original Times Square podium, both towers and original footprint."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-podium-identity-views-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-times-square-ordinary-validation-v2-20261019';PAIR=BASE/'government-xl-times-square-original-assembly-v1-20261018'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),SRC/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(PAIR/'selection.json.gz')['rows'];pod=next(r for r in rows if r['uid']=='landsd/233901:0')
 def source(r):return dict(uid=r['uid'],assetPath=r['candidate']['path'],sourceSHA256=r['sourceSHA256'],worldBounds=r['candidate']['entry']['worldBounds'],triangles=r['triangles'])
 components=[source(r)for r in rows if r!=pod];models=[]
 for name,frame,direction in [('whole',None,[.7,.8,1]),('whole-reverse',None,[-.7,.8,-1]),('outer-platform',[[2280,0,935],[2395,25,990]],[.3,.7,-1])]:
  models.append(dict(**{**source(pod),'uid':'review/'+name},originalComponents=components,forms=[pod['source']['building']],failedSamples=[],reviewFrame=frame,viewDirection=direction))
 tool=HERE/'times_square_podium_identity_views_v1_20261019.mjs';save(DOC/'input.json',dict(models=models,inputHashes={r['candidate']['path']:r['sourceSHA256']for r in rows}));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==3 and not report['errors']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(tool);module('times_podium_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-original-podium-and-outer-platform-views',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],views=3,installationApproved=False))
if __name__=='__main__':main()
