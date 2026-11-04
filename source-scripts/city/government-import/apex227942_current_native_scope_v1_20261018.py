"""Nominate every current packed original touching the whole replaced regional parent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-apex227942-current-native-scope-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();prior=BASE/'government-xl-wave-verdant-expanded-scope-v1-20261017';r=read(prior/'result.json');pins={};refs=[Path(__file__),prior/'result.json',prior/'complete-bounds.json.gz',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifestpath);current={}
 for url in m['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;current.update({e['uid']:e for e in read(p)['models']});refs.append(p)
 cap=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018';candidate=read(cap/'terrain-candidates.json')[0];pp=ROOT/'3d-viewer'/candidate['replaces']['url'];assert digest(pp.read_bytes())==candidate['replaces']['sha256'];parent=read(pp);g=parent['meta']['georef'];domain=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(parent['w']-1)*g['aE'],816500-g['bN']-(parent['h']-1)*g['aN']]
 bounds=read(prior/'complete-bounds.json.gz')['rows'];assert set(current)=={x['uid']for x in bounds};touch=[];local=[]
 for row in bounds:
  assert row['sourceSHA256']==current[row['uid']]['sha256']
  if not closed_disjoint(row['completeFourWorldBounds'],domain):touch.append(row)
  if not closed_disjoint(row['completeFourWorldBounds'],candidate['bounds']):local.append(row)
 save(DOC/'scope.json',dict(parentExtent=domain,localCandidateExtent=candidate['bounds'],currentNativeActors=len(bounds),wholeParentTouching=touch,localTouching=local,fullAcceptance=False))
 refs.extend([manifestpath,pp,cap/'terrain-candidates.json']);summary=dict(currentNativeActors=len(bounds),wholeParentTouching=len(touch),localTouching=len(local),fullAcceptance=False);print(summary,flush=True)
 out=module('apex_native_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-full-current-packed-native-parent-scope-v1',list(set(refs)),dict(uids=['landsd/227942:0']+[x['uid']for x in touch],summary=summary,fullAcceptance=False,newlyInstalled=0,nextStep='Prove unchanged exterior terrain and run full before/after checks for every touching native actor; scope nomination grants no regression acceptance.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
