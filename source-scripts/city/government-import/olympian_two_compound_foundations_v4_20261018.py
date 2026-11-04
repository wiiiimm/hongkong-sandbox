"""Complete unchanged tower foundations against both originals and retained candidate terrain."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018';BATCH='government-xl-olympian-two-compound-foundations-v4-20261018';DOC=BASE/BATCH

def check(args):
 row,ground,building=args
 tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)]
 final=module('olympian_full_foundation',HERE/'xl-final-script-pass.py');f=final.foundation_context(tri,ground,Polygon(building['rings'][0],building['rings'][1:]));ok=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0 and f['fullyBuriedUpwardTriangles']==0
 result=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],strictFoundationAccepted=ok,foundation=f);print(dict(uid=row['uid'],passed=ok,faces=f['triangles'],covered=f['completeTerrainTriangles'],buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles']),flush=True);return result

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json',HERE/'xl-final-script-pass.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);d=read(PRIOR/'geometry-inputs.json.gz')
 old=BASE/'government-xl-olympian-two-source-local-terrain-20261008';oldresult=read(old/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(oldresult['jobId'],)).fetchone()==('complete',oldresult)
 oldpins={e['path']:e['sha256']for e in oldresult['evidenceRefs']};refs.append(old/'result.json')
 def oldread(p):
  assert digest(p.read_bytes())==oldpins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=oldread(old/'selection.json.gz');candidates=oldread(old/'terrain-candidates.json')
 for candidate in candidates:
  path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256'];refs.append(path)
 selection['manifestSHA256']=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
 for row in selection['rows']:
  tile=ROOT/'3d-viewer'/row['source']['tile'];row['source']['building']=next(x for x in read(tile)['buildings']if x['uid']==row['uid'])
 save(DOC/'selection.json.gz',selection);terrain=DOC/'runtime-geometry.json.gz';assetdir=(ROOT/selection['rows'][0]['candidate']['path']).parent.parent
 assert assetdir/selection['rows'][0]['candidate']['entry']['asset']==ROOT/selection['rows'][0]['candidate']['path']
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str(terrain.relative_to(ROOT)),'--candidates',str(assetdir.relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(terrain);assert len(capture['rows'])==1 and not any(x.get('error')for x in read(DOC/'metrics.json')['rows'])
 for path,h in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 g=np.asarray(capture['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3)
 supports=[np.asarray(s['position']).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)]for s in d['rows']if s['uid']not in d['towerUIDs']];ground=np.concatenate([g,*supports]);tile=ROOT/'3d-viewer/city/data/tiles/0_-2.json';tilehash=digest(tile.read_bytes());forms={b['uid']:b for b in read(tile)['buildings']};refs.append(tile)
 with ProcessPoolExecutor(max_workers=4)as pool:rows=list(pool.map(check,[(r,ground,forms[r['uid']])for r in d['rows']if r['uid']in d['towerUIDs']]))
 assert digest(tile.read_bytes())==tilehash
 save(DOC/'foundations.json',dict(rows=rows,fullAcceptance=False,qualification='Exact original source coordinates, both original podium meshes and fresh current rendered terrain without the historical terrain candidate. Complete face/centroid foundation check only. Current affected-neighbour and four-mode production qualification remain separate.'))
 out=module('olympian_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-complete-original-four-tower-compound-foundations-v4',list(set(refs)),dict(uids=d['towerUIDs'],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
