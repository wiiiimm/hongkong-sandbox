"""Unfitted government aerial and attributed primary photographic pier context."""
from pathlib import Path
import io,math,urllib.request
import numpy as np
import shapely
from PIL import Image
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
P='government-xl-disneyland-piers-after-passenger-';BATCH=P+'primary-imagery-v1-20261030'
def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 def take(s,n):
  b=base/(P+s)
  if s not in pins:pins[s]=authenticate(b)[1];refs.append(b/'result.json')
  p=b/n;assert digest(p.read_bytes())==pins[s][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=take('all-basic-fallback-patch-runtime-v2-20261030','selection.json.gz')['rows'];forms=take('joint-model-scope-v1-20261030','75643:0-forms.json.gz');osm=next(r['building']for r in forms if r['building']['uid']=='way/334029318:0')
 transform=Transformer.from_crs(2326,3857,always_xy=True)
 def mercator(coords):
  a=np.asarray(coords);x,y=transform.transform(a[:,0]+834500,816500-a[:,1]);return np.column_stack([x,y])
 projections=[];allpoints=[]
 for row in rows:
  p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p)
  tri=decode_original_world_triangles(p.read_bytes());projections.append((row['uid'],shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))));allpoints.append(mercator(tri[:,:,[0,2]].reshape(-1,2)))
 points=np.concatenate(allpoints);low,high=points.min(0)-15,points.max(0)+15
 world=2*math.pi*6378137;zoom=20;span=world/2**zoom
 xmin,xmax=int((low[0]+world/2)//span),int((high[0]+world/2)//span);ymin,ymax=int((world/2-high[1])//span),int((world/2-low[1])//span)
 assert (xmax-xmin+1)*(ymax-ymin+1)<=64
 out.mkdir();provenance=[];canvas=Image.new('RGB',((xmax-xmin+1)*256,(ymax-ymin+1)*256))
 for x in range(xmin,xmax+1):
  for y in range(ymin,ymax+1):
   url=f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{zoom}/{x}/{y}.png';raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-source-research/1.0'}),timeout=30).read();im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(256,256);p=out/f'official-{zoom}-{x}-{y}.png';p.write_bytes(raw);canvas.paste(im,((x-xmin)*256,(y-ymin)*256));provenance.append(dict(url=url,path=str(p.relative_to(ROOT)),sha256=digest(raw)));refs.append(p)
 extent=[xmin*span-world/2,(xmax+1)*span-world/2,world/2-(ymax+1)*span,world/2-ymin*span];fig,axes=plt.subplots(1,2,figsize=(14,9),dpi=160)
 for ax in axes:ax.imshow(canvas,extent=extent);ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=6)
 axes[0].set_title('Unmodified official aerial pixels')
 for (uid,projection),color in zip(projections,['#ff5555','#55ddff']):
  for poly in shapely.get_parts(projection):
   if hasattr(poly,'exterior'):
    a=mercator(poly.exterior.coords);axes[1].plot(a[:,0],a[:,1],color=color,linewidth=.7)
 a=mercator(osm['rings'][0]);axes[1].plot(a[:,0],a[:,1],color='#ffdd22',linewidth=2);axes[1].set_title('Original piers red/cyan; retained OSM yellow')
 fig.suptitle('Disneyland piers: exact original placement; no image fitting or model edits');fig.text(.02,.015,'Aerial Photograph from Lands Department; capture date unknown. EPSG:2326 to EPSG:3857. Identity diagnostic only.',fontsize=8);fig.tight_layout(rect=[0,.04,1,.96]);p=out/'unfitted-official-aerial.png';fig.savefig(p);plt.close(fig);refs.append(p)
 photos=[dict(filename='lighthouse-Malcolm-Koo-20111212.jpg',url='https://upload.wikimedia.org/wikipedia/commons/e/e8/Disney_Resort_Pier%2C_Lighthouse_%28Hong_Kong%29.jpg',sourcePage='https://commons.wikimedia.org/wiki/File:Disney_Resort_Pier,_Lighthouse_(Hong_Kong).jpg',author='Malcolm Koo (Mk2010)',date='2011-12-12',licence='CC BY 4.0 attribution option stated on source page; also CC BY-SA 3.0'),dict(filename='pier-lighting-design-photograph.jpg',url='https://images.squarespace-cdn.com/content/v1/5f8da7c5df62f739cc22a9f6/1607964337774-59N5HZ2XIRU4LOG6GP4Z/Penny%2BBay%2BPier%2Bat%2BNight.jpg',sourcePage='https://www.fkaild.com/landscape/penny-bay-masterplan',author='Francis Krahe and Associates project portfolio',date=None,licence='Copyright holder portfolio; local source research only, no viewer redistribution')]
 for item in photos:
  try:
   raw=urllib.request.urlopen(urllib.request.Request(item['url'],headers={'User-Agent':'HongKongSandbox-source-research/1.0'}),timeout=30).read();im=Image.open(io.BytesIO(raw));assert im.width>100 and im.height>100;p=out/item['filename'];p.write_bytes(raw);item.update(path=str(p.relative_to(ROOT)),sha256=digest(raw),dimensions=[im.width,im.height]);refs.append(p)
  except Exception as e:item['downloadError']=str(e)
 result=dict(uids=[r['uid']for r in rows],tiles=provenance,photographs=photos,exactOSMForm=osm,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,aerialCaptureDateKnown=False)
 save(out/'provenance.json',result);refs.append(out/'provenance.json');module('pier_primary_imagery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unfitted-official-aerial-and-primary-photographic-context',refs,result);print(dict(tiles=len(provenance),photographs=[{k:v for k,v in p.items()if k in ['filename','dimensions','downloadError']}for p in photos]))
if __name__=='__main__':main()
