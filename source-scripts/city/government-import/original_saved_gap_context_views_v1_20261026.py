"""Plot an authenticated original assembly's remaining target-footprint gap."""
from pathlib import Path
import argparse
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


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','selection','coverage','extension']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists() and a.batch.startswith('government-xl-') and '/' not in a.batch
    refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.selection,'selection.json.gz');coverage=take(a.coverage,'summary.json');extension=take(a.extension,'summary.json');raw=take(a.extension,'remaining-target-gap.json.gz')
    assert selected['manifestSHA256']==coverage['currentManifestSHA256']==extension['currentManifestSHA256']
    assert {r['uid']:r['sourceSHA256'] for r in selected['rows']}==coverage['sourceSHA256ByUid']
    gap=shapely.from_geojson(raw['geometry']);assert abs(gap.area-extension['remainingUncoveredTargetAreaM2'])<1e-9
    target=next(r for r in selected['rows'] if r['uid']==coverage['targetUid']);form=target['source']['building'];polygon=shapely.Polygon(form['rings'][0],form['rings'][1:]);center=np.asarray(polygon.centroid.coords[0]);sources=[]
    for row in selected['rows']:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path)
        tri=decode_original_world_triangles(path.read_bytes());sources.append((row['uid'],tri))
    pieces=[g for g in shapely.get_parts(gap) if g.geom_type=='Polygon' and g.area>1e-10];stats=[]
    for g in sorted(pieces,key=lambda g:g.area,reverse=True):
        circle=shapely.maximum_inscribed_circle(g,tolerance=.001)
        stats.append(dict(areaM2=g.area,bounds=list(g.bounds),centroidXZ=list(g.centroid.coords[0]),estimatedInscribedRadiusM=circle.length,inscribedCircleToleranceM=.001))
    fig,axes=plt.subplots(1,2,figsize=(15,9),layout='constrained')
    for ax in axes:
        for uid,tri in sources:
            pc=PolyCollection(tri[:,:,[0,2]]-center,facecolors='#bac8ce',edgecolors='none',alpha=.7);ax.add_collection(pc)
        for ring in form['rings']:
            points=np.asarray(ring)-center;points=np.vstack([points,points[0]]);ax.plot(points[:,0],points[:,1],color='#b11722',linewidth=1.1)
        for g in pieces:
            v=np.asarray(g.exterior.coords)-center;ax.fill(v[:,0],v[:,1],facecolor='#ed35b0',edgecolor='#661148',hatch='///',linewidth=.7)
        ax.set_aspect('equal');ax.set_xlabel('Local east (m)');ax.set_ylabel('Local viewer Z (m; positive=south)')
    lo=np.asarray(polygon.bounds[:2])-center;hi=np.asarray(polygon.bounds[2:])-center
    axes[0].set_xlim(lo[0]-15,hi[0]+15);axes[0].set_ylim(lo[1]-15,hi[1]+15);axes[0].set_title('All seven original sources; target red; remaining gap magenta')
    largest=max(pieces,key=lambda g:g.area);lo=np.asarray(largest.bounds[:2])-center;hi=np.asarray(largest.bounds[2:])-center
    axes[1].set_xlim(lo[0]-8,hi[0]+8);axes[1].set_ylim(lo[1]-8,hi[1]+8);axes[1].set_title('Largest remaining gap; existing installed models add no coverage')
    out.mkdir();fig.savefig(out/'remaining-gap-context.png',dpi=140);plt.close(fig)
    result=dict(uids=coverage['uids'],targetUid=coverage['targetUid'],sourceSHA256ByUid=coverage['sourceSHA256ByUid'],remainingTargetAreaM2=gap.area,positiveAreaPieces=len(pieces),pieces=stats,sourceGeometryChanges=0,installationApproved=False,identityApproved=False,qualification='Diagnostic Float64 projected areas and approximate inscribed-circle radii. Viewer positive Z is south. Existing source triangles and baseline footprints are unchanged. Figure shows geometric gap location only, not whether the recorded footprint or original model is architecturally correct; no removal or source-corruption permission.')
    save(out/'summary.json',result)
    module('original_gap_context_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'saved-original-companion-gap-location-context',refs,result)
    print(dict(areaM2=gap.area,pieces=len(pieces),largest=stats[:5]),flush=True)


if __name__=='__main__':main()
