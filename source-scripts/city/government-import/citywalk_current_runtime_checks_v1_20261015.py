"""Rebind exact unchanged Citywalk form and run current loader/runtime metrics."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-current-runtime-checks-v1-20261015';DOC=BASE/BATCH
OLD=BASE/'government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue';STAGE=HERE/'accepted/government-xl-citywalk-source-20261004';UID='landsd/134332:0'
def main():
 assert not DOC.exists();selection=read(OLD/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];assert row['uid']==UID
 tile=ROOT/'3d-viewer'/row['source']['tile'];matches=[b for b in read(tile)['buildings']if b['uid']==UID];assert matches==[row['source']['building']]
 row['source']['tileSHA256']=digest(tile.read_bytes());selection['manifestSHA256']=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
 claim=reservations.claim('citywalk-runtime-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'selection.json.gz',selection);save(DOC/'source-forms.json',{UID:row['source']});save(DOC/'terrain-candidates.json',read(OLD/'terrain-candidates.json'))
  commands=[['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(STAGE.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT))],['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(STAGE.relative_to(ROOT)),'--source-forms',str((DOC/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]]
  for i,cmd in enumerate(commands):
   with(DOC/f'command-{i}.log').open('w')as log:result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
   assert result.returncode==0,(i,result.returncode)
  metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');paths=[Path(__file__),OLD/'selection.json.gz',OLD/'terrain-candidates.json',HERE/'acceptance-metrics.mjs',HERE.parent/'building-batch/validate_candidates.mjs']
  for packet in [metrics,validation]:
   for p,h in packet['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
  module('citywalk_runtime_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-original-runtime-metrics-and-loader-v1',paths,dict(uids=[UID],fullAcceptance=False,originalSourceAndFormUnchanged=True,nextStep='Evaluate current metrics against unchanged policy, source identity, foundation, neighbour and source-functional evidence before installation.'))
  print({'metricsRows':len(metrics['rows']),'loaderAccepted':validation.get('loaderAccepted'),'exceptions':validation.get('exceptions')},flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
