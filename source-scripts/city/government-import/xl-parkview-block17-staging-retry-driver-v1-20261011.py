"""Retry unchanged full staging after preserving the original failed503 report."""
import importlib.util,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,reservations
p=HERE/'xl-terrain-recovery-20261011-parkview-block17-unchanged-current-stage-v1.py'
s=importlib.util.spec_from_file_location('stage_retry_original',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
forms=read(m.PHYSICAL/'neighbour-inputs.json.gz')['rows'];keys={'building:'+r['building']['uid']for r in forms}|{'building:'+u for u in m.UIDS|set(m.RETAINED)}
claim=reservations.claim('parkview-block17-stage-retry-'+str(uuid.uuid4()),sorted(keys),batch=m.BATCH,ttl=3600);assert claim['ok']
save(m.LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(m.LEASE),'--ttl','3600','--',sys.executable,str(p),'--owned'],cwd=ROOT,check=True)
