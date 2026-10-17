"""Extract only Ngong Ping's exact indexed source component; preserve each triangle and attribute."""
import collections,copy,gzip,hashlib,json,struct
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
import importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BATCH='government-ngong-ping-peaks-473-20260918';UID='landsd/168823:0'
STAGE=HERE/'local/government-lantau-ngong-extract-20260921';ORIGINAL=HERE/'accepted/government-lantau-ngong-original-20260921';DOC=ROOT/'docs/astra-city/government-import/government-lantau-ngong-extract-20260921'
spec=importlib.util.spec_from_file_location('held',HERE/'lantau-final-held-review.py');held=importlib.util.module_from_spec(spec);spec.loader.exec_module(held)
def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def glb(gltf,binary):
 body=json.dumps(gltf,separators=(',',':')).encode();body+=b' '*(-len(body)%4);binary+=b'\0'*(-len(binary)%4)
 return b'glTF'+struct.pack('<II',2,12+8+len(body)+8+len(binary))+struct.pack('<II',len(body),0x4e4f534a)+body+struct.pack('<II',len(binary),0x004e4942)+binary
def source_mesh(gltf,binary):
 primitive=gltf['meshes'][0]['primitives'][0]
 def values(index):
  a=gltf['accessors'][index];view=gltf['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0)
  code={5123:'H',5125:'I',5126:'f'}[a['componentType']];width={'SCALAR':1,'VEC3':3}[a['type']]
  return struct.unpack_from('<'+code*(a['count']*width),binary,offset)
 positions=values(primitive['attributes']['POSITION']);local=[positions[i:i+3] for i in range(0,len(positions),3)]
 transform=gltf['nodes'][0]['matrix'];world=[(x+transform[12]-834500,z+transform[13],-y+transform[14]+816500) for x,y,z in local]
 return world,values(primitive['indices'])
def main():
 row=copy.deepcopy(held.source_row(BATCH,UID));entry=row['candidate']['entry'];source=ORIGINAL/entry['asset'];packed=source.read_bytes();assert sha(packed)==entry['sha256'];raw=gzip.decompress(packed)
 n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);bo=20+n;bn=struct.unpack_from('<I',raw,bo)[0];binary=raw[bo+8:bo+8+bn]
 v,ix=source_mesh(g,binary);target=Polygon(row['source']['building']['rings'][0]);other=Polygon(held.source_row(BATCH,'landsd/181268:0')['source']['building']['rings'][0])
 keys=[tuple(round(q,3) for q in point) for point in v];distinct={key:i for i,key in enumerate(dict.fromkeys(keys))};mapped=[distinct[key] for key in keys];parent=list(range(len(distinct)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i in range(0,len(ix),3):
  a,b,c=(mapped[ix[i+j]] for j in range(3));parent[find(b)]=find(a);parent[find(c)]=find(a)
 components=collections.defaultdict(list)
 for i in range(0,len(ix),3):components[find(mapped[ix[i]])].append(i)
 selected=[]
 for offsets in components.values():
  triangles=[Polygon([(v[ix[i+j]][0],v[ix[i+j]][2]) for j in range(3)]) for i in offsets]
  area=unary_union(triangles).intersection(target).area
  if area>.01:selected.append(offsets)
 assert len(components)==73 and len(selected)==1 and len(selected[0])==16
 offsets=selected[0];projected=unary_union([Polygon([(v[ix[i+j]][0],v[ix[i+j]][2]) for j in range(3)]) for i in offsets])
 assert projected.intersection(target).area/target.area>.997 and projected.intersection(other).area==0
 original_indices=[ix[i+j] for i in offsets for j in range(3)];unique=list(dict.fromkeys(original_indices));remap={old:new for new,old in enumerate(unique)};new_indices=[remap[i] for i in original_indices]
 primitive=g['meshes'][0]['primitives'][0];assert primitive['indices']==3 and set(primitive['attributes'])=={'COLOR_0','NORMAL','POSITION'}
 arrays=[];views=[];accessors=copy.deepcopy(g['accessors'])
 for ai in range(3):
  descriptor=accessors[ai];assert descriptor['componentType']==5126 and descriptor['type']=='VEC3'
  view=g['bufferViews'][descriptor['bufferView']];assert not descriptor.get('byteOffset') and not view.get('byteStride')
  values=[struct.unpack_from('<3f',binary,view['byteOffset']+old*12) for old in unique]
  arrays.append(b''.join(struct.pack('<3f',*value) for value in values));descriptor['count']=len(unique)
  if ai==2:
   descriptor['min']=[min(x[k] for x in values) for k in range(3)];descriptor['max']=[max(x[k] for x in values) for k in range(3)]
 index_bytes=struct.pack('<'+'H'*len(new_indices),*new_indices);arrays.append(index_bytes)
 accessors[3].update(count=len(new_indices),min=[0],max=[len(unique)-1]);g['accessors']=accessors
 offset=0
 for i,data in enumerate(arrays):
  views.append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':34963 if i==3 else 34962});offset+=len(data)
 g['bufferViews']=views;g['buffers'][0]['byteLength']=offset
 output=glb(g,b''.join(arrays));encoded=gzip.compress(output,mtime=0);digest=sha(encoded);asset='assets/'+digest+'.glb.gz';path=STAGE/asset;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded)
 # The subset uses original positions, normals, colours, winding, transform and material.
 source_bounds=[[min(v[i][axis] for i in unique) for axis in range(3)],[max(v[i][axis] for i in unique) for axis in range(3)]]
 entry.update(asset=asset,sha256=digest,bytes=len(encoded),glbBytes=len(output),indexedVertices=len(unique),triangles=len(new_indices)//3,worldBounds=source_bounds,decodedGeometryBytes=len(unique)*36+len(new_indices)*2,
  sourceSubsetOf=sha(packed),sourceSubsetTriangles=16,sourceComponentsOmitted=72,priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=False,proceduralWindows=False,retainsBasicForm=True,
  placementReview='Exact 16 original government triangles for this CSUID, selected by welded source connectivity and 99.79% target footprint coverage. 72 unrelated components omitted; positions, normals, colours, transform and material unchanged. No overlap with installed station footprint.')
 row['candidate']['path']=str(path);form=row['source']['building'];save(STAGE/'source-forms.json',[form]);template=held.read(ROOT/'3d-viewer/city/data/official-models/government-discovery-bay-compute-20260921/catalogue.json');template.update(area='Ngong Ping exact source component',counts={'packedModels':1},models=[entry]);save(STAGE/'catalogue.json',template);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'selection.json.gz').write_bytes(gzip.compress((json.dumps({'batch':'government-lantau-ngong-extract-20260921','rows':[row],'manifestSHA256':sha((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'aiCalls':0})+'\n').encode(),mtime=0))
 save(DOC/'source-forms.json',{UID:row['source']});save(DOC/'terrain-candidates.json',[])
 save(DOC/'extraction-proof.json',{'uid':UID,'originalSHA256':sha(packed),'extractedSHA256':digest,'originalTriangles':len(ix)//3,'retainedTriangles':16,'omittedComponents':72,'sourceAttributeBytesPreserved':True,'sourceTransformAndMaterialPreserved':True,'targetCoverage':projected.intersection(target).area/target.area,'installedStationOverlapM2':0,'aiCalls':0,'aiModellingCalls':0,'geometryGenerated':False})
 print(json.dumps({'uid':UID,'asset':asset,'triangles':16,'vertices':len(unique),'worldBounds':source_bounds}))
if __name__=='__main__':main()
