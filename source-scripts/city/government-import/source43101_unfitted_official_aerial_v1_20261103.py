"""Small official aerial crop against both complete immutable provider roots.

No fitting, source edits, deletion, identity approval or installation credit.
"""
import argparse,io,math,shutil,sys,time,uuid
from pathlib import Path
import numpy as np
import shapely
from PIL import Image
from pyproj import Transformer
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source43101-unfitted-official-aerial-v1-20261103';SELECT='government-xl-source43101-current-selection-v1-20261029';PROVIDER='government-xl-after-sha-tin-43101-provider-roots-v1-20261029';UID='landsd/43101:0'
API_DOC='https://tools.csdi.gov.hk/csdi-webpage/apidoc/ImageryMapAPI';TNC='https://tools.csdi.gov.hk/csdi-webpage/doc/TNC';LOGO='https://api.hkmapservice.gov.hk/mapapi/landsdlogo.jpg'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists()and not local.exists();c=reservations.claim('source43101-aerial-'+str(uuid.uuid4()),['building:'+UID,'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],'Source reservation unavailable';return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and shutil.disk_usage(local.parent).free>16_000_000;refs=[Path(__file__),HERE/'exact_packed_world_geometry_v2_20261103.py',HERE.parent/'landmark-acquisition/acquire.py'];data={}
    for batch,name in [(SELECT,'selection.json.gz'),(PROVIDER,'summary.json')]:
        _,pins=authenticate(BASE/batch);p=BASE/batch/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',p]);data[batch]=read(p)
    row=data[SELECT]['rows'][0];proof=data[PROVIDER];asset=ROOT/row['candidate']['path'];assert row['uid']==UID and digest(asset.read_bytes())==row['sourceSHA256']==proof['sourceSHA256']and proof['allProviderAndPackedWorldArraysEqual'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());counts=[r['completeFaces']for r in proof['roots']];assert counts==[12154,12154]and len(tri)==24308;pieces=np.split(tri,[counts[0]])
    for part,root in zip(pieces,proof['roots']):assert digest(part.astype('<f8').tobytes())==root['providerWorldSHA256']
    transform=Transformer.from_crs(2326,3857,always_xy=True)
    def mercator(coords):
        q=np.asarray(coords);x,y=transform.transform(q[:,0]+834500,816500-q[:,1]);return np.column_stack([x,y])
    points=mercator(tri[:,:,[0,2]].reshape(-1,2));low,high=points.min(0)-15,points.max(0)+15;world=2*math.pi*6378137;zoom=20;span=world/2**zoom;xmin,xmax=int((low[0]+world/2)//span),int((high[0]+world/2)//span);ymin,ymax=int((world/2-high[1])//span),int((world/2-low[1])//span);tile_count=(xmax-xmin+1)*(ymax-ymin+1);assert tile_count<=9
    net=ac.Network(out/'transfer.json',cap=3_500_000);provenance=[]
    def acquire(url,name,maximum):
        raw,headers=net.get(url,maximum);p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);refs.append(p);entry=dict(url=url,path=str(p.relative_to(ROOT)),sha256=digest(raw),headers=headers);provenance.append(entry);return raw
    acquire(API_DOC,'official-api-documentation.html',150_000);acquire(TNC,'official-terms.html',150_000);logo_raw=acquire(LOGO,'lands-department-logo.jpg',64_000);logo=Image.open(io.BytesIO(logo_raw)).convert('RGB');assert logo.width>10 and logo.height>10
    canvas=Image.new('RGB',((xmax-xmin+1)*256,(ymax-ymin+1)*256));tiles=[]
    for x in range(xmin,xmax+1):
        for y in range(ymin,ymax+1):
            assert reservations.owns(lease);url=f'https://mapapi.hkmapservice.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/{zoom}/{x}/{y}.png';raw=acquire(url,f'official-{zoom}-{x}-{y}.png',256_000);im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(256,256);canvas.paste(im,((x-xmin)*256,(y-ymin)*256));tiles.append(dict(x=x,y=y,**provenance[-1]));time.sleep(.25)
    extent=[xmin*span-world/2,(xmax+1)*span-world/2,world/2-(ymax+1)*span,world/2-ymin*span]
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import OffsetImage,AnnotationBbox
    fig,axes=plt.subplots(1,2,figsize=(14,9),dpi=160)
    for ax in axes:
        ax.imshow(canvas,extent=extent,interpolation='nearest');ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=6);ax.add_artist(AnnotationBbox(OffsetImage(np.asarray(logo),zoom=24/logo.height),(.04,.04),xycoords='axes fraction',frameon=True,box_alignment=(0,0)))
    axes[0].set_title('Official aerial pixels; native surveyed extent')
    projections=[]
    for part,root,color in zip(pieces,proof['roots'],['#ff5544','#00eeff']):
        projection=shapely.union_all(shapely.polygons(part[:,:,[0,2]]));projections.append(dict(name=root['name'],completeOriginalFaces=len(part),sourceWorldSHA256=digest(part.astype('<f8').tobytes()),projectedAreaM2=projection.area))
        for poly in shapely.get_parts(projection):
            if hasattr(poly,'exterior'):
                q=mercator(poly.exterior.coords);axes[1].plot(q[:,0],q[:,1],color=color,linewidth=.7)
    axes[1].set_title('Red B4561111; cyan B456572683001063C0')
    fig.suptitle('43101: both complete original roots at unchanged surveyed placement; no image fitting')
    fig.text(.02,.015,'Aerial Photograph from Lands Department / HKSAR Government / CSDI. Capture date unknown. EPSG2326 to3857.',fontsize=8);fig.tight_layout(rect=[0,.04,1,.96]);image=out/'unfitted-official-aerial-two-roots.png';fig.savefig(image);plt.close(fig);refs.append(image)
    assert reservations.owns(lease)and digest(asset.read_bytes())==row['sourceSHA256']
    result=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],sourceWorldArraySHA256=digest(tri.astype('<f8').tobytes()),providerRoots=projections,tileZoom=zoom,tiles=tiles,aerialMercatorExtent=extent,plottedMercatorBounds=[low.tolist(),high.tolist()],geographicTransform='EPSG:2326 -> EPSG:3857, no fitted translation/rotation/scale',allOriginalFaces=24308,allOriginalRoots=2,image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()),width=2240,height=1440),provenance=provenance,receivedBytes=net.data['receivedBytes'],capBytes=3_500_000,aerialCaptureDateKnown=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,permanentRejection=False,qualification='Primary aerial location context only. Original pixels and untouched source projections use coordinate transforms without visual fitting. Imagery age, obscured features and map alignment require review; aerial proximity alone does not establish complete source identity, permit root deletion or grant physical/publication approval.')
    save(out/'summary.json',result);refs.extend(p for p in out.iterdir()if p.is_file());module('source43101_unfitted_aerial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unfitted-official-aerial-context-for-both-complete-provider-roots',list(dict.fromkeys(refs)),result);print(dict(tiles=len(tiles),receivedBytes=net.data['receivedBytes'],sourceGeometryChanges=0,identityAccepted=False),flush=True)
if __name__=='__main__':main()
