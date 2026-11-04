"""Run directory discovery twice and retain evidence of unchanged-input reuse."""
import argparse,json,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def transfer():
 rows=[json.loads(p.read_text()) for p in (HERE/'cache').glob('*/*/transfer.json')]
 return {'receivedBytes':sum(r.get('receivedBytes',0) for r in rows),'requests':sum(len(r.get('requests',[])) for r in rows)}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',required=True);p.add_argument('--workers',type=int,default=8);p.add_argument('--max-mb',type=int,default=512);a=p.parse_args()
 docs=ROOT/'docs/astra-city/citywide-source';runs=[];(HERE/'cache').mkdir(parents=True,exist_ok=True)
 for label in ('current-pipeline','unchanged-replay'):
  before=transfer();start=time.monotonic()
  with (HERE/'cache'/('verification-'+label+'.log')).open('w') as log:
   subprocess.run([sys.executable,str(HERE/'discover.py'),'--index',a.index,'--workers',str(a.workers),'--max-mb',str(a.max_mb)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  result=json.loads((docs/'summary.json').read_text());after=transfer()
  if result['status']!='complete':raise ValueError('Partial scan cannot prove full reuse')
  run={'label':label,'seconds':round(time.monotonic()-start,3),'newTransferredBytes':after['receivedBytes']-before['receivedBytes'],'newRequests':after['requests']-before['requests'],'summary':result};runs.append(run)
  print(json.dumps({k:v for k,v in run.items() if k!='summary'}),flush=True)
 replay=runs[-1]
 if replay['newRequests'] or replay['newTransferredBytes'] or replay['summary']['reusedSheets']!=replay['summary']['sourceSheets']:raise ValueError('Unchanged run repeated network acquisition')
 if runs[0]['summary']['pipelineSHA256']!=replay['summary']['pipelineSHA256']:raise ValueError('Pipeline changed during verification')
 proof={'issue':'HKS-221','runs':runs,'qualification':'All source sheet metadata reused without network acquisition; native geometry conversion and visual acceptance remain separate.'}
 (docs/'reuse-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
if __name__=='__main__':main()
