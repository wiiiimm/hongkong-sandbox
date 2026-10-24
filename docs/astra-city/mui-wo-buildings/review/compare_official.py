"""Independent footprint-gap counts and source maps; no city data is modified."""
import collections,gzip,hashlib,json,math,os,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city'))
from build_city import xy,polys
from shapely.geometry import Polygon,Point,GeometryCollection
from shapely.strtree import STRtree
from shapely.ops import unary_union


def official_shape(feature):
    result=GeometryCollection()
    for ring in feature['geometry']['rings']:
        polygon=Polygon([(e-834500,816500-n) for e,n in ring]).buffer(0)
        result=result.symmetric_difference(polygon)
    return result


def main():
    baseline=json.loads((HERE/'current-building-diagnostic.json').read_text())
    source=ROOT/'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz'
    raw=gzip.decompress(source.read_bytes());official=json.loads(raw)
    assert official['bboxWGS84']==baseline['bboxWGS84'],'Compare identical user envelopes'
    village_path=ROOT/'source-scripts/city/regional/nt/surfaces-osm.json.gz'
    village_raw=gzip.decompress(village_path.read_bytes());village_data=json.loads(village_raw)
    villages=[e for e in village_data['elements'] if e['type']=='node' and e.get('tags',{}).get('addr:suburb:en')=='Mui Wo']
    old=baseline['generatedBuildings'];old_shapes=[Polygon(b['rings'][0],b['rings'][1:]).buffer(0) for b in old];tree=STRtree(old_shapes)
    forms=[]
    for f in official['features']:
        shape=official_shape(f)
        if shape.is_empty:continue
        near=[int(i) for i in tree.query(shape.buffer(3)) if old_shapes[i].distance(shape)<=3]
        intersections=[int(i) for i in tree.query(shape) if old_shapes[i].intersects(shape)]
        attrs=f['attributes'];forms.append({'id':attrs['OBJECTID'],'attributes':attrs,'shape':shape,'clearGap':not near,'nearOldUIDs':[old[i]['uid'] for i in near],'intersectingUIDs':[old[i]['uid'] for i in intersections]})
    clusters=[]
    for v in villages:
        centre=Point(xy(v['lon'],v['lat']));circle=centre.buffer(250)
        fs=[f for f in forms if circle.covers(f['shape'].representative_point())]
        osms=[b for b,p in zip(old,old_shapes) if circle.covers(p.representative_point())]
        gaps=[f for f in fs if f['clearGap']]
        clusters.append({'id':'node/'+str(v['id']),'name':v['tags'].get('name:en',v['tags'].get('name')),'zh':v['tags'].get('name:zh-Hant',v['tags'].get('name:zh','')),'lat':v['lat'],'lon':v['lon'],'centreWorld':[centre.x,centre.y],'radiusMetres':250,'officialForms':len(fs),'currentForms':len(osms),'clearGapForms':len(gaps),'clearGapKinds':dict(collections.Counter(f['attributes']['BuildingBlockType'] for f in gaps)),'clearGapObjectIds':[f['id'] for f in gaps],'currentUIDs':[b['uid'] for b in osms]})
    gap_forms=[f for f in forms if f['clearGap']]
    report={'study':'Exact user envelope; snapshot comparison before the official building gap-fill is integrated.','bboxWGS84':official['bboxWGS84'],'officialDatasetVersion':official['datasetVersion'],'officialRetrievedAt':official['retrievedAt'],'officialSource':official['source'],'officialSnapshot':str(source.relative_to(ROOT)),'officialSha256':hashlib.sha256(raw).hexdigest(),'baselineManifestSha256':baseline['manifestSha256'],'villageSource':str(village_path.relative_to(ROOT)),'villageSourceSha256':hashlib.sha256(village_raw).hexdigest(),'counts':{'officialForms':len(forms),'officialKinds':dict(collections.Counter(f['attributes']['BuildingBlockType'] for f in forms)),'currentForms':len(old),'clearGapForms':len(gap_forms),'clearGapKinds':dict(collections.Counter(f['attributes']['BuildingBlockType'] for f in gap_forms))},'gapRule':'An official whole footprint has no current OSM-derived building footprint at a distance of 3 m or less. This conservative spatial screen identifies clear absence; it is not the importer deduplication rule. Every source structure type and footprint area is included.','clusterRule':'250 m circles around retained OSM nodes explicitly tagged addr:suburb:en=Mui Wo. Representative-point inclusion. Circles overlap and are not official village boundaries; counts must not be added together.','clusters':clusters,'clearGaps':[{'objectId':f['id'],'buildingCSUID':f['attributes'].get('BuildingCSUID'),'name':f['attributes'].get('BuildingNameEN'),'kind':f['attributes']['BuildingBlockType'],'area':round(f['shape'].area,2),'centreWorld':[round(f['shape'].centroid.x,2),round(f['shape'].centroid.y,2)]} for f in gap_forms],'limits':['Source feature counts differ from household/building counts because official tower, podium, temporary and open-sided forms are separate.','No footprints are inferred or drawn manually.','This audit captures the pre-gap-fill baseline; later renderer/build changes require a fresh audit.']}
    (HERE/'official-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['counts'],indent=2))
    for cluster in clusters:print(cluster['name'],cluster['currentForms'],'current /',cluster['officialForms'],'official /',cluster['clearGapForms'],'clear gaps')
    os.environ.setdefault('MPLCONFIGDIR','/private/tmp/astra-muiwo-mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch,Patch
    from matplotlib.path import Path
    from shapely.geometry.polygon import orient
    fig,axes=plt.subplots(2,2,figsize=(14,11),dpi=180)
    selected=['Pak Ngan Heung','Tai Tei Tong Village','Luk Tei Tong Village','Wang Tong']
    def draw(ax,polygon,colour,alpha=1):
        for p in polys(polygon):
            p=orient(p,sign=1);parts=[]
            for ring in [p.exterior,*p.interiors]:
                coords=[(x,-z) for x,z in ring.coords];parts.append(Path(coords,[Path.MOVETO]+[Path.LINETO]*(len(coords)-2)+[Path.CLOSEPOLY]))
            ax.add_patch(PathPatch(Path.make_compound_path(*parts),facecolor=colour,edgecolor=colour,linewidth=.25,alpha=alpha))
    for ax,name in zip(axes.flat,selected):
        cluster=next(c for c in clusters if c['name']==name);x,z=cluster['centreWorld'];window=Point(x,z).buffer(355)
        ax.set_facecolor('#f6f3ec')
        for f in forms:
            if window.intersects(f['shape']):draw(ax,f['shape'],'#c36445' if f['clearGap'] else '#ccd1cc',.88)
        for p in old_shapes:
            if window.intersects(p):draw(ax,p,'#286e83')
        ring=Point(x,z).buffer(250).exterior
        ax.plot([a for a,b in ring.coords],[-b for a,b in ring.coords],color='#686e67',linewidth=.8,linestyle='--')
        ax.set_xlim(x-285,x+285);ax.set_ylim(-z-285,-z+285);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
        ax.plot([x-240,x-140],[-z-235,-z-235],color='#253b39',linewidth=2);ax.text(x-190,-z-222,'100 m',ha='center',fontsize=8)
        ax.text(x+246,-z+225,'N ↑',ha='right',fontsize=10,color='#253b39')
        ax.set_title(name+'\n'+f'{cluster["currentForms"]} current forms · {cluster["officialForms"]} official forms · {cluster["clearGapForms"]} clear gaps',fontsize=11,pad=10)
    fig.suptitle('Mui Wo: where the current building source is sparse',fontsize=18,y=.97)
    fig.legend(handles=[Patch(color='#286e83',label='Current OSM-derived building footprint'),Patch(color='#c36445',label='Official footprint >3 m from any current footprint'),Patch(color='#ccd1cc',label='Other official footprint')],loc='lower center',ncol=3,bbox_to_anchor=(.5,.045),fontsize=8)
    fig.text(.5,.025,'Dashed circles: 250 m study areas around sourced village nodes. Counts overlap; these are not village boundaries.',ha='center',fontsize=8)
    fig.text(.5,.011,'Sources: Lands Department Building '+official['datasetVersion']+'; © OpenStreetMap contributors (ODbL). HK1980 metres, north up.',ha='center',fontsize=7)
    fig.subplots_adjust(top=.9,bottom=.1,hspace=.2,wspace=.1)
    fig.savefig(HERE/'mui-wo-village-source-gaps-2520x1980.png',dpi=180)
    fig.savefig(HERE/'mui-wo-village-source-gaps.svg')
    plt.close(fig)
if __name__=='__main__':main()
