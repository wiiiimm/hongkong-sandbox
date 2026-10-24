"""Complete current original Villa Elegance identity; no support/publication claim."""
import importlib.util,uuid,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='xl-terrain-recovery-20261010-no1-garden-villa-elegance-source-identity-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-no1-garden-villa-elegance-original-recovery-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();row=read(PRIOR/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/237414:0';manifest=ROOT/'3d-viewer/city/data/manifest.json';pin=ref(manifest);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==517;row['triangles']=len(tri)
 local=LOCAL/'identity-recheck';asset=local/'assets'/(row['sourceSHA256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
 final=module('villa_full_forms','xl-final-script-pass.py');lo=tri[:,:,[0,2]].min((0,1));hi=tri[:,:,[0,2]].max((0,1));forms=final.load_forms([lo[0]-2,lo[1]-2,hi[0]+2,hi[1]+2]);context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms})
 claim=reservations.claim('villa-original-identity-'+str(uuid.uuid4()),['building:'+row['uid']],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  proof=verify_files(row,context,local);assert ref(manifest)==pin;save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=pin['sha256']));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity-proof.json',proof)
  freeze=module('villa_source_identity_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'complete-current-exact-original-villa-elegance-identity-only-v1',[Path(__file__),PRIOR/'selection.json.gz',asset,manifest,HERE/'exact_original_georef_cell_identity_20261009.py'],dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],identityPassed=proof['passed'],identityReasons=proof['reasons'],sourceGeometryChanges=0,publication=False,newlyInstalled=0,fullPhysicalAcceptance=False))
  print(json.dumps(dict(identityPassed=proof['passed'],reasons=proof['reasons'],manifest=pin['sha256'])),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
