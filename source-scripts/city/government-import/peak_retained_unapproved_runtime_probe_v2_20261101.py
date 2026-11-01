"""Actual-renderer diagnostic for a preserved, constructor-unadmitted surface.

Does not admit the surface, alter either route budget, run a publisher or grant
physical/identity acceptance. Every raw failure remains in the receipt.
"""
import sys,uuid,subprocess,copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peak-retained-unapproved-runtime-probe-v2-20261101';LOCAL=HERE/'local'/BATCH
PRIOR='government-xl-peak-retained-original-terrain-v1-20261101-167911-0';CAPTURE='government-xl-peak-harbourfront-current-sequence-v1-20261101-runtime';INVENTORY='government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101';UID='landsd/167911:0'
def main():
 receipt,pins=authenticate(BASE/PRIOR);assert receipt['reason']=='terrain-runtime-budget'and receipt['installationApproved']is False
 rawpath=BASE/PRIOR/'unapproved-terrain.json';scopepath=BASE/PRIOR/'scope.json';assert all(digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]for p in [rawpath,scopepath]);patch=read(rawpath);domain=read(scopepath)['bounds'];lease=LOCAL/'reservation.json'
 if '--owned'not in sys.argv:
  assert not LOCAL.exists()and not(BASE/BATCH).exists();_,ip=authenticate(BASE/INVENTORY);iv=BASE/INVENTORY/'complete-bounds.json.gz';assert digest(iv.read_bytes())==ip[str(iv.relative_to(ROOT))];inv=read(iv);final=module('peak_probe_lease_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([domain[0]-.01,domain[1]-.01,domain[2]+.01,domain[3]+.01])
  resources={('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f,_,_ in forms};resources.update('building:'+r['uid']for r in inv['rows']if not closed_disjoint(r['completeFourWorldBounds'],domain));resources.update(['building:'+UID,'building:landsd/248218:0','terrain:city/data/terrain.json','terrain:city/data/support-exact-tin-248218-0.json','immutable-source-proof:'+BATCH])
  c=reservations.claim('peak-unapproved-renderer-probe-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],lease,[sys.executable,__file__,'--owned']);return
 assert reservations.owns(read(lease));_,cp=authenticate(BASE/CAPTURE);sp=BASE/CAPTURE/'selection.json.gz';assert digest(sp.read_bytes())==cp[str(sp.relative_to(ROOT))];selected=read(sp);rows=copy.deepcopy([r for r in selected['rows']if r['uid']==UID]);assert len(rows)==1 and rows[0]['sourceSHA256']==receipt['sourceSHA256ByUid'][UID]
 doc=BASE/BATCH;refs=[Path(__file__),BASE/PRIOR/'result.json',rawpath,scopepath,BASE/CAPTURE/'result.json',sp]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';assert digest(parentpath.read_bytes())==patch['meta']['parentSha256'];refs.append(parentpath)
 # A candidate field here is only the input schema for read-only scope/render tools.
 # Status explicitly remains unadmitted and can never satisfy runtime stage admission.
 inputbatch=BATCH+'-surface-input';inputdoc=BASE/inputbatch
 inputs=dict(uids=receipt['uids'],sourceSHA256ByUid=receipt['sourceSHA256ByUid'],candidate=dict(path=str(rawpath.relative_to(ROOT)),sha256=digest(rawpath.read_bytes())),replacedNativeTerrain=receipt['replacedNativeTerrain'],retainedNativeTerrainTargets=receipt['retainedNativeTerrainTargets'],status='unapproved-diagnostic-surface-input',constructorAdmitted=False,constructorMaximumTriangles=25000,constructorActualTriangles=len(patch['nativeMesh']['index'])//3,installationApproved=False,publication=False,sourceGeometryChanges=0)
 save(inputdoc/'summary.json',inputs);module('peak_unapproved_surface_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(inputbatch,'unadmitted-preserved-terrain-surface-diagnostic-input',refs,inputs)
 scopebatch=BATCH+'-scope'
 with (LOCAL/'scope.log').open('w')as log:subprocess.run([sys.executable,str(HERE/'selected_original_retained_patch_scope_v3_20261026.py'),'--batch',scopebatch,'--inventory',INVENTORY,'--patch',inputbatch],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=3600)
 full=read(BASE/scopebatch/'scope.json');from flat_native_replacement_collection_v1_20261028 import verify
 originals={};sources=[]
 for old in receipt['replacedNativeTerrain']:
  p=ROOT/'3d-viewer'/old['url'];assert digest(p.read_bytes())==old['sha256'];originals[old['url']]=read(p);refs.append(p)
 replacements=verify(full,receipt,originals,patch);assert len(replacements)==1
 for row in rows:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];target=LOCAL/row['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes());refs.extend([asset,target]);row['candidate']['path']=str(target.relative_to(ROOT))
 save(doc/'selection.json.gz',dict(rows=rows,manifestSHA256=selected['manifestSHA256']));save(doc/'diagnostic-terrain-input.json',[dict(path=str(rawpath.relative_to(ROOT)),sha256=digest(rawpath.read_bytes()),uids=receipt['uids'],bounds=domain,triangles=len(patch['nativeMesh']['index'])//3,replaces=replacements[0])])
 tool=HERE/'acceptance_metrics_multi_retained_v4_20261101.mjs';cmd=['node',str(tool),'--full-basic-ground','--selection',str((doc/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((doc/'diagnostic-terrain-input.json').relative_to(ROOT)),'--out',str((doc/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with(LOCAL/'renderer.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
 metrics=read(doc/'metrics.json');assert metrics['completeSourceAndBasicFootprintGround']is True and len(metrics['rows'])==1
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=[UID],sourceSHA256ByUid=receipt['sourceSHA256ByUid'],status='unadmitted-terrain-renderer-diagnostic-complete',constructorAdmitted=False,constructorMaximumTriangles=25000,constructorActualTriangles=len(patch['nativeMesh']['index'])//3,completeSourceAndBasicFootprintGround=True,rawMetrics=metrics['rows'],physicalAcceptance=False,identityAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Read-only actual production-renderer measurement of preserved surface. Neither the constructor cap nor any source, physical, neighbour, budget, identity or publication guard is waived. No accepted candidate is created.')
 save(doc/'summary.json',result);refs.extend([BASE/inputbatch/'result.json',BASE/scopebatch/'result.json',tool,HERE/'flat_native_replacement_collection_v1_20261028.py',LOCAL/'runtime-geometry.json.gz']);assert reservations.owns(read(lease))and digest(manifest.read_bytes())==selected['manifestSHA256']
 module('peak_unapproved_runtime_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unadmitted-terrain-actual-renderer-diagnostic',refs,result);print(result,flush=True)
if __name__=='__main__':main()
