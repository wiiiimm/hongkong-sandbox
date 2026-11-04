"""Bounded desktop or mobile original-assembly acceptance with durable results."""
from pathlib import Path
import sys,os,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import olympian_two_thirteen_private_browser_v2_20261018 as prior
width=390;phase=sys.argv[1];assert phase=='fallback'
BATCH='government-xl-olympian-two-browser-'+str(width)+'-'+phase+'-v5-20261018';DOC=prior.BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists()and not LOCAL.exists();pins={};refs=[Path(__file__),Path(prior.__file__)]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for name in prior.NAMES:
  d=prior.BASE/name;r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
config=read(prior.LOCAL/'browser-config.json');cat=read(prior.LOCAL/'catalogue.json');uids=[m['uid']for m in cat['models']];assert len(uids)==13
for m in cat['models']:assert digest((prior.LOCAL/m['asset']).read_bytes())==m['sha256']
config.update(doc=str(DOC.relative_to(ROOT))+'/',viewportWidths=[width])
if phase=='joint':config['failureTestUids']=[]
else:config.update(fallbackOnly=True,jointUids=[],nativeSupportUidsByModel={},retainedBuildingUidsByModel={})
save(LOCAL/'browser-config.json',config);DOC.mkdir()
tool=HERE/'olympian_thirteen_assembly_browser_v5_20261018.mjs';cmd=['node',str(tool),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]
with(DOC/'browser.log').open('w')as log:process=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
save(DOC/'command.json',dict(command=cmd,exitCode=process.returncode,width=width,publication=False))
for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
refs.extend([tool,*[ROOT/p for p in pins],*[p for p in prior.LOCAL.rglob('*')if p.is_file()],LOCAL/'browser-config.json'])
module('viewport_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-original-browser-mobile-'+phase+'-v5',refs,dict(uids=uids,width=width,browserExitCode=process.returncode,fullAcceptance=False))
