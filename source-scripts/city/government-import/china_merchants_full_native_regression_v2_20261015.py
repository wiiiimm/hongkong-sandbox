"""Recheck previously blocked retained originals against current installed metadata."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-full-native-regression-v2-20261015';DOC=BASE/BATCH;OLD=BASE/'government-xl-retained-group-central-wrapper-20261009-264206-0'
def main():
 assert not DOC.exists();inputs=read(BASE/'government-xl-china-merchants-current-wrapper-v1-20261015/neighbour-inputs.json.gz');manifest=read(ROOT/'3d-viewer/city/data/manifest.json');tiles={r['id']:r for r in manifest['tiles']};paths=[BASE/'government-xl-china-merchants-current-wrapper-v1-20261015/result.json',BASE/'government-xl-china-merchants-current-wrapper-v1-20261015/composition.json',Path(__file__),ROOT/'3d-viewer/city/data/manifest.json',OLD/'neighbour-inputs.json.gz',OLD/'neighbour-checks.json'];tiledata={}
 for row in inputs['rows']:
  b=row['building'];tid=b['tile'];p=ROOT/'3d-viewer'/tiles[tid]['url'];
  if tid not in tiledata:
   tiledata[tid]={}
   for v in read(p)['buildings']:tiledata[tid].setdefault(v['uid'],[]).append(v)
  assert tiledata[tid].get(b['uid'])==[b],b['uid'];paths.append(p)
 scopepath=BASE/'government-xl-china-merchants-complete-current-scope-v1-20261015/scope.json.gz';scope=read(scopepath);paths.extend([scopepath,scopepath.parent/'result.json']);census=read(BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015/input.json.gz');paths.append(BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015/input.json.gz');native={r['uid']for r in census['rows']};inputs['rows']=[dict(building=b,existingNative=b['uid']in native,patchIndexes=[0])for b in census['currentAllNativeSourceForms'].values()];target=next(r['building']for r in read(BASE/'government-xl-china-merchants-current-wrapper-v1-20261015/neighbour-inputs.json.gz')['rows']if r['building']['uid']=='landsd/264206:0');
 if target['uid']not in census['currentAllNativeSourceForms']:inputs['rows'].append(dict(building=target,existingNative=False,patchIndexes=[0]))
 inputs['patches'][0]['replaces']['retainedUids']=[r['uid']for r in scope['nominatedNativeActors']]
 uids={u for p in inputs['patches']for u in p.get('replaces',{}).get('retainedUids',[])};resources=['building:'+u for u in sorted(uids|{'landsd/264206:0'})];leases=[];owner='china-current-native-'+str(uuid.uuid4())
 try:
  for offset in range(0,len(resources),800):
   claim=reservations.claim(owner,resources[offset:offset+800],batch=BATCH+'-'+str(offset),ttl=1800);assert claim['ok'];leases.append(claim['reservation'])
  DOC.mkdir();save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'neighbour-checks.json',{'rows':[]});tool=HERE/'check-china-proposed-support-v2-20261015.mjs';command=['node',str(tool),str(DOC.relative_to(ROOT))+'/']
  with(DOC/'worker.log').open('w')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1500)
  save(DOC/'command.json',dict(command=command,exitCode=p.returncode,currentFormsExactlyUnchanged=True,publication=False));assert p.returncode==0
  result=read(DOC/'native-neighbour-checks.json')
  for path,h in result['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;paths.append(ROOT/path)
  module('china_current_retained_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'proposed-original-support-diagnostic-v1',paths,dict(uids=['landsd/264206:0'],checkedUids=result['blocked'],passedUids=result['resolved'],allRetainedPassed=all(r['passed']for r in result['rows']),fullAcceptance=False,scope='All 1199 current installed originals touching complete parent terrain domain; proposed unchanged original support included. Full basic/target and source-role acceptance remain separate.'))
  print({'checked':len(result['rows']),'passed':len(result['resolved'])},flush=True)
 finally:
  for lease in reversed(leases):
   if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
