"""Replay frozen original topology/contacts against fresh unchanged drawn ground."""
import importlib.util,json,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_ordinary_ground_root_graph_20261009 import verify
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-green18-fresh-original-support-replay-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261010-green18-complete-original-support-v1';PHYSICAL=BASE/'government-xl-terrain-recovery-green18-original-terrain-current-v1-20261010';GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';MANIFEST=ROOT/'3d-viewer/city/data/manifest.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=digest(MANIFEST.read_bytes());old=read(PRIOR/'diagnostic.json.gz');receipt=read(PRIOR/'result.json');physical=read(PHYSICAL/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [receipt,physical]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 # The earlier runner fenced the whole diagnostic value, not a file pointer.
 assert all(receipt[k]==v for k,v in old.items()),'Frozen complete original graph differs from durable Neon value'
 g=read(GEOMETRY)
 for path,sha in g['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 selected=read(PHYSICAL/'selection.json.gz');assert selected['manifestSHA256']==manifest;pieces=[];indexed=[];assets=[]
 for r in selected['rows']:
  asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256'];decoded=decode_original_world_triangles(raw);row=next(x for x in g['rows'] if x['uid']==r['uid']);indices=np.asarray(row['index'],np.uint32).reshape(-1,3);positions=np.asarray(row['position']).reshape(-1,3);assert decoded.shape==positions[indices].shape and np.max(np.abs(decoded-positions[indices]))<=1e-9
  original=np.empty_like(positions);assigned={}
  for faceids,face in zip(indices,decoded):
   for i,v in zip(faceids,face):
    i=int(i)
    if i in assigned:assert np.array_equal(assigned[i],v)
    else:assigned[i]=v;original[i]=v
  assert set(assigned)==set(range(len(original))) and np.array_equal(original[indices],decoded);indexed.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],position=original.reshape(-1).tolist(),index=indices.reshape(-1).tolist()));pieces.append(decoded);assets.append(asset)
 tri=np.concatenate(pieces);ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry']).reshape(-1,9) for r in g['rows']]),axis=0).reshape(-1,3,3)
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=digest(GEOMETRY.read_bytes()),supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed))
 for key in ['completeOriginalWorldTrianglesSHA256','currentDrawnGroundSHA256','originalIndexedSourcesSHA256','supportScope']:assert binding[key]==old['binding'][key]
 claim=reservations.claim('green18-original-replay-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  replay=json.loads(json.dumps(verify(tri,old['actors'],old['components'],old['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding)))
  for key in replay:
   if key!='binding':assert replay[key]==old[key],key
  result={**old,**replay,'batch':BATCH,'binding':binding,'uids':[r['uid'] for r in selected['rows']],'historicalInputHashes':g['inputHashes'],'currentRegionalRebindRequired':False,'cachedOriginalTopologyAndContactsReplayed':ref(PRIOR/'diagnostic.json.gz'),'currentPhysicalReceipt':ref(PHYSICAL/'result.json'),'currentManifestSHA256':manifest,'installationApproved':False,'publication':False}
  refs=[ref(p) for p in [__file__ and HERE/'xl-terrain-recovery-20261010-green18-fresh-original-support-replay-v1.py',PRIOR/'diagnostic.json.gz',PRIOR/'result.json',PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',GEOMETRY,MANIFEST,HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'test_original_ordinary_ground_root_graph_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]];result['evidenceRefs']=refs;assert digest(MANIFEST.read_bytes())==manifest;save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('green18freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-original-topology-support-current-ground-replay-v1',[ROOT/r['path'] for r in refs],dict(uids=result['uids'],completeOriginalFaces=11088,completeOriginalComponentCount=903,resolvedOriginalComponents=result['resolvedOriginalComponents'],independentSourceGraphReplayed=True,installationApproved=False));print(dict(resolved=len(result['resolvedOriginalComponents']),unresolved=903-len(result['resolvedOriginalComponents']),currentDrawnGroundSHA256=binding['currentDrawnGroundSHA256']))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
