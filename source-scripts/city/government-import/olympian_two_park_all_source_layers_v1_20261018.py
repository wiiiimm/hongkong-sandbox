"""All original assembly layers at the remaining canonical interface points."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-park-all-source-layers-v1-20261018';DOC=BASE/BATCH
NAMES=['government-xl-olympian-two-fourteen-source-projection-context-v1-20261018','government-xl-olympian-two-park-foundations-contacts-v1-20261018']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sources=read(BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018/geometry-inputs.json.gz')['rows']
 for s in read(BASE/'government-xl-olympian-two-park-avenue-restored-v1-20261018/restored.json')['rows']:
  raw=(ROOT/s['assetPath']).read_bytes();assert digest(raw)==s['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==s['triangles'];sources.append(dict(uid=s['uid'],sourceSHA256=s['sourceSHA256'],position=tri.reshape(-1).tolist(),index=list(range(tri.size//3))))
 assert len(sources)==len({s['uid']for s in sources})==14
 points=[dict(uid=r['uid'],position=d['position'])for r in read(BASE/NAMES[1]/'support-checks.json.gz')['rows']for d in r['unresolved']];assert len(points)==109
 save(DOC/'inputs.json.gz',dict(sources=sources,points=points))
 tool=HERE/'olympian-two-residual-all-source-layers-v1-20261018.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True)
 data=read(DOC/'layers.json.gz');summary=dict(points=len(data['rows']),withContactLayer=sum(x['hasContactLayer']for x in data['rows']),fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([tool,HERE/'support-contact.mjs',HERE/'exact_packed_world_geometry_20261009.py'])
 out=module('olympian_residual_layer_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-109-park-residual-fourteen-original-layer-diagnostic-v1',list(set(refs)),dict(uids=[s['uid']for s in sources],**summary));print(out['jobId'],flush=True)
if __name__=='__main__':main()
