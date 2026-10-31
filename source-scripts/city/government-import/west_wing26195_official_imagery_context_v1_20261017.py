"""Bounded georeferenced LandsD imagery context; no model acceptance or modification."""
from pathlib import Path
import json,math,time,hashlib,io
import requests,numpy as np
from PIL import Image
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'government-xl-west-wing26195-official-imagery-context-v1-20261017'
GEO=BASE/'government-xl-west-wing26195-missing-coverage-v1-20261017/missing-components.geojson'
assert not DOC.exists();DOC.mkdir()
tr=Transformer.from_crs(2326,3857,always_xy=True);z=18;world=2*math.pi*6378137;span=world/2**z
features=json.loads(GEO.read_text())['features']
def merc(coords):
 q=np.asarray(coords);x,y=tr.transform(q[:,0]+834500,816500-q[:,1]);return np.column_stack([x,y])
allpoints=np.concatenate([merc(f['geometry']['coordinates'][0])for f in features]);low=allpoints.min(axis=0)-30;high=allpoints.max(axis=0)+30
xmin=int((low[0]+world/2)//span);xmax=int((high[0]+world/2)//span);ymin=int((world/2-high[1])//span);ymax=int((world/2-low[1])//span)
assert (xmax-xmin+1)*(ymax-ymin+1)<=16
refs=[];canvas=None
for y in range(ymin,ymax+1):
 for x in range(xmin,xmax+1):
  url=f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{z}/{x}/{y}.png'
  response=requests.get(url,timeout=60);response.raise_for_status();im=Image.open(io.BytesIO(response.content)).convert('RGB');assert im.size==(256,256)
  p=DOC/f'tile-{z}-{x}-{y}.png';p.write_bytes(response.content);refs.append(dict(url=url,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(response.content).hexdigest()))
  if canvas is None:canvas=Image.new('RGB',((xmax-xmin+1)*256,(ymax-ymin+1)*256))
  canvas.paste(im,((x-xmin)*256,(y-ymin)*256));time.sleep(.3)
logo_url='https://www.landsd.gov.hk/images/landsd_logo.svg';r=requests.get(logo_url,timeout=60);r.raise_for_status();(DOC/'landsd_logo.svg').write_bytes(r.content)
left=xmin*span-world/2;right=(xmax+1)*span-world/2;top=world/2-ymin*span;bottom=world/2-(ymax+1)*span
fig,ax=plt.subplots(figsize=(11,13),dpi=160);ax.imshow(canvas,extent=[left,right,bottom,top])
for f in features:
 p=merc(f['geometry']['coordinates'][0]);ax.add_patch(Polygon(p,facecolor='#ff3333',edgecolor='#ffdddd',alpha=.35,linewidth=.7))
 if f['properties']['areaM2']>1:ax.text(*p.mean(axis=0),str(f['properties']['component']),color='white',fontsize=10,bbox=dict(facecolor='black',alpha=.6,pad=1))
ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain');ax.set_title('West Wing unresolved footprint on LandsD imagery\nExact CRS transformation; imagery date/roof displacement not assumed')
fig.text(.02,.015,'Aerial Photograph from Lands Department · Source-identity diagnostic only',fontsize=9)
fig.tight_layout(rect=[0,.035,1,1]);fig.savefig(DOC/'context.svg');plt.close(fig)
# Embed the official logo into the standalone SVG rather than rasterising it.
import xml.etree.ElementTree as ET
p=DOC/'context.svg';tree=ET.parse(p);root=tree.getroot();logo=ET.fromstring(r.content);logo.set('x','550');logo.set('y','900');logo.set('width','200');logo.set('height','32');root.append(logo);tree.write(p,encoding='utf-8',xml_declaration=True)
meta=dict(tiles=refs,logo=dict(url=logo_url,sha256=hashlib.sha256(r.content).hexdigest()),apiDocumentation='https://tools.csdi.gov.hk/csdi-webpage/apidoc/ImageryMapAPI',sourceCRS='EPSG:2326',displayCRS='EPSG:3857',localToHK80=dict(eastingOffset=834500,northingOrigin=816500,localZIsSouth=True),input=dict(path=str(GEO.relative_to(ROOT)),sha256=hashlib.sha256(GEO.read_bytes()).hexdigest()),imageryCaptureDateKnown=False,identityAccepted=False,publicationApproved=False,sourceGeometryChanges=0)
(DOC/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(dict(tiles=len(refs),output=str(DOC.relative_to(ROOT)),approval=False)))
