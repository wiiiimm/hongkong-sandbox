"""Inspect complete original low-rim faces; no ground-support or publication approval."""
from pathlib import Path
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-low-rim-views-v1-20261019';DOC=BASE/BATCH
SOURCE=BASE/'government-xl-kai-tak-cruise-extent-views-v1-20261019';FACES=BASE/'government-xl-kai-tak-cruise-contact-faces-v1-20261019';CAP=BASE/'government-xl-kai-tak-cruise-expanded-parent-v3-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SOURCE,FACES,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(CAP/'selection.json.gz')['rows'][0];faces=read(FACES/'faces.json');rim=[f for f in faces['faces']if f['globalLowRim']];assert len(rim)==129 and faces['sourceSHA256']==row['sourceSHA256'];t=np.asarray([f['vertices']for f in rim]);lo=t.min((0,1));hi=t.max((0,1));frame=[(lo-[4,3,4]).tolist(),(hi+[4,5,4]).tolist()]
 models=[]
 for name,direction,viewframe in [('rim-front',[1,.45,1],frame),('rim-reverse',[-1,.45,-1],frame),('rim-context',[.7,.8,1],None)]:
  models.append(dict(uid='review/'+name,label='original global low-rim faces',assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=row['candidate']['entry']['worldBounds'],triangles=row['triangles'],forms=[row['source']['building']],reviewFrame=viewframe,viewDirection=direction,highlightFaces=t.tolist()))
 save(DOC/'low-rim.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],globalMinimumY=faces['globalMinimumY'],sourceFaceIds=[f['faceId']for f in rim],bounds=[lo.tolist(),hi.tolist()],rawFaceRecords=rim,installationApproved=False))
 tool=HERE/'kai_tak_cruise_low_rim_views_v1_20261019.mjs';refs.append(tool);hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};save(DOC/'input.json',dict(models=models,inputHashes=hashes))
 subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==3 and not report['errors']
 for p,h in {**hashes,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('ocean_lowrim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-complete-original-low-rim-views',list(dict.fromkeys(refs)),dict(uids=[row['uid']],lowRimFaces=129,installationApproved=False))
if __name__=='__main__':main()
