"""Exact budget recovery then complete retained-neighbour/source diagnostics.

Private original acquisition work only. No threshold edits or publication.
"""
import argparse,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,reservations
from require_remaining_xl import require_remaining
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','prior','capture','inventory','installed','uid']:p.add_argument('--'+k,required=True)
 p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
 local=HERE/'local'/a.batch;lease=local/'reservation.json';prior=BASE/a.prior;receipt,pins=authenticate(prior)
 path=prior/'scope.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];bounds=read(path)['bounds']
 cr,cp=authenticate(BASE/a.capture);selectionpath=BASE/a.capture/'selection.json.gz';assert digest(selectionpath.read_bytes())==cp[str(selectionpath.relative_to(ROOT))]
 selected=read(selectionpath);row=next(r for r in selected['rows']if r['uid']==a.uid);require_remaining(BASE/a.installed/'full-xl-current-count.json',a.uid,row['sourceSHA256'])
 assert receipt['uids']==[a.uid]and receipt['sourceSHA256ByUid'][a.uid]==row['sourceSHA256']
 if not a.owned:
  assert not local.exists();_,ip=authenticate(BASE/a.inventory);invpath=BASE/a.inventory/'complete-bounds.json.gz';assert digest(invpath.read_bytes())==ip[str(invpath.relative_to(ROOT))];inv=read(invpath)
  final=module('retained_budget_lease_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([bounds[0]-.01,bounds[1]-.01,bounds[2]+.01,bounds[3]+.01])
  resources={('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b,_,_ in forms}
  resources.update('building:'+r['uid']for r in inv['rows']if not closed_disjoint(r['completeFourWorldBounds'],bounds))
  resources.update(['building:'+a.uid,'terrain:city/data/terrain.json','immutable-source-proof:'+a.batch])
  for old in receipt['replacedNativeTerrain']:
   resources.add('terrain:'+old['url']);resources.update('building:'+u for u in old['targetUids'])
  c=reservations.claim('retained-budget-validation-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],lease,[sys.executable,__file__,*sys.argv[1:],'--owned']);return
 patch=a.batch+'-terrain';scope=a.batch+'-scope';runtime=a.batch+'-runtime';bindings=a.batch+'-bindings';neighbours=a.batch+'-neighbours'
 steps=[('budget','selected_exact_colour_terrain_budget_recovery_v1_20261101.py',['--batch',patch,'--prior',a.prior,'--lease-file',str(lease)]),('scope','selected_original_retained_patch_scope_v3_20261026.py',['--batch',scope,'--inventory',a.inventory,'--patch',patch]),('runtime','selected_original_patch_runtime_full_basic_ground_v2_20261101.py',['--batch',runtime,'--patch',patch,'--capture',a.capture]),('bindings','selected_current_installed_dependency_bindings_v2_20261028.py',['--batch',bindings,'--scope',scope]),('neighbours','selected_retained_native_neighbours_v10_20261101.py',['--batch',neighbours,'--scope',scope,'--inventory',a.inventory,'--patch',patch,'--bindings',bindings,'--lease-file',str(lease)])]
 for name,tool,args in steps:
  assert reservations.owns(read(lease))
  with (local/(name+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
  print(name+' complete',flush=True)
 save(local/'completed.json',dict(uid=a.uid,batches=dict(terrain=patch,scope=scope,runtime=runtime,bindings=bindings,neighbours=neighbours),sourceGeometryChanges=0,installationApproved=False,publication=False))
if __name__=='__main__':main()
