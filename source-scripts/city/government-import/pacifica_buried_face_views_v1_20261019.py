"""Render the two exactly identified original Tower 3 compound-burial faces."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-buried-face-views-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-pacifica-four-mode-foundations-v1-20261019';CAP=BASE/'government-xl-pacifica-original-assembly-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows={r['uid']:r for r in read(CAP/'selection.json.gz')['rows']};tower=rows['landsd/75351:0'];pod=rows['landsd/283036:0'];faces=read(SRC/'75351:0-original.json')['buriedFaces'];assert [f['faceId']for f in faces]==[3028,3029];points=np.asarray([f['vertices']for f in faces]);frame=[(points.min((0,1))-[5,5,5]).tolist(),(points.max((0,1))+[5,9,5]).tolist()];samples=[dict(position=p.tolist())for p in points.reshape(-1,3)]+[dict(position=p.tolist())for p in points.mean(1)]
 def source(r):return dict(uid=r['uid'],assetPath=r['candidate']['path'],sourceSHA256=r['sourceSHA256'],worldBounds=r['candidate']['entry']['worldBounds'],triangles=r['triangles'])
 models=[dict(**{**source(tower),'uid':'review/'+name},originalComponents=[source(pod)],forms=[],failedSamples=samples,reviewFrame=frame,viewDirection=direction)for name,direction in [('buried-front',[.7,.4,1]),('buried-reverse',[-.7,.4,-1])]]
 tool=HERE/'pacifica_buried_face_views_v1_20261019.mjs';save(DOC/'input.json',dict(models=models,inputHashes={r['candidate']['path']:r['sourceSHA256']for r in [tower,pod]}));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==2 and not report['errors']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(tool);module('pacifica_buried_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-upward-faces-compound-context',list(dict.fromkeys(refs)),dict(uids=[tower['uid'],pod['uid']],faceIds=[3028,3029],views=2,installationApproved=False))
if __name__=='__main__':main()
