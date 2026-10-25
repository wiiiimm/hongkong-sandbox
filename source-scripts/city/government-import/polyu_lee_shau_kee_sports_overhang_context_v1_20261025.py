"""Measure exact original tower extension over the unchanged Sports Centre; no approval."""
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-lee-shau-kee-sports-overhang-context-v1-20261025'
RT='government-xl-polyu-lee-shau-kee-current-ground-v2-20261025'
AT='government-xl-polyu-lee-shau-kee-current-attributes-v2-20261025'
ID='government-xl-polyu-lee-shau-kee-current-identity-v2-20261025'
SCOPE='government-xl-polyu-lee-shau-kee-current-scope-v2-20261025'
INV='government-xl-after-school-current-inventory-v1-20261025'
NATIVE='government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025'
UID='landsd/305600:0';SPORT='landsd/305582:0'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        p=BASE/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selected=take(RT,'selection.json.gz');r=next(r for r in selected['rows']if r['uid']==UID)
    attr=next(r for r in take(AT,'attributes.json.gz')['rows']if r['uid']==UID)
    assert attr['sourceSHA256']==r['sourceSHA256']
    asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
    raw=take(ID,'305600:0/identity.json');context=take(ID,'305600:0/context.json')['identity']
    assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
    assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']
    assert context['targetCoveredBySourceProjection']>=.95 and context['sourceExcessMaximumDistanceFromTargetM']<=10
    native=next(r for r in take(NATIVE,'native-input.json.gz')['rows']if r['uid']==SPORT)
    cat=ROOT/native['cataloguePath'];assert next(r for r in read(cat)['models']if r['uid']==SPORT)==native['entry'];refs.append(cat)
    sportasset=ROOT/native['path'];assert digest(sportasset.read_bytes())==native['entry']['sha256'];refs.append(sportasset)
    tile=ROOT/'3d-viewer'/next(r['tile']for r in context['intersectingForms']if r['uid']==SPORT)
    sport=next(f for f in read(tile)['buildings']if f['uid']==SPORT);assert sport==native['building'];refs.append(tile)
    sb=next(r for r in take(INV,'complete-bounds.json.gz')['rows']if r['uid']==SPORT)
    assert sb['sourceSHA256']==native['entry']['sha256']
    target=shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:])
    sports=shapely.Polygon(sport['rings'][0],sport['rings'][1:])
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    rows=[];fig,axes=plt.subplots(1,2,figsize=(13,7))
    for j,(mode,tri)in enumerate(worlds.items()):
        polys=shapely.polygons(tri[:,:,[0,2]]);projection=shapely.union_all(polys)
        overlap=projection.difference(target).intersection(sports)
        assert 0<overlap.area<=context['sourceExcessCoveredByUnrelatedFormsM2']+1e-7
        assert abs(overlap.area-context['sourceExcessCoveredByUnrelatedFormsM2'])<1e-6
        ids=[]
        for i in shapely.STRtree(polys).query(sports,predicate='intersects'):
            if polys[i].difference(target).intersection(sports).area>1e-10:ids.append(int(i))
        assert ids
        low=float(tri[ids,:,1].min());top=float(sb['completeFourWorldBounds'][j][1][1]);assert low>top
        rows.append(dict(mode=mode,completeSourceFaces=len(tri),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),sourceExcessOverSportsM2=float(overlap.area),originalFaceIds=sorted(ids),conservativeOriginalFaceMinimumYM=low,completeSportsMaximumYM=top,conservativeVerticalSeparationM=low-top))
        if j==0:
            ax=axes[0];ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors='#d4d8d8',edgecolors='none'));ax.add_collection(PolyCollection(tri[ids][:,:,[0,2]],facecolors='#c95641',edgecolors='none'))
            for p,color,label in [(target,'#235c95','current tower record'),(sports,'#ae771e','Sports Centre record')]:
                x,z=p.exterior.xy;ax.plot(x,z,color=color,label=label)
            ax.autoscale_view();ax.set_aspect('equal');ax.legend();ax.set_title('Original tower; red=flagged elevated extension')
            f=tri[ids];xyz=f.reshape(-1,3);axes[1].scatter(xyz[:,0],xyz[:,1],s=3,color='#c95641');axes[1].axhline(top,color='#ae771e',label='Highest Sports Centre vertex');axes[1].set_xlabel('Local east metres');axes[1].set_ylabel('HKPD metres');axes[1].legend();axes[1].set_title('Every flagged face above complete Sports Centre')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    out.mkdir();fig.tight_layout();fig.savefig(out/'original-overhang-and-native-height-context.png',dpi=150);plt.close(fig)
    result=dict(uids=[UID,SPORT],sourceSHA256=r['sourceSHA256'],installedSportsSHA256=native['entry']['sha256'],rows=rows,rawIdentityFailures=raw['reasons'],identityAccepted=False,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,nativeMetadataChanges=0,qualification='Entire raw unrelated projection excess is accounted for by exact original elevated source facets over the unchanged Sports Centre record. Every contributing triangle is conservatively above the entire installed Sports source in all4streams. This is source-role/identity context, not approval or a general campus/overlap exemption; raw flags and all original geometry remain.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('polyu_overhang_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-world-original-tower-elevated-extension-over-current-sports-context',refs,result)


if __name__=='__main__':main()
