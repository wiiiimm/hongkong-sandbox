"""Small source-backed LandsD imagery/topographic comparison for unchanged originals.

Geographic context only; never centimetre-level placement or model approval.
"""
import argparse
from io import BytesIO
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import time
import numpy as np
import fitz
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Transformer
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--uid',action='append',required=True)
    ap.add_argument('--layer',choices=['imagery','basemap'],default='basemap')
    a=ap.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert not doc.exists()
    receipt,pins=authenticate(base/a.capture)
    sp=base/a.capture/'selection.json.gz';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))]
    selection=read(sp);rows=[r for r in selection['rows'] if r['uid'] in set(a.uid)]
    assert len(rows)==len(set(a.uid))==len(a.uid) and 0<len(rows)<=4
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==selection['manifestSHA256']
    manifest=read(manifestpath);assert manifest['origin']==[834500,816500]
    refs=[Path(__file__),base/a.capture/'result.json',sp,manifestpath]
    transformer=Transformer.from_crs('EPSG:2326','EPSG:3857',always_xy=True)
    polygons=[];sources={};allpoints=[]
    for row in rows:
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset);sources[row['uid']]=row['sourceSHA256']
        tri=decode_original_world_triangles(raw)
        east=tri[:,:,0]+834500;north=816500-tri[:,:,2]
        x,y=transformer.transform(east.ravel(),north.ravel());xy=np.stack([x,y],axis=1).reshape(-1,3,2)
        p=shapely.union_all(shapely.polygons(xy));polygons.append((row['uid'],p))
        allpoints.append(xy.reshape(-1,2))
    values=np.concatenate(allpoints);lo,hi=values.min(0)-20,values.max(0)+20
    zoom=19;half=20037508.342789244;span=2*half/(2**zoom)
    xmin,xmax=math.floor((lo[0]+half)/span),math.floor((hi[0]+half)/span)
    ymin,ymax=math.floor((half-hi[1])/span),math.floor((half-lo[1])/span)
    count=(xmax-xmin+1)*(ymax-ymin+1);assert 0<count<=25
    doc.mkdir();mosaic=Image.new('RGB',((xmax-xmin+1)*256,(ymax-ymin+1)*256));tiles=[]
    for x in range(xmin,xmax+1):
        for y in range(ymin,ymax+1):
            url=f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/{a.layer}/WGS84/{zoom}/{x}/{y}.png'
            raw,meta=request(url,json_expected=False);tile=Image.open(BytesIO(raw));assert tile.size==(256,256)
            path=doc/'tiles'/f'{zoom}-{x}-{y}.png';path.parent.mkdir(exist_ok=True);path.write_bytes(raw);save(path.with_suffix('.request.json'),meta)
            mosaic.paste(tile.convert('RGB'),((x-xmin)*256,(y-ymin)*256));tiles.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(raw),x=x,y=y,z=zoom,url=url))
            time.sleep(.5)
        print(dict(tileColumnsComplete=x-xmin+1,totalTileColumns=xmax-xmin+1),flush=True)
    logo,meta=request('https://www.landsd.gov.hk/images/landsd_logo.svg',json_expected=False)
    (doc/'landsd-logo.svg').write_bytes(logo);save(doc/'landsd-logo-request.json',meta)
    root=ET.fromstring(logo)
    geometry=[(n.tag,{k:v for k,v in n.attrib.items() if k!='fill'}) for n in root.iter()]
    css=''.join(n.text or '' for n in root.iter() if n.tag.endswith('style'))
    fills=dict(re.findall(r'\.([A-Za-z0-9_-]+)\s*\{\s*fill\s*:\s*(#[0-9A-Fa-f]+)\s*;?\s*\}',css))
    assert len(fills)==5
    for n in root.iter():
        if n.get('class') in fills:
            n.set('fill',fills[n.get('class')])
    assert geometry==[(n.tag,{k:v for k,v in n.attrib.items() if k!='fill'}) for n in root.iter()]
    ET.register_namespace('','http://www.w3.org/2000/svg')
    renderedlogo=ET.tostring(root)
    (doc/'landsd-logo-render-style-expanded.svg').write_bytes(renderedlogo)
    logopdf=fitz.open(stream=renderedlogo,filetype='svg');logoimage=Image.open(BytesIO(logopdf[0].get_pixmap(alpha=True).tobytes('png')))
    logoimage.save(doc/'landsd-logo-render.png')
    extent=[xmin*span-half,(xmax+1)*span-half,half-(ymax+1)*span,half-ymin*span]
    fig,axes=plt.subplots(1,2,figsize=(18,10))
    for ax,title in zip(axes,['Official LandsD '+a.layer,'Same map with exact original source projections']):
        ax.imshow(mosaic,extent=extent,origin='upper',interpolation='nearest');ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_aspect('equal');ax.set_title(title);ax.set_axis_off()
    for color,(uid,geometry) in zip(['#ffb100','#00c9ff','#ef00c5','#ff4433'],polygons):
        parts=list(geometry.geoms) if hasattr(geometry,'geoms') else [geometry]
        for poly in parts:
            if poly.geom_type!='Polygon':continue
            rings=[poly.exterior,*list(poly.interiors)]
            for ring in rings:
                coords=np.asarray(ring.coords);axes[1].plot(coords[:,0],coords[:,1],color=color,linewidth=1.2)
        axes[1].plot([],[],color=color,label=uid,linewidth=2)
    axes[1].legend(loc='upper right',fontsize=9)
    fig.subplots_adjust(left=.01,right=.99,top=.94,bottom=.11,wspace=.02)
    logoax=fig.add_axes([.02,.015,.24,.06]);logoax.imshow(logoimage);logoax.axis('off')
    fig.text(.29,.045,('Aerial Photograph' if a.layer=='imagery' else 'Map')+' from Lands Department | Government copyright',fontsize=11)
    fig.text(.29,.022,'EPSG:2326 -> 3857 via pyproj; acquisition date unconfirmed; geographic context only',fontsize=9)
    fig.savefig(doc/'official-map-comparison.png',dpi=135);plt.close(fig)
    assert digest(manifestpath.read_bytes())==selection['manifestSHA256']
    summary=dict(uids=sorted(sources),sourceSHA256ByUid=sources,tiles=tiles,tileCount=count,zoom=zoom,epsg2326Origin=[834500,816500],sourceProjectionCRS='EPSG:3857',transformDescription=transformer.description,transformAccuracyMetres=transformer.accuracy,fullMosaicExtent=extent,contextExtent=[lo.tolist(),hi.tolist()],mapCopyright=('Aerial Photograph' if a.layer=='imagery' else 'Map')+' from Lands Department',mapLayer=a.layer,imageDateEstablished=False,currentManifestSHA256=selection['manifestSHA256'],imagePath=str((doc/'official-map-comparison.png').relative_to(ROOT)),identityAccepted=False,placementAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Independent officialimagery context, fixedunmodifiedsource geometry, deterministicgeographictransform; nopixelalignment/manuallyshiftedoverlay. Imagery acquisitiondateandcentimetreprecisionnotestablished. No bridgeidentity, ownership, sourceplacement, physical, runtime orpublicationapproval.')
    save(doc/'summary.json',summary)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py');refs.append(HERE.parent/'landsd-territory/source.py')
    module('original_orthophoto_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'bounded-official-map-original-source-projection-context',refs,summary)


if __name__=='__main__':main()
