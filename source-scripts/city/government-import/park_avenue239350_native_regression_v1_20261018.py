"""Private three-source terrain candidate; joint installed actors remain unapproved."""
from pathlib import Path
import json,sys,uuid,subprocess,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-park-avenue239350-native-regression-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/239350:0','landsd/240161:0','landsd/227455:0']
INPUT=BASE/'government-xl-park-avenue239350-terrain-inputs-v1-20261018'
MAIN=BASE/'government-xl-park-avenue239350-current-identity-runtime-v3-20261018'
COMP=BASE/'government-xl-park-avenue239350-companion-identity-runtime-v1-20261018'
REVIEW=BASE/'government-xl-park-avenue239350-identity-review-v1-20261018'
JOINT=BASE/'government-xl-park-avenue239350-joint-scope-v1-20261018'
PRIOR=BASE/'government-xl-olympian-two-current-retained-terrain-v1-20261018'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 prior=BASE/'government-xl-park-avenue239350-joint-validation-v1-20261018'
 installed=BASE/'government-xl-olympian-original-installed-v1-20261018'
 pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [prior,installed]:
   receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   refs.append(folder/'result.json')
   # The older installation contains historical bytes; authenticate its exact acceptance only.
   if folder==installed:
    path=folder/'installed-acceptance.json';matches=[e for e in receipt['evidenceRefs'] if e['path']==str(path.relative_to(ROOT))];assert len(matches)==1
    pins[matches[0]['path']]=matches[0]['sha256']
   else:
    for e in receipt['evidenceRefs']:pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 acceptance=read(installed/'installed-acceptance.json');assert acceptance['publication']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';entries={};refs.append(manifest)
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for entry in read(path)['models']:assert entry['uid'] not in entries;entries[entry['uid']]=entry
 inputdata=read(prior/'neighbour-inputs.json.gz');forms={r['building']['uid']:r['building'] for r in inputdata['rows']};resolved=[]
 for uid in acceptance['installedUids']:
  entry=entries[uid];assert entry['sha256']==acceptance['sourceSHA256ByUid'][uid] and entry['publicationApproved']
  for dep in entry.get('supportDependencies',[]):
   if dep['state']!='candidate':continue
   support=entries[dep['uid']];assert dep['uid'] in acceptance['installedUids'] and support['publicationApproved']
   assert dep['sha256']==support['sha256']==acceptance['sourceSHA256ByUid'][dep['uid']]
   assert forms[dep['uid']]['buildingCSUID']==support['buildingCSUID']
   resolved.append(dict(uid=uid,dependencyUid=dep['uid'],originalDependency=dep))
 path=installed/'installed-acceptance.json'
 save(DOC/'installed-dependency-resolution.json',dict(rows=resolved,installedReceipt=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),liveCatalogueChanged=False,qualification='Exact installed sources only; raw candidate labels preserved. No physical acceptance implied.'))
 for name in ['neighbour-inputs.json.gz','neighbour-checks.json']:save(DOC/name,read(prior/name))
 tool=HERE/'park_avenue239350_native_neighbours_v1_20261018.mjs';rc=subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT).returncode
 assert reservations.owns(lease)
 summary=dict(uids=UIDS,checkerExitCode=rc,dependencyLabelsResolved=len(resolved),fullAcceptance=False,newlyInstalled=0,publication=False)
 if rc==0:
  result=read(DOC/'native-neighbour-checks.json');summary.update(checked=len(result['rows']),failed=[r['uid'] for r in result['rows'] if not r['passed']])
  for p,h in result['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 else:save(DOC/'guard-failure.json',dict(checkerExitCode=rc))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.append(tool)
 out=module('park_native_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-exact-installed-dependency-native-regression-v1',list(set(refs)),summary);print(dict(jobId=out['jobId'],**summary),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope=read(INPUT/'scope.json');final=module('pair_scope_forms',HERE/'xl-final-script-pass.py');uids={b['uid']for b,_,_ in final.load_forms(scope['fullParentBounds'])}|set(UIDS)
 keys={('building:'if u.startswith('landsd/')else'source-form:')+u for u in uids}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['url']for r in scope['retainedParents']}
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
