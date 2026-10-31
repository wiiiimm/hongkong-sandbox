"""Measure disputed OSM fallback against both unchanged pier originals; no approval."""
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-disneyland-piers-after-passenger-'
BATCH=P+'osm-feature-context-v1-20261030'
OSM='way/334029318:0'

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(suffix,path):
        batch=P+suffix
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def doc(suffix,name):return take(suffix,base/(P+suffix)/name)
    forms=doc('75642-source-scope-v3-20261030','75642:0-forms.json.gz')
    basic=next(r['building']for r in forms if r['building']['uid']==OSM)
    foot=shapely.Polygon(basic['rings'][0],basic['rings'][1:]);assert foot.is_valid and foot.area>0
    primary=base/(P+'osm-way334029318-primary-v1-20261030')
    xml=primary/'way.xml';url=primary/'source-url.txt';refs.extend([xml,url]);way=ET.fromstring(xml.read_bytes()).find('way');assert way.attrib['id']=='334029318'
    tags={r.attrib['k']:r.attrib['v']for r in way.findall('tag')}
    assert tags=={'building':'yes'} and basic['heightSource']=='estimated'and basic['height']==24
    selection=doc('joint-current-ground-v1-20261030','selection.json.gz')
    attrs={r['uid']:r for r in doc('joint-attributes-v1-20261030','attributes.json.gz')['rows']}
    rows=[];fig,axes=plt.subplots(1,2,figsize=(12,6))
    for selected,ax in zip(selection['rows'],axes):
        uid=selected['uid'];attr=attrs[uid];asset=ROOT/selected['candidate']['path'];assert digest(asset.read_bytes())==attr['sourceSHA256']==selected['sourceSHA256'];refs.append(asset)
        idx=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds={'packed':decode_original_world_triangles(asset.read_bytes())}
        for field in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:worlds[field]=np.asarray(attr[field]).reshape(-1,3)[idx]
        for mode,tri in worlds.items():
            assert len(tri)==selected['triangles'];polys=shapely.polygons(tri[:,:,[0,2]]);area=shapely.area(polys);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=normal[:,1]>.25*np.linalg.norm(normal,axis=1)
            mask=(area>0)&shapely.intersects(polys,foot);projection=shapely.union_all(polys[mask]).intersection(foot)
            roofs=[]
            for height in [basic['base'],5,6,7,8,9,10,24]:
                picked=mask&up&(tri[:,:,1].min(1)>=height);coverage=shapely.union_all(polys[picked]).intersection(foot)
                roofs.append(dict(minimumWholeFacetHeightM=height,coverageM2=coverage.area,coverageFraction=coverage.area/foot.area,upwardFacets=int(picked.sum())))
            rows.append(dict(uid=uid,mode=mode,sourceSHA256=selected['sourceSHA256'],completeSourceFaces=len(tri),originalProjectionCoverageFraction=projection.area/foot.area,roof=roofs))
            if mode=='packed':
                for color,shape,label in [('#2c7fb8',shapely.union_all(polys[area>0]),'Original pier projection'),('#e67e22',foot,'Retained OSM fallback')]:
                    for polygon in shapely.get_parts(shape):
                        if polygon.geom_type!='Polygon':continue
                        x,z=polygon.exterior.xy;ax.fill(x,z,color=color,alpha=.3,label=label);label=None
                a,b,c,d=foot.bounds;ax.set_xlim(a-10,c+10);ax.set_ylim(b-10,d+10);ax.set_aspect('equal');ax.set_xlabel('X (m)');ax.set_ylabel('Z (m)');ax.set_title(uid);ax.ticklabel_format(useOffset=False);ax.legend()
    fig.suptitle('Local source projection context only; footprint overlap is not ownership proof')
    out.mkdir();fig.tight_layout();fig.savefig(out/'local-projections.png',dpi=160,bbox_inches='tight');plt.close(fig)
    result=dict(uids=[r['uid']for r in selection['rows']],basicUid=OSM,exactBasicForm=basic,osmPrimarySource=dict(url=url.read_text().strip(),sha256=digest(xml.read_bytes()),version=way.attrib['version'],timestamp=way.attrib['timestamp'],tags=tags),basicFootprintAreaM2=foot.area,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,duplicateSuppressionApproved=False,installationApproved=False,qualification='Current public OSM way has no recorded height or roof type; current24m fallback is explicitly estimated. Exact complete source projection/upward-facet coverage is measured in all four worlds. No object suppression, identity/architectural ownership or foundation acceptance follows from these measurements.')
    save(out/'summary.json',result)
    module('piers_osm_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-pier-versus-retained-osm-primary-and-roof-context',refs,result)
    print([(r['uid'],round(r['originalProjectionCoverageFraction'],4),[(v['minimumWholeFacetHeightM'],round(v['coverageFraction'],4))for v in r['roof']])for r in rows if r['mode']=='packed'])

if __name__=='__main__':main()
