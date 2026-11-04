"""Bounded higher-resolution official imagery for exact unresolved source regions."""
from pathlib import Path
import io
import math
import requests
import numpy as np
from PIL import Image
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-sheung-shui-overlap-imagery-v1-20261020'
DOC = BASE/BATCH
PRIOR = BASE/'government-xl-next-twenty-original-identity-v2-20261020'

def main():
    assert not DOC.exists()
    receipt = read(PRIOR/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone() == ('complete',receipt)
    pins = {}
    for item in receipt['evidenceRefs']:
        assert item['path'] not in pins or pins[item['path']] == item['sha256']
        pins[item['path']] = item['sha256']
    for path, sha in pins.items(): assert digest((ROOT/path).read_bytes()) == sha, path
    identity=read(PRIOR/'56054:0/identity.json')
    others=[r for r in identity['freshCurrentIdentity']['intersectingForms'] if not r['sameParent']]
    features=[]
    for r in others:
        tile=ROOT/'3d-viewer'/r['tile'];assert str(tile.relative_to(ROOT)) in pins
        form=next(b for b in read(tile)['buildings'] if b['uid']==r['uid'])
        features.append(dict(type='Feature',geometry=dict(type='Polygon',coordinates=form['rings']),properties=dict(component=r['uid'].split('/')[1],areaM2=r['intersectionAreaM2'])))
    assert len(features)==5
    geo=DOC/'overlap-forms.geojson'
    transform = Transformer.from_crs(2326,3857,always_xy=True)
    def mercator(coords):
        points = np.asarray(coords)
        x,y = transform.transform(points[:,0]+834500,816500-points[:,1])
        return np.column_stack([x,y])
    world = 2*math.pi*6378137
    zoom = 19; span = world/2**zoom
    boxes = []; needed = set()
    for feature in features:
        points = mercator(feature['geometry']['coordinates'][0])
        low, high = points.min(axis=0)-6, points.max(axis=0)+6
        xmin,xmax = int((low[0]+world/2)//span),int((high[0]+world/2)//span)
        ymin,ymax = int((world/2-high[1])//span),int((world/2-low[1])//span)
        tiles = {(x,y) for y in range(ymin,ymax+1) for x in range(xmin,xmax+1)}
        needed |= tiles
        boxes.append((feature,points,low,high,xmin,xmax,ymin,ymax))
    assert len(needed) <= 80, len(needed)
    DOC.mkdir(); save(geo,dict(type="FeatureCollection",features=features)); tiles = {}; refs = []; session = requests.Session()
    for x,y in sorted(needed):
        url = f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{zoom}/{x}/{y}.png'
        response = session.get(url,timeout=60); response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        assert image.size == (256,256)
        path = DOC/f'tile-{zoom}-{x}-{y}.png';path.write_bytes(response.content)
        tiles[(x,y)] = image
        refs.append(dict(url=url,path=str(path.relative_to(ROOT)),sha256=digest(response.content)))
        print('tile',x,y,flush=True)
    outputs = []
    for feature,points,low,high,xmin,xmax,ymin,ymax in boxes:
        canvas = Image.new('RGB',((xmax-xmin+1)*256,(ymax-ymin+1)*256))
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):canvas.paste(tiles[(x,y)],((x-xmin)*256,(y-ymin)*256))
        extent = [xmin*span-world/2,(xmax+1)*span-world/2,world/2-(ymax+1)*span,world/2-ymin*span]
        figure, axes = plt.subplots(1,2,figsize=(12,8),dpi=180)
        for ax in axes:
            ax.imshow(canvas,extent=extent);ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.set_aspect('equal')
            ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7)
        axes[0].set_title('Official imagery, unchanged pixels')
        axes[1].plot(points[:,0],points[:,1],color='#ffdf37',linewidth=1)
        axes[1].set_title('Recorded basic footprint boundary')
        number = feature['properties']['component']
        figure.suptitle(f'Sheung Shui overlapping basic footprint {number}: {feature["properties"]["areaM2"]:.3f} m²')
        figure.text(.02,.015,'Aerial Photograph from Lands Department · Exact EPSG:2326 → EPSG:3857 · Capture date unknown; identity diagnostic only',fontsize=8)
        figure.tight_layout(rect=[0,.04,1,.96])
        path = DOC/f'region-{number}.png';figure.savefig(path);plt.close(figure)
        outputs.append(dict(component=number,path=str(path.relative_to(ROOT)),areaM2=feature['properties']['areaM2']))
    save(DOC/'provenance.json',dict(zoom=zoom,tiles=refs,sourceCRS='EPSG:2326',displayCRS='EPSG:3857',
         sourceRegions=dict(path=str(geo.relative_to(ROOT)),sha256=digest(geo.read_bytes())),
         localToHK80=dict(eastingOffset=834500,northingOrigin=816500,localZIsSouth=True),
         outputs=outputs,captureDateKnown=False,identityAccepted=False,sourceGeometryChanges=0))
    for path, sha in pins.items(): assert digest((ROOT/path).read_bytes()) == sha,path
    result = module('west_imagery_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'sheung-shui-overlapping-basic-footprint-official-imagery-v1',
        [Path(__file__),PRIOR/'result.json',geo,*[ROOT/path for path in pins]],
        dict(uids=['landsd/56054:0'],tiles=len(tiles),regions=5,identityAccepted=False,publication=False))
    print(result['jobId'],flush=True)

if __name__ == '__main__': main()
