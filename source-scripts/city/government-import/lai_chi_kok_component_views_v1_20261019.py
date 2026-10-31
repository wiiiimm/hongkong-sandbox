"""View unresolved unchanged rooftop sources with the complete terminal mesh."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019';CAP=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v3-20261019';BATCH='government-xl-lai-chi-kok-component-views-v1-20261019';DOC=BASE/BATCH
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];tool=HERE/'lai_chi_kok_component_views_v1_20261019.mjs';refs.append(tool)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 terminal=read(CAP/'selection.json.gz')['rows'][0];component=dict(uid=terminal['uid'],assetPath=terminal['candidate']['path'],sourceSHA256=terminal['sourceSHA256'],worldBounds=terminal['candidate']['entry']['worldBounds']);wanted={r['uid']for r in read(SRC/'summary.json')['rows']if not r['supportPassed']};models=[]
 for r in read(SRC/'selection.json.gz')['rows']:
  if r['uid']not in wanted:continue
  bounds=r['native']['model']['worldBounds'];frame=[[v-3 for v in bounds[0]],[v+3 for v in bounds[1]]]
  models.append(dict(uid=r['uid'],label=r['uid']+' original component and platform',assetPath=r['candidate']['path'],sourceSHA256=r['sourceSHA256'],worldBounds=bounds,triangles=r['triangles'],forms=[r['source']['building']],reviewFrame=frame,viewDirection=[.8,.55,1],originalComponents=[component]))
 refs.extend(ROOT/p for p in pins);hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};save(DOC/'input.json',dict(models=models,inputHashes=hashes));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);report=read(DOC/'render.json');assert len(report['views'])==len(wanted)and not report['errors']
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('kai_component_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-original-component-contact-views',list(dict.fromkeys(refs)),dict(uids=sorted(wanted),installationApproved=False))
if __name__=='__main__':main()
