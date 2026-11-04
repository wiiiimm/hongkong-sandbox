"""Compare unresolved footprint regions with the unchanged government terrain source."""
from pathlib import Path
import uuid,numpy as np,shapely
from shapely.geometry import shape,box
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-missing-original-ground-v1-20261017';DOC=BASE/BATCH
SHEET=BASE/'government-xl-west-wing26195-missing-sheet-candidates-v2-20261017';COVER=BASE/'government-xl-west-wing26195-missing-coverage-v1-20261017';EXTRA=BASE/'government-xl-west-wing26195-extra-source-coverage-v1-20261017'
def main():
 assert not DOC.exists();r=read(SHEET/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 native=read(SHEET/'sheet-result.json.gz')['result'];assert len(native['terrain'])==1;t=native['terrain'][0];folder=HERE.parent/'central-completion/staged/11-SW-9C';refs=[Path(__file__),SHEET/'result.json',SHEET/'sheet-result.json.gz',COVER/'missing-components.geojson',EXTRA/'remaining.geojson'];paths={}
 for q in t['preparedFiles']:
  if q['path']=='manifest.json':continue
  p=folder/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p);paths[p.suffix]=p
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  helper=module('west_original_ground_decode',HERE/'xl-second-pass.py');ground=helper.context.triangles(paths['.gltf']);assert len(ground)==t['triangles']==97915
  assert np.max(np.abs(np.asarray([ground.min((0,1)),ground.max((0,1))])-np.asarray(t['worldBounds'])))<.002
  polygons=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(polygons);regions=read(COVER/'missing-components.geojson')['features'];remaining=shape(read(EXTRA/'remaining.geojson'));rows=[];selected=set()
  for f in regions:
   region=shape(f['geometry']).intersection(remaining);ids=tree.query(region,predicate='intersects');positive=[int(i)for i in ids if polygons[i].area>0];coverage=shapely.union_all(polygons[positive]).intersection(region) if positive else shapely.GeometryCollection();selected.update(int(i)for i in ids)
   rows.append(dict(component=f['properties']['component'],areaM2=region.area,numericalTerrainProjectionCoverageM2=coverage.area,numericalUncoveredM2=region.difference(coverage).area,originalTerrainFaceIds=[int(i)for i in ids],projectedVerticalOrZeroFaces=[int(i)for i in ids if polygons[i].area==0],unclippedIntersectingFaceYRangeM=[float(ground[ids,:,1].min()),float(ground[ids,:,1].max())]if len(ids)else None))
  save(DOC/'coverage.json',dict(originalTerrainFaces=len(ground),worldSHA256=digest(ground.tobytes()),rows=rows,terrainAsBuildingCoverageCredit=False,identityAccepted=False,sourceGeometryChanges=0,qualification='Numerical terrain projection and complete intersecting source-face context only. Terrain coverage does not prove open space, missing-building absence or installation acceptance.'))
  original=read(BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015/projection.json');h=next(r['sourceSHA256']for r in original['rows']if r['uid']=='landsd/26195:0');q=next(q for q in original['inputRefs']if q['sha256']==h);p=ROOT/q['path'];assert digest(p.read_bytes())==h;tri=decode_original_world_triangles(p.read_bytes());refs.extend([p,BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015/projection.json'])
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d.art3d import Poly3DCollection
  for component in [0,1]:
   region=shape(regions[component]['geometry']);lo=np.asarray(region.bounds[:2])-8;hi=np.asarray(region.bounds[2:])+8;shown=[]
   fig=plt.figure(figsize=(13,6),dpi=160)
   for j,az in enumerate([35,215]):
    ax=fig.add_subplot(1,2,j+1,projection='3d')
    for geom,color,alpha in [(ground,'#b17c43',.8),(tri,'#287e99',.75)]:
     xz=geom[:,:,[0,2]];mask=(xz.max(1)>=lo).all(1)&(xz.min(1)<=hi).all(1);part=geom[mask];shown.append(part)
     ax.add_collection3d(Poly3DCollection(part[:,:,[0,2,1]],facecolor=color,edgecolor='none',alpha=alpha))
    pts=np.concatenate(shown).reshape(-1,3);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(pts[:,1].min(),pts[:,1].max());ax.set_box_aspect((hi[0]-lo[0],hi[1]-lo[1],max(1,pts[:,1].ptp())));ax.view_init(elev=35,azim=az);ax.set_title('Unchanged source geometry');ax.set_xlabel('East');ax.set_ylabel('South');ax.set_zlabel('HKPD height')
   fig.suptitle(f'West Wing missing region {component}: blue building / brown original terrain\nContext only; terrain is not proof of missing-building coverage');fig.tight_layout();fig.savefig(DOC/f'component-{component}.png');plt.close(fig);assert reservations.heartbeat(lease)['ok']
  refs.extend([HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);out=module('west_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-terrain-context-for-missing-footprint-v1',refs,dict(uids=['landsd/26195:0'],originalTerrainFaces=len(ground),intersectingTerrainFaces=len(selected),numericalMissingProjectionM2=sum(r['numericalUncoveredM2']for r in rows),identityAccepted=False,nextStep='Review the two saved complete source/terrain context images against the retained architect plan; retain separate coverage and overlap holds unless source roles are established.'))
  print(dict(jobId=out['jobId'],terrainFaces=len(ground),intersectingFaces=len(selected)),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
