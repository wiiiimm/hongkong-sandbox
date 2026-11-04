"""Original IFC assembly views; exact bytes and native placement, no acceptance."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ifc-original-identity-views-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-ifc-original-assembly-support-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
 sources=read(SRC/'input.json')['sources'];models=[]
 def view(r):
  return dict(uid=r['uid'],sourceUid=r['uid'],sourceSHA256=r['sourceSHA256'],assetPath=r['candidate']['path'],worldBounds=r['candidate']['entry']['worldBounds'],triangles=r['candidate']['entry']['triangles'],forms=[x['source']['building']for x in sources])
 mall=next(r for r in sources if r['uid']=='landsd/64856:0');entry=view(mall);entry['originalComponents']=[view(r)for r in sources if r['uid']!=mall['uid']]
 for name,direction,frame in [('whole',[.7,.6,1],None),('mall-front',[1,.4,-.7],mall['candidate']['entry']['worldBounds']),('mall-reverse',[-1,.4,.7],mall['candidate']['entry']['worldBounds'])]:
  m=dict(entry,uid='review/'+name,viewDirection=direction)
  if frame:m['reviewFrame']=frame
  models.append(m)
 save(DOC/'input.json',dict(models=models,inputHashes=pins));tool=HERE/'ifc_original_identity_views_v1_20261019.mjs';subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==3 and not report['errors'];refs=[Path(__file__),tool,SRC/'result.json']
 for path,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==h,path;refs.append(ROOT/path)
 module('ifc_identity_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ifc-exact-original-assembly-identity-views',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in sources],views=3,installationApproved=False))
if __name__=='__main__':main()
