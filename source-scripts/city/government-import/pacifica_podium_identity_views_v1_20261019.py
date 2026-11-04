"""Exact original candidate podium beside both installed neighbouring sources."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-podium-identity-views-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-pacifica-overlap-context-v1-20261019';PAIR=BASE/'government-xl-pacifica-original-assembly-v1-20261019'
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),SRC/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=next(r for r in read(PAIR/'selection.json.gz')['rows']if r['uid']=='landsd/283036:0');source=dict(uid=row['uid'],assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=row['candidate']['entry']['worldBounds'],triangles=row['triangles']);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');components=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']in ['landsd/265478:0','landsd/283034:0']:
    q=p.parent/e['asset'];assert digest(q.read_bytes())==e['sha256'];components.append(dict(uid=e['uid'],assetPath=str(q.relative_to(ROOT)),sourceSHA256=e['sha256'],worldBounds=e['worldBounds'],triangles=e['triangles']));refs.extend([p,q])
 assert len(components)==2;components.sort(key=lambda r:r['uid']);models=[]
 for name,frame,direction in [('whole',None,[.7,.8,1]),('whole-reverse',None,[-.7,.8,-1]),('liberte-edge',[[-1080,0,-5320],[-1045,40,-5170]],[-1,.5,.2]),('mall-join',[[-1075,0,-5235],[-960,45,-5140]],[.7,.6,1])]:models.append(dict(**{**source,'uid':'review/'+name},originalComponents=components,forms=[row['source']['building']],failedSamples=[],reviewFrame=frame,viewDirection=direction))
 tool=HERE/'pacifica_podium_identity_views_v1_20261019.mjs';save(DOC/'input.json',dict(models=models,inputHashes={r['assetPath']:r['sourceSHA256']for r in [source,*components]}));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);report=read(DOC/'render.json');assert len(report['views'])==4 and not report['errors']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([tool,PAIR/'selection.json.gz']);module('pacifica_podium_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-three-podium-identity-context',list(dict.fromkeys(refs)),dict(uids=[source['uid']]+[r['uid']for r in components],views=4,installationApproved=False))
if __name__=='__main__':main()
