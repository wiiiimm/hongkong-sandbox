"""Complete unchanged original pair views and labelled interface crops, no approval."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-266146-original-views-v3-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-times-square-266146-failed-face-context-v1-20261019';CAP=BASE/'government-xl-times-square-original-assembly-v1-20261018'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows={r['uid']:r for r in read(CAP/'selection.json.gz')['rows']};tower=rows['landsd/266146:0'];pod=rows['landsd/233901:0'];fail=read(SRC/'faces.json')['failedSamples']
 def source(r):return dict(uid=r['uid'],assetPath=r['candidate']['path'],sourceSHA256=r['sourceSHA256'],worldBounds=r['candidate']['entry']['worldBounds'],triangles=r['triangles'])
 points=np.asarray([r['vertices']for r in read(SRC/'faces.json')['incidentFaces']]);frame=[(points.min((0,1))-np.array([5,4,5])).tolist(),(points.max((0,1))+np.array([5,10,5])).tolist()]
 models=[]
 for name,frame,direction,marked in [('whole',None,[.7,.8,1],False),('whole-reverse',None,[-.7,.8,-1],False),('lower-front',frame,[.7,.4,1],True),('lower-reverse',frame,[-.7,.4,-1],True)]:
  models.append(dict(**{**source(tower),'uid':'review/'+name},originalComponents=[source(pod)],forms=[] if frame else [tower['source']['building'],pod['source']['building']],failedSamples=fail if marked else [],reviewFrame=frame,viewDirection=direction))
 tool=HERE/'times_square_original_views_v1_20261019.mjs';save(DOC/'input.json',dict(models=models,inputHashes={str((ROOT/p).relative_to(ROOT)):h for p,h in pins.items()if p in [tower['candidate']['path'],pod['candidate']['path']]}))
 subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==4 and not report['errors']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(tool);module('olympian_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-assembly-complete-and-interface-views',list(dict.fromkeys(refs)),dict(uids=list(rows),views=4,installationApproved=False))
if __name__=='__main__':main()
