"""Compare complete immutable Murray podium to authenticated original terrain; no publication."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-murray-current-pair-physical-v1-20261017'
BATCH='government-xl-murray-original-terrain-foundation-v2-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in {(r['path'],r['sha256'])for r in receipt['evidenceRefs']}:assert digest((ROOT/p).read_bytes())==h,p
 historical=HERE/'local/government-xl-murray-current-nested-terrain-20261008/terrain-central-with-sun-yat-sen.json'
 patch=next(p for p in read(historical)['patches']if p.get('meta',{}).get('targetUids')==['landsd/265825:0'])
 source=patch['meta']['source']['nativeSources'][0];folder=HERE/'local/government-xl-terrain-sources-20260924/sheets/11-SW-14A'
 proof=read(folder/'original/download.json');directory=read(folder/'directory/result.json')
 assert proof['directorySHA256']==directory['directorySHA256']==source['directorySHA256']
 refs=[Path(__file__),historical,PRIOR/'result.json',PRIOR/'selection.json.gz',folder/'original/download.json',folder/'directory/result.json']
 files=source['sourceFiles']
 for e in files:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];assert any(x['sha256']==e['sha256']for x in proof['entries']);refs.append(p)
 second=module('murray_terrain_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
 terrain=np.concatenate([second.terrain_triangles(ROOT/e['path'])for e in files if e['path'].endswith('.gltf')])
 final=module('murray_original_foundation',HERE/'xl-final-script-pass.py')
 rtpath=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';refs.append(rtpath)
 rt=read(rtpath);row=next(r for r in read(PRIOR/'selection.json.gz')['rows']if r['uid']=='landsd/248655:0');g=next(r for r in rt['rows']if r['uid']==row['uid'])
 t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(t)==5496
 b=row['source']['building'];foundation=final.foundation_context(t,terrain,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 faces=BASE/'government-xl-murray-buried-faces-v1-20261017/faces.json';refs.append(faces)
 points=np.asarray([r['samplePoints']for r in read(faces)['rows']]);polygons=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
 heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain[valid],shapely.STRtree(polygons[valid])).reshape(-1,4)
 def finite_values(values):return [float(v) if np.isfinite(v) else None for v in values]
 rows=[dict(faceIndex=r['faceIndex'],originalTerrainHeights=finite_values(heights[i]),originalTerrainGaps=finite_values(points[i,:,1]-heights[i]),currentTerrainGaps=r['groundOnlyGaps'])for i,r in enumerate(read(faces)['rows'])]
 save(DOC/'flagged-face-comparison.json',dict(rows=rows,terrainTriangles=len(terrain),terrainBounds=[terrain.min(axis=(0,1)).tolist(),terrain.max(axis=(0,1)).tolist()],modelBounds=[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()],uncoveredSamples=int((~np.isfinite(heights)).sum()),source=source,installationApproved=False))
 refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']);refs.extend(p for p in (HERE/'local'/BATCH).rglob('*')if p.is_file())
 result=module('murray_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-whole-original-podium-source-terrain-foundation-v2',refs,dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],foundation=foundation,flaggedFaces=rows,originalTerrainOnly=True,fullAcceptance=False,nextStep='If original terrain resolves burial, construct a current source-preserving terrain candidate and validate full affected scope; otherwise investigate remaining exact source intersections.'))
 print(dict(jobId=result['jobId'],terrainTriangles=len(terrain),buried=foundation['fullyBuriedTriangles'],upward=foundation['fullyBuriedUpwardTriangles'],area=foundation['fullyBuriedAreaM2']),flush=True)
if __name__=='__main__':main()
