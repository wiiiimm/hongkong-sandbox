"""Keep source lines immutable; tie a labelled estimated public connector to the mesh opening."""
import gzip,hashlib,json,pathlib,xml.etree.ElementTree as ET,zipfile
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def build():
 route=json.loads((ROOT/'docs/astra-city/tai-o-completion/route.json').read_text())
 source=HERE/'infrastructure-models.json.gz';m=next(m for m in json.loads(gzip.decompress(source.read_bytes()))['models'] if m['id'].endswith('I038171281003063C1'))
 a=m['modelGeometry']['position'];floor=unary_union([Polygon([(a[j],a[j+2]) for j in range(i*9,i*9+9,3)]) for i in m['walkTriangleIndices']])
 start=route['centreline'][20];assert abs(start[0]+30656.920061)<.01
 approach=[start,[-30657.4,3687.0],[-30659.5,3685.8],[-30660.0,3684.75]]
 entry=LineString(approach[-2:]).intersection(floor.boundary);assert entry.geom_type=='Point'
 # The mesh opening and the source OSM approach are authoritative anchors.
 # These intermediate clearance positions are explicitly estimated, not source vertices.
 line=[*approach[:-1],list(entry.coords)[0],approach[-1],[-30662.0,3683.3],route['centreline'][22]]
 archive=HERE/'hydro-sources/9-SW-23B.zip';entry_path='9-SW-23B/Layers/Transportation/CartoPedLine.gml'
 with zipfile.ZipFile(archive) as z:raw=z.read(entry_path)
 refs=[]
 for member in ET.fromstring(raw):
  if not member.tag.endswith('featureMember'):continue
  f=list(member)[0];tags={e.tag.split('}')[-1]:e.text for e in list(f) if len(e)==0}
  if tags.get('CARTOPEDESTRIANLINEID') not in ['1109131981','1109131982','1109097753','1810305569','1109083560']:continue
  paths=[]
  for n in f.iter():
   if n.tag.endswith('posList'):
    v=list(map(float,n.text.split()));paths.append([[v[i+1]-834500,816500-v[i]] for i in range(0,len(v),3)])
  refs.append({'attributes':tags,'paths':paths,'sourceHeightPolicy':'The source Z=0 is a plan placeholder, not a surveyed deck height.'})
 original=LineString(route['centreline'][20:23])
 output={'schemaVersion':1,'id':'tai-chung-public-entry','replacesSourceIndices':[20,22],'centreline':line,'approach':approach,'sourceDeckEntry':list(entry.coords)[0],'sourceDeckHeightHKPD':4.058000087738037,'sourceBridgeId':m['id'],'sourceStreetWay':48126232,'publicAccessSource':m['publicAccessSource'],'maximumDistanceFromOriginalSegmentMetres':max(Point(p).distance(original) for p in line),'estimatedHorizontalAlignment':True,'alignmentBasis':'A visible illustrative public access connector from the retained public street node around the southeast opening in the exact bridge mesh. Intermediate positions are clearance estimates; original OSM nodes, source bridge railings, footprint geometry and recorded heights remain unchanged.','sourceDiscrepancy':'The original OSM shortcut crosses a solid source-mesh side railing. Nearby iB1000 plan step/path lines identify public access at the northeast end, but the 3D mesh retains railing across that exact plan strip. The usable southeast mesh opening is used here; this is not claimed as an exact reconstruction of the mapped stairs.','sources':[{'path':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceEntryHashes':m['modelGeometry']['sourceHashes']},{'path':str(archive.relative_to(ROOT)),'entry':entry_path,'entrySha256':hashlib.sha256(raw).hexdigest(),'features':refs}], 'limits':['Exact horizontal stair alignment, number of risers, width and approach elevations are unavailable; all added approach geometry is explicitly illustrative.','The connector is separate from the bounded 0.75 m adjustments to ordinary public-street centrelines. It does not grant access to private residential decks.']}
 (HERE/'route-entry.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:output[k] for k in ['sourceDeckEntry','maximumDistanceFromOriginalSegmentMetres']}))
 return output
if __name__=='__main__':build()
