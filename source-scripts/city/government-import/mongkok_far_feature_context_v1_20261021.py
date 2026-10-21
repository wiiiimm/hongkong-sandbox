"""Bind historical far faces to current exact source and render their local context."""
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mongkok-far-feature-context-v1-20261021';DOC=BASE/BATCH

def main():
    assert not DOC.exists()
    current=BASE/'government-xl-remaining-forty-original-identity-v2-20261021'
    _,pins=authenticate(current)
    selection=current/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
    row=next(r for r in read(selection)['rows'] if r['uid']=='landsd/240332:0')
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[str(asset.relative_to(ROOT))]
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
    old=BASE/'government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011/diagnostic.json.gz'
    assert digest(old.read_bytes())=='e908109e5eebaee54e5dcb57861ac3f7a81cbec374afad9f719826fbce459dc8'
    x=read(old);tri=decode_original_world_triangles(asset.read_bytes())
    assert digest(tri.astype('<f8').tobytes())==x['completeOriginalWorldSHA256']
    assert row['source']['building']['rings']==x['historicalTargetForm']['rings']
    foot=shapely.Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:])
    distances=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3)
    ids=np.flatnonzero(distances.max(1)>10);assert ids.tolist()==[r['originalFace']for r in x['all62OriginalFarFaceAttributions']]
    for r in x['all62OriginalFarFaceAttributions']:assert np.array_equal(tri[r['originalFace']],r['completeOriginalTriangle'])
    far=tri[ids];lo=far.min((0,1));hi=far.max((0,1));centre=(lo+hi)/2
    mask=np.all(tri.max(1)>=lo-3,axis=1)&np.all(tri.min(1)<=hi+3,axis=1)
    DOC.mkdir(parents=True);fig=plt.figure(figsize=(16,10))
    for k,angle in enumerate([-60,120]):
        ax=fig.add_subplot(2,2,k+1,projection='3d')
        for faces,color,alpha in [(tri[mask],'lightgray',.5),(far,'crimson',1)]:
            ax.add_collection3d(Poly3DCollection((faces-centre)[:,:,[0,2,1]],facecolor=color,edgecolor='black',linewidth=.15,alpha=alpha))
        dims=np.maximum(hi-lo+6,1);ax.set_xlim(-dims[0]/2,dims[0]/2);ax.set_ylim(-dims[2]/2,dims[2]/2);ax.set_zlim(-dims[1]/2,dims[1]/2);ax.set_box_aspect(dims[[0,2,1]]);ax.view_init(25,angle);ax.set_title('62 far faces (red); nearby unchanged source (grey)')
    ax=fig.add_subplot(223)
    for f in tri:ax.plot(f[[0,1,2,0],0],f[[0,1,2,0],2],color='gray',linewidth=.15)
    for f in far:ax.fill(f[:,0],f[:,2],color='crimson')
    a,b=foot.exterior.xy;ax.plot(a,b,color='blue');ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Whole source plan / recorded footprint / far feature')
    ax=fig.add_subplot(224)
    for f in tri[mask]:ax.plot(f[[0,1,2,0],0],f[[0,1,2,0],1],color='gray',linewidth=.3)
    for f in far:ax.plot(f[[0,1,2,0],0],f[[0,1,2,0],1],color='crimson',linewidth=.6)
    ax.set_aspect('equal');ax.set_title('Local X/Y elevation (metres)');fig.tight_layout();fig.savefig(DOC/'far-feature.png',dpi=140);plt.close(fig)
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],historicalAttributionMatchesCurrentSourceAndFootprint=True,farFaces=ids.tolist(),farBounds=[lo.tolist(),hi.tolist()],maximumExtentM=float(distances.max()),nearbySourceFaces=np.flatnonzero(mask).tolist(),identityAccepted=False,installationApproved=False,qualification='Current exact source and footprint match historical attribution. Rendered red faces are the complete >10m feature, not roof-canopy attribution. Source/photo interpretation remains pending.')
    save(DOC/'summary.json',result)
    module('far_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-far-feature-context',[Path(__file__),selection,asset,tile,old,HERE/'exact_packed_world_geometry_20261009.py'],result)
if __name__=='__main__':main()
