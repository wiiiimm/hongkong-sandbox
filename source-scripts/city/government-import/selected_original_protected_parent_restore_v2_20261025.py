"""Private terrain-only restoration of current ground inside explicit form boxes.

Reuse the existing exact finite upper-boundary join, current drawn parent capture
and terrain validators. Never edit source building meshes or grant acceptance.
"""
import argparse,copy,subprocess,traceback
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from bounded_native_upper_return_v1 import join
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','previous','selection','scope']:p.add_argument('--'+k,required=True)
 p.add_argument('--protect-form',action='append',required=True);p.add_argument('--core-margin',action='append',default=[],help='Explicit protectedUID,marginM; default1m, bounded1..8m');a=p.parse_args()
 assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.previous,a.selection,a.scope])
 out=BASE/a.batch;local=HERE/'local'/a.batch;assert not out.exists()and not local.exists();refs=[Path(__file__),HERE/'bounded_native_upper_return_v1.py'];pins={};receipts={}
 def take(batch,path):
  if batch not in pins:receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(a.selection,BASE/a.selection/'selection.json.gz');rows=selected['rows'];sources={r['uid']:r['sourceSHA256']for r in rows}
 old=take(a.previous,BASE/a.previous/'summary.json');assert old['status']=='private-terrain-validator-passed'and not old.get('replacedNativeTerrain')
 assert set(old['uids'])<=set(sources)and all(sources[u]==h for u,h in old['sourceSHA256ByUid'].items())
 patch=take(a.previous,ROOT/old['candidate']['path']);assert digest((ROOT/old['candidate']['path']).read_bytes())==old['candidate']['sha256'];patch=copy.deepcopy(patch)
 rootpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(rootpath);refs.append(rootpath);assert patch['meta']['parentSha256']==digest(rootpath.read_bytes())
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==selected['manifestSHA256'];manifest=read(manifestpath);refs.append(manifestpath)
 tiles={t['id']:t['url']for t in manifest['tiles']};forms=take(a.scope,BASE/a.scope/'form-obligations.json.gz');protected=set(a.protect_form);assert 0<len(protected)==len(a.protect_form)<=12 and not protected&set(sources)
 margins={u:float(v)for u,v in (x.split(',')for x in a.core_margin)};assert len(margins)==len(a.core_margin)and set(margins)<=protected and all(np.isfinite(v)and 1<=v<=8 for v in margins.values())
 protected_forms=[f for f in forms if f['uid']in protected];assert {f['uid']for f in protected_forms}==protected
 for f in forms:
  path=ROOT/'3d-viewer'/tiles[f['tile']];assert digest(path.read_bytes())==pins[a.scope][str(path.relative_to(ROOT))];assert next(x for x in read(path)['buildings']if x['uid']==f['uid'])==f;refs.append(path)
 for r in rows:
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  path=ROOT/'3d-viewer'/r['source']['tile'];assert digest(path.read_bytes())==r['source']['tileSHA256']and next(f for f in read(path)['buildings']if f['uid']==r['uid'])==r['source']['building'];refs.append(path)
 validator=module('protected_restore_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=validator.extent(patch['coarseCells'],parent);domain=shapely.box(*bounds)
 save(out/'scope.json',dict(uids=old['uids'],bounds=bounds,coarseCells=patch['coarseCells'],currentManifestSHA256=selected['manifestSHA256'],installationApproved=False))
 tool=HERE/'selected_original_parent_capture_v2.mjs';parent_capture=local/'current-parent.json'
 subprocess.run(['node',str(tool),str((out/'scope.json').relative_to(ROOT)),str(parent_capture.relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(parent_capture);assert capture['domain']==bounds;refs.extend([tool,parent_capture])
 for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 baseline=np.asarray(capture['triangles'],float);mesh=patch['nativeMesh'];terrain=np.asarray(mesh['position'],dtype=np.float32).astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];proofs=[]
 result=dict(uids=old['uids'],sourceSHA256ByUid=old['sourceSHA256ByUid'],allExplicitOriginalSourceSHA256ByUid=sources,protectedFormUids=sorted(protected),sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,currentManifestSHA256=selected['manifestSHA256'])
 try:
  for f in sorted(protected_forms,key=lambda f:f['uid']):
   footprint=shapely.Polygon(f['rings'][0],f['rings'][1:]);assert footprint.is_valid and footprint.area>0
   x,z,X,Z=footprint.bounds;margin=margins.get(f['uid'],1.);inner=[x-margin,z-margin,X+margin,Z+margin];outer=[inner[0]-3,inner[1]-3,inner[2]+3,inner[3]+3]
   assert domain.covers(shapely.box(*outer))and domain.boundary.distance(shapely.box(*outer))>0
   before=terrain;terrain,proof=join(before,baseline,bounds,outer,3,validator.exact)
   assert np.isfinite(terrain).all()and terrain[:,:,1].min()>=1.2 and len(terrain)<=25000
   proofs.append(dict(uid=f['uid'],coreMarginM=margin,inputBasis='Existing candidate packed to exact renderer Float32 positions; identical rendered surface',footprintWKT=footprint.wkt,inputTriangles=len(before),outputTriangles=len(terrain),**proof));save(out/'restore-proof.json',proofs)
  mesh['position']=terrain.reshape(-1).tolist();mesh['index']=list(range(terrain.size//3))
  binding=dict(protectedForms=protected_forms,currentParentCapture=dict(path=str(parent_capture.relative_to(ROOT)),sha256=digest(parent_capture.read_bytes())),coreMarginsM={u:margins.get(u,1.)for u in protected},construction='Exact current parent inside explicitly bounded footprint bounding-box core; existing3m upper-boundary join returns to prior private terrain. Derived terrain only; no source or publication approval.')
  for metadata in [mesh['source'],patch['meta']['source']]:metadata['protectedParentRestoration']=binding
  from native_patch_resolution import projected_context
  from float32_coverage import approve_roundoff
  _,polygons,_,_=projected_context(patch,bounds)
  if shapely.union_all(polygons).symmetric_difference(domain).area:save(out/'numerical-coverage.json',approve_roundoff(patch,bounds))
  overlap=module('protected_restore_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out;overlap.overlap_proof(patch,refs)
  save(out/'before-validation-terrain.json',patch);validator.validate_patch(patch,parent)
  candidate=local/'candidate-terrain.json';save(candidate,patch);refs.append(candidate)
  result.update(status='private-terrain-validator-passed',candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=digest(candidate.read_bytes())),terrainTriangles=len(terrain),qualification='Exact current-ground restoration proposal only. Full original/four-world coverage, clearance, foundations, complete neighbours/native229481 and device/browser checks remain mandatory.')
 except Exception as e:
  save(out/'construction-failure.json',dict(error=repr(e),traceback=traceback.format_exc()));result.update(status='private-terrain-construction-investigation',error=repr(e),qualification='Failed construction is not source corruption or acceptance. Preserve existing limits and investigate exact construction failure.')
 assert digest(manifestpath.read_bytes())==selected['manifestSHA256']
 save(out/'summary.json',result);refs.extend([HERE/'resolve_pass_indexed_parent_clipping_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
 module('protected_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-current-parent-ground-protection-private-terrain-proposal',list(dict.fromkeys(refs)),result)
 print({k:v for k,v in result.items()if k not in ['allExplicitOriginalSourceSHA256ByUid','sourceSHA256ByUid']},flush=True)
if __name__=='__main__':main()
