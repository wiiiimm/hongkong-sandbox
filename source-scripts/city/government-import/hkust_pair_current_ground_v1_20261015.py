"""Capture actual current ground around the unchanged HKUST pair, retaining old rim failures."""
from pathlib import Path
import subprocess,sys,uuid,json
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hkust-pair-current-ground-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OLD=BASE/'government-xl-hkust-uncovered-target-partition-v1-20261015/result.json';PACKET=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014';JS=HERE/'hkust_pair_current_ground_capture_v1_20261015.mjs'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 if '--owned' not in sys.argv:
  assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('hkust-ground-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'lease.json',json.loads(json.dumps(lease,default=str)))
  try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'lease.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
  finally:
   if reservations.owns(lease):assert reservations.release(lease)['ok']
  return
 old=read(OLD);pins={r['path']:r['sha256'] for r in old['evidenceRefs']};resultp=PACKET/'two-original-scope-interface-output-v1/result.json';assert ref(resultp)['sha256']==pins[str(resultp.relative_to(ROOT))];r=read(resultp);paths=[OLD,resultp,JS,Path(__file__)];vertices=[]
 for a in r['arrayRefs']:
  p=ROOT/a['path'];assert ref(p)==a;vertices.extend(np.array(read(p)['completeOrderedOriginalTriangles']).reshape(-1,3).tolist());paths.append(p)
 v=np.array(vertices);assert len(v)==13598*3;DOC.mkdir();save(DOC/'source-input.json.gz',{'sourceWorlds':[{'label':'providerOriginal','position':v.reshape(-1).tolist()}],'sourceTuples':r['sourceTuples']})
 samples=r['all227OldInterfaceNegativesVerbatim']['interface']['strictLowRim']['failed'];assert len(samples)==227
 save(DOC/'plan.json',{'uid':r['uids'][0],'completeSourceFaces':13598,'sourceInput':ref(DOC/'source-input.json.gz'),'expectedManifest':ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256'],'providerOriginalFaceBounds':[v.min(0).tolist(),v.max(0).tolist()],'originalRimSamples':samples,'evidenceRefs':[ref(p) for p in paths]})
 with (DOC/'capture.log').open('w') as log:subprocess.run(['node',str(JS),str((DOC/'plan.json').relative_to(ROOT)),str((DOC/'ground.json.gz').relative_to(ROOT))],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
 g=read(DOC/'ground.json.gz');rows=g['originalRimGroundSamples'];gaps=[s['currentTerrainGap'] for s in rows];summary={'uids':r['uids'],'samples':len(rows),'minimumCurrentGroundGapM':min(gaps),'maximumCurrentGroundGapM':max(gaps),'missingCurrentHeight':sum(s['currentTerrainHeight'] is None for s in rows),'groundContactWithinExisting01M':sum(abs(x)<=.1 for x in gaps),'buriedBeyondExisting05M':sum(x<-.5 for x in gaps),'aboveGroundBeyondExisting01M':sum(x>.1 for x in gaps),'fullAcceptance':False,'providerOriginalOnlyNotPlacedFourWorldProof':True,'nextStep':'Use ground evidence to distinguish unsupported original rims from podium-only mismatches; retain all original failures and run whole physical/identity gates independently.'};save(DOC/'summary.json',summary)
 for p,h in g['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 module('hkust_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hkust-current-ground-original-rim-context-v1',paths,summary);print(summary,flush=True)
if __name__=='__main__':main()
