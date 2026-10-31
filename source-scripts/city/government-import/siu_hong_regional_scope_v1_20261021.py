"""Nominate complete regional terrain obligations; no live geometry changes."""
from pathlib import Path
import json, subprocess, sys, uuid
import numpy as np
from shapely.geometry import box
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-siu-hong-regional-scope-v1-20261021'
DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH
SOURCE=BASE/'government-xl-tko-current-inventory-v1-20261021'
def owned():
 lease=read(LOCAL/'reservation.json'); assert reservations.owns(lease) and not DOC.exists()
 receipt=read(SOURCE/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 # Recheck the complete bound inventory, catalogues, source assets and renderer.
 for p,h in pins.items(): assert digest((ROOT/p).read_bytes())==h,p
 inventory=read(SOURCE/'complete-bounds.json.gz'); rows=inventory['rows']; assert len(rows)==6800
 selectionpath=BASE/'government-xl-siu-hong-private-capture-v2-20261021/selection.json.gz'
 selection=read(selectionpath);assert len(selection['rows'])==2
 row=next(r for r in selection['rows']if r['uid']=='landsd/233417:0')
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json'; manifest=read(manifestpath)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json'; parent=read(parentpath)
 builder=module('yoho_regional_scope',HERE/'resolve-pass-indexed-parent-clipping.py')
 assert digest(manifestpath.read_bytes())==selection['manifestSHA256']
 captureFolder=selectionpath.parent;cr=read(captureFolder/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cr['jobId'],)).fetchone()==('complete',cr)
 cp={e['path']:e['sha256']for e in cr['evidenceRefs']};attributePath=captureFolder/'attributes.json.gz';assert digest(attributePath.read_bytes())==cp[str(attributePath.relative_to(ROOT))];assert digest(selectionpath.read_bytes())==cp[str(selectionpath.relative_to(ROOT))]
 attributes=read(attributePath);assert attributes['startEndAllInputsVerified'] and not attributes['rejected']
 bounds=[r['candidate']['entry']['worldBounds']for r in selection['rows']]
 for r in attributes['rows']:
  bounds.extend(r[k]for k in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds'])
 points=np.asarray(bounds).reshape(-1,3);lo,hi=points.min(0),points.max(0);x0,z0,x1,z1=lo[0]-8,lo[2]-8,hi[0]+8,hi[2]+8
 cells=builder.rectangle_for([[x0,0,z0],[x1,0,z1]],parent);retained=[];refs=[Path(__file__),SOURCE/'result.json',selectionpath,captureFolder/'result.json',attributePath,parentpath]+[ROOT/p for p in pins]
 # Close over every intersecting existing patch until no regional domain grows.
 changed=True
 while changed:
  changed=False; domain=builder.extent(cells,parent)
  for entry in manifest['terrainPatches']:
   url=entry['url']
   if any(r['url']==url for r in retained): continue
   path=ROOT/'3d-viewer'/url; patch=read(path)
   pc=patch['coarseCells']; extent=builder.extent(pc,parent)
   if box(*domain).intersection(box(*extent)).area<=1e-8: continue
   assert not patch.get('patches'), 'Nested patch needs explicit recursive accounting'
   packed=np.asarray(patch['nativeMesh']['position'],dtype='float64').reshape(-1,3)
   points=np.concatenate([packed,packed.astype('float32').astype('float64')])
   lo=points.min(0); hi=points.max(0)
   retained.append(dict(url=url,sha256=digest(path.read_bytes()),coarseCells=pc,extent=extent,allPackedExtent=[float(lo[0]),float(lo[2]),float(hi[0]),float(hi[2])],packedVertices=len(packed),drawnTriangles=len(patch['nativeMesh']['index'])//3))
   refs.append(path); cells=[min(cells[0],pc[0]),min(cells[1],pc[1]),max(cells[2],pc[2]),max(cells[3],pc[3])]; changed=True
 domain=builder.extent(cells,parent); affected=list(domain)
 for r in retained:
  e=r['allPackedExtent']; affected=[min(affected[0],e[0]),min(affected[1],e[1]),max(affected[2],e[2]),max(affected[3],e[3])]
 touch=sorted(r['uid'] for r in rows if not closed_disjoint(r['completeFourWorldBounds'],affected))
 result=dict(uids=['landsd/233417:0'],currentNativeActors=len(rows),regionalCoarseCells=cells,regionalParentExtent=domain,allRetainedPackedAffectedExtent=affected,retainedPatches=retained,touchingNativeUids=touch,fullBeforeAfterRegressionRequired=touch,installationApproved=False,modelGeometryChanges=0,qualification='Planning domain only. Candidate construction may expand packed bounds and must repeat nomination before acceptance.')
 save(DOC/'scope.json',result)
 for p,h in pins.items(): assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease)
 r=module('yoho_regional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-regional-terrain-obligation-scope',list(dict.fromkeys(refs+[HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])),result)
 print(json.dumps(dict(jobId=r['jobId'],touchingNativeUids=touch,regionalExtent=domain)),flush=True)
def main():
 if '--owned' in sys.argv: return owned()
 assert not DOC.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/233417:0'],batch=BATCH,ttl=3600); assert claim['ok'],claim
 lease=claim['reservation']; path=LOCAL/'reservation.json'; save(path,json.loads(json.dumps(lease,default=str)))
 try: subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease): assert reservations.release(lease)['ok']
if __name__=='__main__': main()
