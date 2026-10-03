"""Retain closed iB1000 footbridge boundaries; never assign placeholder Z a datum."""
import hashlib,json,pathlib,xml.etree.ElementTree as ET,zipfile
from shapely.geometry import LineString,Polygon
from shapely.ops import unary_union,polygonize
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
CODEBOOK='https://www.landsd.gov.hk/doc/en/mapping/digital-map/common/feature/ib1_gml_mf.pdf'

def build():
    result={'schemaVersion':1,'kind':'tai-o-plan-only-footbridge-linework','crs':'EPSG:2326','codebook':CODEBOOK,'heightPolicy':'Source GML has placeholder Z=0. No deck elevation is assigned; these are plan-only source polygons, not a surveyed 3D walking surface.','records':[],'sourceLinework':[],'sources':[]}
    for sheet in ['9-SW-23A','9-SW-23B']:
        archive=HERE/'hydro-sources'/(sheet+'.zip');entry=sheet+'/Layers/Transportation/CartoPedLine.gml'
        with zipfile.ZipFile(archive) as z:raw=z.read(entry)
        root=ET.fromstring(raw);features=[]
        for member in root:
            if not member.tag.endswith('featureMember'):continue
            feature=list(member)[0];tags={e.tag.split('}')[-1]:e.text for e in list(feature) if len(e)==0}
            if tags.get('PEDESTRIANTYPE')!='FBR':continue
            parts=[];zs=[]
            for node in feature.iter():
                if node.tag.endswith('posList'):
                    v=list(map(float,node.text.split()));assert len(v)%3==0
                    parts.append([(v[i+1]-834500,816500-v[i]) for i in range(0,len(v),3)]);zs.extend(v[2::3])
            # Treat distinct source posLists as segments; no invented links between parts.
            for part in parts:
                if len(part)>=2:features.append({'id':tags['CARTOPEDESTRIANLINEID'],'line':LineString(part),'tags':tags,'sourceZ':sorted(set(zs))})
        source={'sheet':sheet,'sourceArchive':str(archive.relative_to(ROOT)),'sourceEntry':entry,'entrySha256':hashlib.sha256(raw).hexdigest(),'sourceArchiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'sourceFeatureSegments':len(features)}
        result['sources'].append(source)
        result['sourceLinework'].extend({'id':'landsd-line/'+sheet+'/FBR/'+f['id']+'/'+str(i),'featureId':f['id'],'path':list(map(list,f['line'].coords)),'attributes':f['tags'],'sourceZValues':f['sourceZ'],'heightHKPD':None,'walkable':False,'sourceEntry':entry} for i,f in enumerate(features))
        if not features:continue
        union=unary_union([f['line'] for f in features]);polygons=sorted(polygonize(union),key=lambda p:(p.centroid.x,p.centroid.y))
        for poly in polygons:
            assert poly.is_valid and poly.boundary.difference(union.buffer(1e-7)).length<1e-6
            used=[f for f in features if f['line'].intersection(poly.boundary.buffer(1e-7)).length>1e-5]
            ids=sorted(set(f['id'] for f in used));key=hashlib.sha256((' '.join(ids)+' '+poly.wkt).encode()).hexdigest()[:16]
            result['records'].append({'id':'landsd-plan/'+sheet+'/FBR/'+key,'name':'Yim Tin Bridge mapped plan surface','kind':'footbridge-plan','rings':[list(map(list,poly.exterior.coords))]+[list(map(list,r.coords)) for r in poly.interiors],'area':poly.area,'source':source['sourceArchive'],'sourceEntry':entry,'sourceFeatureIds':ids,'sourceFeatureAttributes':[f['tags'] for f in used],'sourceZValues':sorted(set(z for f in used for z in f['sourceZ'])),'heightHKPD':None,'walkable':False,'publicAccessSource':'https://www.info.gov.hk/gia/general/202605/03/P2026050300320.htm','nearbyMappedBridgeIds':['way/1202242137','way/1214278675'],'geometryPolicy':'Polygonised actual closed FBR linework with exact intersections; no snapping, gap closing or invented vertices away from source lines. Public bridge identity does not provide missing deck elevation.'})
    result['counts']={'closedPlanSurfaces':len(result['records']),'area':sum(r['area'] for r in result['records']),'sourceLineSegments':len(result['sourceLinework'])}
    result['geometryCaution']='Feature1910678330 contains separate curve members with a90.141m gap. Naive concatenation fabricates3closed outlines; preserving each source posList separately yields0closed polygons. No such polygons are published.'
    (HERE/'infrastructure-plan-linework.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result['counts']))
    return result
if __name__=='__main__':build()
