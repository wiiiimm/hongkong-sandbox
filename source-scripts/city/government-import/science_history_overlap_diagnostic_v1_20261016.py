"""Measure every positive packed-terrain overlap; retain failures without publication."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-science-history-overlap-diagnostic-v1-20261016';CAND=BASE/'government-xl-science-history-combined-private-terrain-v2-20261016'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in ['government-xl-science-museum-original-terrain-v2-20261016','government-xl-history-museum-original-installed-v1-20261016','government-xl-fu-tor-loy-current-ground-v1-20261016']:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 patch=CAND/'pre-validation-terrain.json';m=read(patch)['nativeMesh'];t=np.asarray(m['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];polys=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ids=np.flatnonzero(valid);ps=polys[valid];tree=shapely.STRtree(ps);pairs=tree.query(ps,predicate='intersects');rows=[]
 for ia,ib in zip(*pairs):
  if ia>=ib:continue
  q=ps[ia].intersection(ps[ib])
  if q.area<=1e-10:continue
  coords=shapely.get_coordinates(q);heights=[]
  for face in [t[ids[ia]],t[ids[ib]]]:
   a,b,c=face;n=np.cross(b-a,c-a);heights.append(a[1]-(n[0]*(coords[:,0]-a[0])+n[2]*(coords[:,1]-a[2]))/n[1])
  rows.append(dict(faces=[int(ids[ia]),int(ids[ib])],areaM2=q.area,maximumHeightDifferenceM=float(np.max(np.abs(heights[0]-heights[1]))),intersectionGeoJSON=shapely.to_geojson(q),faceVertices=[t[ids[ia]].tolist(),t[ids[ib]].tolist()]))
 summary=dict(pairs=len(rows),totalPairAreaM2=sum(r['areaM2'] for r in rows),maximumPairAreaM2=max(r['areaM2'] for r in rows),maximumHeightDifferenceM=max(r['maximumHeightDifferenceM'] for r in rows),pairFacesExceedingFourMillimetres=[r['faces'] for r in rows if r['maximumHeightDifferenceM']>.004],liveTerrainChanged=False,sourceBuildingGeometryChanges=0,fullAcceptance=False,nextStep='Trace the exact flagged seam faces to constructor/source ancestry and repair the scripted terrain seam; preserve installed History Museum and all current actor scopes. No model corruption or permanent rejection follows.')
 DOC.mkdir();save(DOC/'overlap-pairs.json.gz',dict(summary=summary,rows=rows));save(DOC/'summary.json',summary)
 for version in [1,2]:
  folder=BASE/f'government-xl-science-history-combined-private-terrain-v{version}-20261016';log=Path(f'/tmp/science-history-combined-private-v{version}.log');(folder/'failed-worker.log').write_bytes(log.read_bytes());refs += [HERE/f'science_history_combined_private_terrain_v{version}_20261016.py',*[p for p in folder.rglob('*') if p.is_file()]]
 refs += [HERE/'resolve-pass.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']
 r=module('science_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'complete-packed-shared-museum-terrain-overlap-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/80343:0','landsd/4759:0'],summary=summary,newlyInstalled=0,fullAcceptance=False));print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
