"""Inspect the source-native pavilion corresponding to an estimated BASIC canopy."""
import argparse,sys,uuid,gzip
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,MultiPoint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists();rp=BASE/'government-xl-sha-tin-canopy-feature-resources-v1-20261029.json';resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('native-pavilion-feature-packet-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp,HERE.parent/'landsd-territory/source.py'];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take('government-xl-sha-tin-seven-upward-floor-runtime-v1-20261029','selection.json.gz');source=next(r for r in selection['rows']if r['uid']=='landsd/231013:0');asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes())
 b=next(r for r in take('government-xl-sha-tin-seven-upward-floor-scope-v1-20261029','form-obligations.json.gz')if r['uid']=='landsd/92340:0');tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');actual=next(r for r in read(tile)['buildings']if r['uid']==b['uid']);assert actual==b and b['uid']=='landsd/92340:0';refs.append(tile)
 assert b['structureType']=='Open-sided Structure'
 assert b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and b['baseHeightHKPD']is None and b['topHeightHKPD']is None
 csuid=b['buildingCSUID'];assert csuid.isalnum();out.mkdir()
 def query(name,layer,where,geometry=False):
  raw,receipt=request(URL+'/'+str(layer)+'/query',dict(f='json',where=where,outFields='*',returnGeometry='true'if geometry else'false',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'),json_expected=False)
  decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw;(out/(name+'.json')).write_bytes(decoded);save(out/(name+'-request.json'),dict(receipt,decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded));data=read(out/(name+'.json'));assert not data.get('error')and not data.get('exceededTransferLimit');return data['features']
 features=query('official-canopy',0,"BuildingCSUID='"+csuid+"'",True);assert len(features)==1;official=features[0]['attributes'];assert official['BuildingCSUID']==csuid and official['Status']=='Active'and official['BuildingBlockType']=='Open-sided Structure'
 relations=query('official-canopy-relations',1002,"BuildingCSUID='"+csuid+"'")
 basic=Polygon(b['rings'][0],b['rings'][1:]);official_rings=[[(x-834500,816500-y)for x,y in r]for r in features[0]['geometry']['rings']];official_poly=Polygon(official_rings[0],official_rings[1:])
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);eligible=np.flatnonzero((normal[:,1]>0)&(tri[:,:,1].min(1)>b['base']+b['height']))
 projected={int(i):MultiPoint(tri[i][:,[0,2]]).convex_hull for i in eligible};seed={i for i,poly in projected.items()if poly.intersection(basic).area>0};vertex_faces={}
 for i in map(int,eligible):
  for v in tri[i]:vertex_faces.setdefault(tuple(map(float,v)),set()).add(i)
 groups=[];seen=set()
 for start in sorted(seed):
  if start in seen:continue
  component=set();pending=[start]
  while pending:
   i=pending.pop()
   if i in component:continue
   component.add(i)
   for v in tri[i]:pending.extend(vertex_faces[tuple(map(float,v))]-component)
  seen|=component;poly=shapely.union_all([projected[i]for i in component]);ids=sorted(component);t=tri[ids]
  groups.append(dict(sourceFaces=ids,completeComponentProjectedAreaM2=poly.area,basicFootprintOverlapM2=poly.intersection(basic).area,basicFootprintCoverage=poly.intersection(basic).area/basic.area,wholeComponentBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],projection=poly))
 groups.sort(key=lambda r:-r['basicFootprintOverlapM2']);assert groups
 fig,ax=plt.subplots(figsize=(10,9),dpi=170)
 def draw(poly,color,fill=False):
  if poly.geom_type=='Polygon':
   x,y=poly.exterior.xy
   if fill:ax.fill(x,y,color=color,alpha=.3)
   ax.plot(x,y,color=color,linewidth=1.6)
  elif hasattr(poly,'geoms'):
   for p in poly.geoms:draw(p,color,fill)
 for group in groups:draw(group['projection'],'#316ba7',True)
 draw(basic,'#d02d48');draw(official_poly,'#111111');lo=np.minimum(basic.bounds[:2],groups[0]['projection'].bounds[:2])-1;hi=np.maximum(basic.bounds[2:],groups[0]['projection'].bounds[2:])+1
 ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),aspect='equal',xlabel='World X / m',ylabel='World Z / m',title='Exact native upper-roof component(s) versus estimated BASIC canopy\nBlue: unchanged native roof; red: viewer BASIC; black: current official footprint\nNo suppression or identity approval from this packet');ax.grid(alpha=.2);fig.tight_layout();image=out/'native-roof-versus-estimated-canopy.png';fig.savefig(image);plt.close(fig)
 clean=[{k:v for k,v in r.items()if k!='projection'}for r in groups]
 result=dict(uids=[source['uid'],b['uid']],sourceUid=source['uid'],sourceModelId=source['modelId'],sourceSHA256=source['sourceSHA256'],basicUid=b['uid'],buildingCSUID=csuid,basicForm=b,exactCurrentForm=actual,tileSHA256=digest(tile.read_bytes()),officialRecord=official,officialRelations=relations,basicFootprintAreaM2=basic.area,officialFootprintAreaM2=official_poly.area,basicOfficialFootprintHausdorffDistanceM=basic.hausdorff_distance(official_poly),estimatedBasicRoofY=b['base']+b['height'],completeOriginalRoofComponentsAboveEstimatedRoof=clean,image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,featureReplacementApproved=False,suppressionApproved=False,installationApproved=False,publication=False,
  qualification='Fresh exact active official canopy record plus complete connected source upper-surface components from the unchanged government podium. All source-face IDs/bounds and original/native versus2Dfootprint differences are retained; upper components are nomination evidence, not coverage or ownership approval. No source roof is raised, rescaled, clipped or rebuilt. A source-feature judgement and real conditional fallback/runtime checks are still required before suppressing the estimated BASIC canopy.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 module('canopy_feature_packet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'native-pavilion-feature-and-fresh-official-canopy-correspondence-packet',list(dict.fromkeys(refs)),read(out/'summary.json'))

if __name__=='__main__':main()
