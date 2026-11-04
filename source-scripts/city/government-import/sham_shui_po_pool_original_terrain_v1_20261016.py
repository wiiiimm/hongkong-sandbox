"""Reuse authenticated unchanged government terrain; do not re-download or revive old map evidence."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-original-terrain-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-sham-shui-po-pool-current-ground-v1-20261016';ORIGINAL=BASE/'government-xl-uncovered-qualified-sequence-20261006-265480-0'
def main():
 assert not DOC.exists();current=read(PRIOR/'result.json');old=read(ORIGINAL/'result.json');refs=[Path(__file__),PRIOR/'result.json',ORIGINAL/'result.json'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [current,old]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in current['evidenceRefs']:assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 oldpins={q['path']:q['sha256'] for q in old['evidenceRefs']};recovery=ORIGINAL/'source-recovery.json';assert digest(recovery.read_bytes())==oldpins[str(recovery.relative_to(ROOT))];refs.append(recovery);helper=module('science_original_terrain',HERE/'xl-final-script-pass.py');grounds=[];terrainPaths=[]
 for sheet in read(recovery)['sheets']:
  for item in sheet['terrainFiles']:
   p=ROOT/sheet['cache']/'terrain'/item['name'];rel=str(p.relative_to(ROOT));assert digest(p.read_bytes())==item['sha256'];pins[rel]=item['sha256']
   if p.suffix=='.gltf':terrainPaths.append(rel);grounds.append(helper.s.terrain_triangles(p))
 source=dict(terrainPaths=terrainPaths)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 selection=PRIOR/'selection.json.gz';row=read(selection)['rows'][0];geometry=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';g=read(geometry)['rows'][0];assert g['sourceSHA256']==row['sourceSHA256'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(t)==15629;ground=np.concatenate(grounds);b=row['source']['building'];f=helper.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]))
 # Identify the complete buried source faces and their authored neighbouring faces.
 import shapely
 lo,hi=t.min(axis=(0,1)),t.max(axis=(0,1));native=ground[(ground[:,:,0].max(axis=1)>=lo[0]-1)&(ground[:,:,0].min(axis=1)<=hi[0]+1)&(ground[:,:,2].max(axis=1)>=lo[2]-1)&(ground[:,:,2].min(axis=1)<=hi[2]+1)]
 polys=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;native,polys=native[valid],polys[valid]
 points=np.concatenate([t,t.mean(axis=1)[:,None,:]],axis=1);heights=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,shapely.STRtree(polys)).reshape(-1,4);gaps=points[:,:,1]-heights;buried=np.isfinite(heights).all(axis=1)&(gaps<-.5).all(axis=1);ids=np.flatnonzero(buried)
 assert len(ids)==f['fullyBuriedTriangles']
 floor=t[ids];floorlo,floorhi=floor.min(axis=(0,1)),floor.max(axis=(0,1));near=(t[:,:,0].max(axis=1)>=floorlo[0]-1)&(t[:,:,0].min(axis=1)<=floorhi[0]+1)&(t[:,:,2].max(axis=1)>=floorlo[2]-1)&(t[:,:,2].min(axis=1)<=floorhi[2]+1)
 save(DOC/'buried-source-context.json.gz',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],faceIndices=ids.tolist(),triangles=floor.tolist(),gaps=gaps[ids].tolist(),bounds=[floorlo.tolist(),floorhi.tolist()],neighbourFaceIndices=np.flatnonzero(near).tolist(),neighbourTriangles=t[near].tolist(),classification='Uninterpreted original flat lower faces; no pool-basin or corruption claim yet.',publication=False))
 save(DOC/'summary.json',dict(uid=row['uid'],sourceSHA256=g['sourceSHA256'],terrainPaths=source['terrainPaths'],terrainFaces=len(ground),foundation=f,originalTerrainReceipt=str((ORIGINAL/'result.json').relative_to(ROOT)),sourceSheets=[x['sheet'] for x in read(recovery)['sheets']],historicalMapAcceptanceReused=False,fullAcceptance=False));refs += [selection,geometry,HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py']
 r=module('science_original_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-sham-shui-po-pool-original-terrain-foundation-v1',list(dict.fromkeys(refs)),dict(uids=[row['uid']],foundation=f,newlyInstalled=0,fullAcceptance=False));print(dict(jobId=r['jobId'],foundation=f),flush=True)
if __name__=='__main__':main()
