"""Unfitted official aerial overlays for two complete original source extents."""
from pathlib import Path
import io,math,requests
import numpy as np
import shapely
from PIL import Image
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-source157125-identity-imagery-v1-20261022'
DOC=BASE/BATCH
IDENTITY=BASE/'government-xl-grand-aquarium-repaired-boundary-identity-v1-20261022'
REC=BASE/'government-xl-rest-recovered-current-supervisor-v1-20261022-chunk-01-candidates-157125-0-runtime'

def main():
    assert not DOC.exists()
    refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [REC]:
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    recovery=take(REC,REC/'selection.json.gz')['rows']
    transform=Transformer.from_crs(2326,3857,always_xy=True)
    def mercator(coords):
        a=np.asarray(coords);x,y=transform.transform(a[:,0]+834500,816500-a[:,1]);return np.column_stack([x,y])
    world=2*math.pi*6378137;zoom=19;span=world/2**zoom
    boxes=[];needed=set()
    for uid in ['landsd/157125:0']:
        row=next(r for r in recovery if r['uid']==uid)
        p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256']==pins[REC][row['candidate']['path']];refs.append(p)
        t=decode_original_world_triangles(p.read_bytes())
        projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]))
        target=row['source']['building']
        points=mercator(target['rings'][0]);allpoints=mercator(t[:,:,[0,2]].reshape(-1,2))
        low=np.minimum(points.min(0),allpoints.min(0))-25;high=np.maximum(points.max(0),allpoints.max(0))+25
        xmin,xmax=int((low[0]+world/2)//span),int((high[0]+world/2)//span)
        ymin,ymax=int((world/2-high[1])//span),int((world/2-low[1])//span)
        needed|={(x,y) for x in range(xmin,xmax+1) for y in range(ymin,ymax+1)}
        boxes.append((uid,points,projection,low,high,xmin,xmax,ymin,ymax))
    assert len(needed)<=80
    DOC.mkdir();tiles={};provenance=[];session=requests.Session()
    for x,y in sorted(needed):
        url=f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{zoom}/{x}/{y}.png'
        response=session.get(url,timeout=30);response.raise_for_status();raw=response.content
        image=Image.open(io.BytesIO(raw)).convert('RGB');assert image.size==(256,256)
        path=DOC/f'tile-{zoom}-{x}-{y}.png';path.write_bytes(raw);tiles[x,y]=image
        provenance.append(dict(url=url,path=str(path.relative_to(ROOT)),sha256=digest(raw)))
    outputs=[]
    for uid,points,projection,low,high,xmin,xmax,ymin,ymax in boxes:
        canvas=Image.new('RGB',((xmax-xmin+1)*256,(ymax-ymin+1)*256))
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):canvas.paste(tiles[x,y],((x-xmin)*256,(y-ymin)*256))
        extent=[xmin*span-world/2,(xmax+1)*span-world/2,world/2-(ymax+1)*span,world/2-ymin*span]
        fig,axes=plt.subplots(1,2,figsize=(14,8),dpi=160)
        for ax in axes:
            ax.imshow(canvas,extent=extent);ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.set_aspect('equal')
            ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7)
        axes[0].set_title('Official aerial pixels')
        axes[1].plot(points[:,0],points[:,1],color='#ffdf37',linewidth=1)
        for p in shapely.get_parts(projection):
            if hasattr(p,'exterior'):
                a=mercator(p.exterior.coords);axes[1].plot(a[:,0],a[:,1],color='#ff4040',linewidth=.8)
        axes[1].set_title('Target footprint yellow; complete source projection red')
        fig.suptitle('Original source157125 '+uid+' — no alignment adjustment')
        fig.text(.02,.015,'Aerial Photograph from Lands Department · EPSG:2326 → EPSG:3857 · Capture date unknown; identity diagnostic only',fontsize=8)
        fig.tight_layout(rect=[0,.04,1,.96]);path=DOC/(uid.split('/')[1]+'.png');fig.savefig(path);plt.close(fig)
        outputs.append(dict(uid=uid,path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    save(DOC/'provenance.json',dict(tiles=provenance,outputs=outputs,zoom=zoom,captureDateKnown=False,
                                   sourceCRS='EPSG:2326',displayCRS='EPSG:3857',identityAccepted=False,
                                   localToHK80=dict(eastingOffset=834500,northingOrigin=816500,localZIsSouth=True)))
    module('mount_sterling_imagery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'two-whole-original-source-official-aerial-overlays',refs,
        dict(uids=[r['uid'] for r in outputs],tiles=len(tiles),identityAccepted=False,installationApproved=False))

if __name__=='__main__':main()
