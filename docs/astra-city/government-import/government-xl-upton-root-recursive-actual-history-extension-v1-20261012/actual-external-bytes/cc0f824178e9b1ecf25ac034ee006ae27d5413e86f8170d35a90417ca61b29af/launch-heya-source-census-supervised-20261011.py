import sys,json,uuid,subprocess
from pathlib import Path
HERE=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city/source-scripts/city/government-import')
sys.path.insert(0,str(HERE))
from run import ROOT,read,save,reservations,digest
BATCH='government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
SCRIPT=HERE/'xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011.py'
assert not DOC.exists() and not LOCAL.exists()
assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
claim=reservations.claim('heya-complete-source-census-'+str(uuid.uuid4()),['building:landsd/184286:0','building:landsd/184285:0'],batch=BATCH,ttl=3600)
assert claim['ok'],claim
save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
save(LOCAL/'supervised-launch.json',dict(batch=BATCH,script=str(SCRIPT.relative_to(ROOT)),scriptSHA256=digest(SCRIPT.read_bytes()),sourceOnly=True,currentAcceptance=False))
print(json.dumps(dict(claimed=True,owner=claim['reservation']['owner'],token=str(claim['reservation']['token']))),flush=True)
r=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,str(SCRIPT)],cwd=ROOT)
print(json.dumps(dict(supervisorReturnCode=r.returncode)),flush=True)
sys.exit(r.returncode)
