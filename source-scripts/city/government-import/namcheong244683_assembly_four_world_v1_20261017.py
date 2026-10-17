"""Capture both unchanged originals in all production renderer coordinate modes."""
from pathlib import Path
import subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-namcheong244683-current-capture-v1-20261017';BATCH='government-xl-namcheong244683-assembly-four-world-v1-20261017';DOC=BASE/BATCH;UIDS=['landsd/244683:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(PHYS/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 mpath=ROOT/'3d-viewer/city/data/manifest.json';m=read(mpath);sources={s['uid']:s for s in read(PHYS/'selection.json.gz')['rows']};rows=[]
 for uid in UIDS:
  s=sources[uid];p=ROOT/s['candidate']['path'];assert digest(p.read_bytes())==s['sourceSHA256'];b=s['source']['building'];tile=ROOT/'3d-viewer'/s['source']['tile'];assert b in read(tile)['buildings'];rows.append(dict(uid=uid,entry={**s['candidate']['entry'],'rootTranslation':[-834500,0,816500]},building=b,path=str(p.relative_to(ROOT))))
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(DOC/'input.json.gz',dict(rows=rows,expected={s['uid']:[s['entry']['sha256'],s['entry']['triangles']]for s in rows},currentManifest=ref(mpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in m['officialModelCatalogues']],evidenceRefs=[ref(PHYS/'result.json'),ref(PHYS/'selection.json.gz')]))
  tool=HERE/'namcheong244683_assembly_actual_attributes_v1_20261017.mjs'
  with(DOC/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  cap=read(DOC/'attributes.json.gz');assert cap['startEndAllInputsVerified'];worlds={'original':{s['uid']:decode_original_world_triangles((ROOT/s['path']).read_bytes())for s in rows}}
  for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={s['uid']:np.asarray(s[key]).reshape(-1,3)[np.asarray(s['completeOriginalIndex']).reshape(-1,3)]for s in cap['rows']}
  assert all(all(len(w[u])==sources[u]['candidate']['entry']['triangles']for u in UIDS)for w in worlds.values());summary={u:dict(hashes={mode:digest(w[u].tobytes())for mode,w in worlds.items()},allEqual=all(np.array_equal(w[u],worlds['literal'][u])for w in worlds.values()))for u in UIDS}
  save(DOC/'world-triangles.json.gz',{mode:{u:t.tolist()for u,t in w.items()}for mode,w in worlds.items()});save(DOC/'summary.json',summary)
  refs=[Path(__file__),PHYS/'result.json',tool,HERE/'exact_packed_world_geometry_20261009.py',*[ROOT/s['path']for s in rows]]
  for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  assert reservations.owns(lease)
  out=module('aqua_capture_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong244683-four-original-assembly-four-world-capture-v1',refs,dict(uids=UIDS,completeFaces=20645,summary=summary,fullAcceptance=False,nextStep='Bind the two original boundary edges and complete current foundation to all captured coordinate modes; the single raw strict contact failure remain until specifically qualified.'));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
