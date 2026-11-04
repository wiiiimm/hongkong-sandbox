"""Capture production coordinate modes for original West Wing assembly."""
from pathlib import Path
import subprocess,json,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-group-four-world-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
ASSEMBLY=BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015'
UIDS=['landsd/26195:0','landsd/322270:0','landsd/315069:0','landsd/319534:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);rows=[];refs=[Path(__file__)];pins={}
 receipt=read(ASSEMBLY/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 projection=read(ASSEMBLY/'projection.json');expected_rows={r['uid']:r for r in projection['rows']}
 assert digest((ASSEMBLY/'projection.json').read_bytes())==next(e['sha256'] for e in receipt['evidenceRefs'] if e['path']==str((ASSEMBLY/'projection.json').relative_to(ROOT)))
 refs.extend([ASSEMBLY/'result.json',ASSEMBLY/'projection.json'])
 current=read(ROOT/'3d-viewer/city/data/manifest.json');tile='city/data/tiles/0_0.json';forms={f['uid']:f for f in read(ROOT/'3d-viewer'/tile)['buildings']}
 found={}
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;cat=read(path)
  for e in cat['models']:
   uid=e['uid']
   if uid not in UIDS:continue
   assert uid not in found and e['sha256']==expected_rows[uid]['sourceSHA256']
   entry={**e,'rootTranslation':cat['rootTranslation'],'coordinatePolicy':cat.get('coordinatePolicy'),'datasetId':cat.get('datasetId')}
   found[uid]=dict(uid=uid,sourceSHA256=e['sha256'],source=dict(tile=tile,building=forms[uid]),candidate=dict(path=str((path.parent/e['asset']).relative_to(ROOT)),entry=entry),native=dict(model=dict(triangles=expected_rows[uid]['completeFaces'])))
 assert set(found)==set(UIDS);rows=[found[u] for u in UIDS]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);inputs=[];expected={}
 for r in rows:
  uid=r['uid'];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];tp=ROOT/'3d-viewer'/r['source']['tile'];assert r['source']['building'] in read(tp)['buildings'];refs.extend([p,tp]);inputs.append(dict(uid=uid,entry=r['candidate']['entry'],building=r['source']['building'],path=str(p.relative_to(ROOT))));expected[uid]=[r['sourceSHA256'],r['native']['model']['triangles']]
 save(DOC/'input.json.gz',dict(rows=inputs,expected=expected,currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u) for u in m['officialModelCatalogues']],evidenceRefs=[ref(p) for p in refs if p.is_file()]))
 donor=HERE/'nobhill98845_actual_attributes_v1_20261018.mjs';code=donor.read_text().replace("assert.deepEqual(input.rows.map(r=>r.uid),[\"landsd/98845:0\"])","assert.deepEqual(input.rows.map(r=>r.uid),"+json.dumps([r['uid'] for r in rows])+")");code=code.replace('completeOriginalFaces:20219','completeOriginalFaces:rows.reduce((n,r)=>n+r.completeOriginalIndex.length/3,0)');tool=HERE/'west_wing_group_actual_attributes_v1_20261018.mjs'
 if tool.exists():assert tool.read_text()==code
 else:tool.write_text(code)
 subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True,timeout=300)
 cap=read(DOC/'attributes.json.gz');assert cap['startEndAllInputsVerified'];worlds={mode:{} for mode in ['original','literal','left','balanced']};summaries=[]
 for r in rows:
  uid=r['uid'];a=next(a for a in cap['rows'] if a['uid']==uid);w={'original':decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes())}
  for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:w[mode]=np.asarray(a[key]).reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
  assert all(t.shape==(expected[uid][1],3,3) for t in w.values());summary=dict(uid=uid,modes={mode:dict(worldSHA256=digest(t.tobytes()),maxDifferenceM=float(abs(t-w['original']).max())) for mode,t in w.items()});summaries.append(summary)
  for mode,t in w.items():worlds[mode][uid]=t.tolist()
 save(DOC/'worlds.json.gz',worlds);save(DOC/'selection.json.gz',dict(rows=rows));save(DOC/'summary.json',dict(rows=summaries,installationApproved=False))
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert reservations.owns(lease);refs.extend([tool,donor,HERE/'exact_packed_world_geometry_20261009.py']);out=module('nob_group_four_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-four-originals-production-coordinate-capture-v1',list(dict.fromkeys(refs)),dict(uids=list(expected),models=4,triangles=sum(v[1] for v in expected.values()),physicalAccepted=False,installationApproved=False));print(out['jobId'],flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();uids=UIDS;c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
