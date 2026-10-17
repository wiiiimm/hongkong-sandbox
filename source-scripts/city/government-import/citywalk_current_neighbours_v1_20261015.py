"""Complete current parent-domain BASIC and installed native regression."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,reservations,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-current-neighbours-v1-20261015';DOC=BASE/BATCH
SCOPE=BASE/'government-xl-citywalk-complete-current-scope-v1-20261015';CENSUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015';FOUND=BASE/'government-xl-citywalk-candidate-foundation-v1-20261015'
def main():
 assert not DOC.exists();paths=[Path(__file__)];pins={}
 for folder in [SCOPE,CENSUS,FOUND]:
  r=read(folder/'result.json');paths.append(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
 scope=read(SCOPE/'scope.json.gz');census=read(CENSUS/'input.json.gz');native={r['uid']for r in census['rows']};patch=read(FOUND/'plan.json')['terrainOverride'];patch['replaces']['retainedUids']=[r['uid']for r in scope['nominatedNativeActors']]
 uids=patch['replaces']['retainedUids'];claim=reservations.claim('citywalk-neighbours-'+str(uuid.uuid4()),['building:'+u for u in sorted(set(uids+['landsd/134332:0']))],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  DOC.mkdir();inputhash={p:h for p,h in pins.items()if p.startswith('3d-viewer/')}
  basic=dict(patches=[patch],candidateIds=['landsd/134332:0'],inputHashes=inputhash,rows=[dict(building=b,existingNative=b['uid']in native,patchIndexes=[0])for b in scope['currentIntersectingForms']]);save(DOC/'basic/neighbour-inputs.json.gz',basic)
  target=read(HERE/'accepted/government-xl-citywalk-source-20261004/source-forms.json')[0]
  allforms=dict(census['currentAllNativeSourceForms']);assert target['uid']not in allforms or allforms[target['uid']]==target;allforms[target['uid']]=target
  inp={**basic,'rows':[dict(building=b,existingNative=b['uid']in native,patchIndexes=[0])for b in allforms.values()]};save(DOC/'native/neighbour-inputs.json.gz',inp);save(DOC/'native/neighbour-checks.json',{'rows':[]})
  for part,tool in [('basic','check-neighbours.mjs'),('native','check-citywalk-proposed-support-v1-20261015.mjs')]:
   paths.append(HERE/tool)
   with(DOC/(part+'.log')).open('w')as log:p=subprocess.run(['node',str(HERE/tool),str((DOC/part).relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
   assert p.returncode==0,(part,p.returncode)
  b=read(DOC/'basic/neighbour-checks.json');n=read(DOC/'native/native-neighbour-checks.json');bad=[r for r in b['rows']if r['reasons']and not r['existingNative']and not r['candidate']]
  assert {r['uid']for r in n['rows']}==set(uids)
  for result in [b,n]:
   for p,h in result['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
  for p,h in inputhash.items():assert digest((ROOT/p).read_bytes())==h,p
  summary=dict(basicForms=len(b['rows']),basicFailures=bad,nativeChecked=len(n['rows']),nativePassed=len(n['resolved']),nativeFailures=[r for r in n['rows']if not r['passed']],fullAcceptance=False)
  save(DOC/'summary.json',summary)
  module('citywalk_neighbour_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-parent-neighbour-regression-v1',paths,dict(uids=['landsd/134332:0'],**summary))
  print(dict(basic=len(b['rows']),basicFailures=len(bad),native=len(n['rows']),nativePassed=len(n['resolved'])),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
