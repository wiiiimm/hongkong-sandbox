"""Decode original iB1000 hydro geometry; no image tracing or invented depths."""
import gzip,hashlib,pathlib,xml.etree.ElementTree as ET
from shapely.geometry import Polygon,LineString,mapping
from shapely.ops import unary_union
from shapely import make_valid
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/tai-o-completion';G='{http://www.opengis.net/gml}';BOUNDS=[802700,812300,804650,813750]
def local(tag):return tag.split('}')[-1]
def positions(node):
 values=[float(x) for x in node.text.split()];assert len(values)%3==0
 return [[values[i+1]-834500,816500-values[i]] for i in range(0,len(values),3)]
def load():
 records=[]
 for path in sorted((HERE/'hydro-sources').glob('*.gml.gz')):
  raw=gzip.decompress(path.read_bytes());root=ET.fromstring(raw)
  for member in root.findall(G+'featureMember'):
   feature=list(member)[0];attrs={local(a.tag):a.text for a in feature if not list(a)};layer=local(feature.tag);geoms=[]
   if 'STATUS' in attrs and attrs['STATUS']!='E':continue
   for poly in feature.findall('.//'+G+'PolygonPatch'):
    exterior=poly.find(G+'exterior/.//'+G+'posList');interiors=poly.findall(G+'interior/.//'+G+'posList')
    if exterior is not None:geoms.append(make_valid(Polygon(positions(exterior),[positions(p) for p in interiors])))
   if not geoms:
    geoms=[LineString(positions(p)) for p in feature.findall('.//'+G+'posList') if len(p.text.split())>=6]
   if not geoms:continue
   geom=unary_union(geoms);record={'id':layer+'/'+str(attrs.get(layer.upper()+'ID',feature.get(G+'id'))),'sheet':path.name[:8],'layer':layer,'attributes':attrs,'sourceFile':str(path.relative_to(ROOT)),'sourceSha256':hashlib.sha256(raw).hexdigest(),'geometry':mapping(geom)};records.append((record,geom))
 return records
