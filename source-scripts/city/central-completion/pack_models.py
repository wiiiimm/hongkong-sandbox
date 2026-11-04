"""Stage individually loadable original models; reuse the proved source decoder/matcher.
Only identical complete vertex tuples are indexed. A gzip-wrapped standard GLB
retains source triangle order, float bits, normals, colours, materials and nodes.
No source vertices are quantised, simplified, shifted or removed.
"""
import argparse,collections,copy,gzip,hashlib,json,pathlib,struct,sys
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
DOC=ROOT/'docs/astra-city/central-completion'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from bake_model_geometry import decode
LANDMARKS={
 'landsd/89275:0':'HSBC Main Building', 'landsd/123884:0':'Bank of China Tower',
 'landsd/244915:0':'Two International Finance Centre', 'landsd/161250:0':'One International Finance Centre',
 'landsd/2941:0':'Jardine House','landsd/125345:0':'Cheung Kong Center',
 'landsd/257876:0':'Cheung Kong Center podium','landsd/179440:0':'Cheung Kong Center ancillary building',
 'landsd/3024:0':'City Hall ancillary building','landsd/186938:0':'City Hall',
 'landsd/315069:0':'Legislative Council Complex','landsd/275896:0':'Central Market',
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def pack(source_path):
 """Return standard GLB and bit-for-bit expanded-attribute verification stats."""
 original=json.loads(source_path.read_text());data=copy.deepcopy(original)
 assert not any(original.get(k) for k in ('animations','skins','images','textures','extensionsRequired','extensionsUsed')),'Validate new source features before packing'
 assert not any(m.get('weights') for m in original['meshes'])
 views=[];accessors=[];chunks=bytearray();stats=[]
 def append(array,component_type,kind,target,limits=False):
  while len(chunks)%4:chunks.append(0)
  offset=len(chunks);raw=array.tobytes(order='C');chunks.extend(raw)
  views.append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target})
  a={'bufferView':len(views)-1,'componentType':component_type,'count':len(array),'type':kind}
  if limits:a.update(min=array.min(axis=0).reshape(-1).tolist(),max=array.max(axis=0).reshape(-1).tolist())
  accessors.append(a);return len(accessors)-1
 for mesh,source_mesh in zip(data['meshes'],original['meshes']):
  for primitive,source_primitive in zip(mesh['primitives'],source_mesh['primitives']):
   assert source_primitive.get('mode',4)==4 and not source_primitive.get('targets')
   attrs=source_primitive['attributes'];arrays={k:decode(original,v,source_path.parent) for k,v in attrs.items()}
   assert 'POSITION' in arrays and all(np.isfinite(a).all() for a in arrays.values())
   count=len(arrays['POSITION']);assert all(len(a)==count for a in arrays.values())
   order=decode(original,source_primitive['indices'],source_path.parent).reshape(-1) if 'indices' in source_primitive else np.arange(count)
   assert len(order)%3==0 and int(order.max())<count
   # Byte tuples preserve signed zero and every original float bit. Including all
   # attributes prevents welding hard normals or different source vertex colours.
   keys=sorted(arrays);joined=np.concatenate([a.view(np.uint8).reshape(count,-1) for a in (arrays[k] for k in keys)],axis=1)
   tuples=np.ascontiguousarray(joined).view(np.dtype((np.void,joined.shape[1]))).reshape(-1)
   _,first,inverse=np.unique(tuples,return_index=True,return_inverse=True)
   # Keep first-use order for compression/locality, not NumPy's byte sorting.
   stable=np.argsort(first);remap=np.empty(len(stable),dtype=np.int64);remap[stable]=np.arange(len(stable));first=first[stable]
   new_order=remap[inverse[order]];attrs_out={};attribute_hashes={}
   for name in keys:
    src=original['accessors'][attrs[name]];unique=arrays[name][first]
    assert unique[new_order].tobytes()==arrays[name][order].tobytes(),name
    attrs_out[name]=append(unique,src['componentType'],src['type'],34962,name=='POSITION')
    # Accessor-level extras/name are optional metadata and remain attached.
    for key in ('name','extras'):
     if key in src:accessors[attrs_out[name]][key]=src[key]
    attribute_hashes[name]=sha(arrays[name][order].tobytes())
   index_type=5123 if len(first)<=65535 else 5125
   primitive['attributes']=attrs_out;primitive['indices']=append(new_order.astype('<u2' if index_type==5123 else '<u4').reshape(-1,1),index_type,'SCALAR',34963,True)
   stats.append({'sourceVertices':count,'indexedVertices':len(first),'triangles':len(order)//3,'expandedAttributeSha256':attribute_hashes})
 while len(chunks)%4:chunks.append(0)
 data['bufferViews']=views;data['accessors']=accessors;data['buffers']=[{'byteLength':len(chunks)}]
 # Scene/node/material metadata is copied exactly, including native coordinate
 # transforms. The viewer applies one separately documented city translation.
 for key in ('nodes','scenes','scene','materials'):assert data.get(key)==original.get(key)
 meta=json.dumps(data,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode();meta+=b' '*((-len(meta))%4)
 glb=struct.pack('<4sII',b'glTF',2,12+8+len(meta)+8+len(chunks))+struct.pack('<I4s',len(meta),b'JSON')+meta+struct.pack('<I4s',len(chunks),b'BIN\0')+chunks
 return glb,{'primitives':stats,'decodedGeometryBytes':sum(v['byteLength'] for v in views),'vertices':sum(s['indexedVertices'] for s in stats),'triangles':sum(s['triangles'] for s in stats)}

def matched():
 buildings=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))['buildings'];by_csuid=collections.defaultdict(list)
 for b in buildings:by_csuid[b['buildingCSUID']].append(b)
 groups=collections.defaultdict(list)
 for manifest_path in sorted((HERE/'staged').glob('*/manifest.json')):
  m=json.loads(manifest_path.read_text())
  for s in m['models']:
   if len(s['officialBuildingCSUIDs'])!=1:continue
   rows=by_csuid[s['officialBuildingCSUIDs'][0]]
   if len(rows)==1:groups[rows[0]['uid']].append((manifest_path.parent,m,s,rows[0]))
 for uid,entries in sorted(groups.items()):
  if len({e[2]['id'] for e in entries})!=1:continue
  yield uid,sorted(entries,key=lambda e:(e[1]['tileRevision'],e[1]['tile']),reverse=True)[0]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true',help='Pack all source-matched models; individual architectural review remains separate');args=parser.parse_args()
 out=HERE/'compact';records=[];asset_evidence=[]
 route_proof=DOC/'route-preflight.json'
 route_uids={b['uid'] for r in json.loads(route_proof.read_text())['routes'] for b in r['stagedBlockerBuildings']} if route_proof.exists() else set()
 for uid,(folder,m,s,b) in matched():
  selected=args.all or uid in LANDMARKS or uid in route_uids
  record={'uid':uid,'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'modelId':s['id'],'sourceTile':m['tile'],'sourceTileRevision':m['tileRevision'],'worldBounds':s['worldBounds'],'triangles':s['triangles'],'recordedBaseHeight':b.get('baseHeightHKPD'),'recordedTopHeight':b.get('topHeightHKPD'),'structureType':b.get('structureType'),'label':LANDMARKS.get(uid,b.get('name') or s['id']),'priority':'landmark' if uid in LANDMARKS else 'route-candidate' if uid in route_uids else 'unreviewed','asset':None,'placementReviewed':False}
  if selected:
   path=folder/s['url'];source=json.loads(path.read_text())
   for rel,digest in s['sourceHashes'].items():assert sha((folder/rel).read_bytes())==digest
   raw,stats=pack(path);compressed=gzip.compress(raw,mtime=0);dest=out/'models'/(s['id']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(compressed)
   record.update(asset=str(dest.relative_to(out)),encoding='gzip',bytes=len(compressed),glbBytes=len(raw),decodedGeometryBytes=stats['decodedGeometryBytes'],indexedVertices=stats['vertices'],sha256=sha(compressed))
   assert stats['triangles']==s['triangles']
   asset_evidence.append({'uid':uid,'modelId':s['id'],'sourceEntry':str(path.relative_to(ROOT)),'sourceHashes':s['sourceHashes'],'sourceCacheSha256':m['sourceCacheSha256'],'sourceOriginalDownload':m['sourceDownload'],'worldBounds':s['worldBounds'],'sourceMatches':s['officialMatches'],'compressedSha256':sha(compressed),'glbSha256':sha(raw),**stats})
   print(uid,record['label'],len(compressed),'compressed bytes',stats['triangles'],'triangles',flush=True)
  records.append(record)
 counts={'catalogueModels':len(records),'packedModels':sum(r['asset'] is not None for r in records),'routeCandidateModels':sum(r['asset'] is not None and r['priority']=='route-candidate' for r in records),'compressedBytes':sum(r.get('bytes',0) for r in records),'glbBytes':sum(r.get('glbBytes',0) for r in records),'decodedGeometryBytes':sum(r.get('decodedGeometryBytes',0) for r in records),'packedTriangles':sum(r['triangles'] for r in records if r['asset'])}
 catalogue={'schemaVersion':1,'kind':'staged-official-model-catalogue','area':'Central','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'coordinatePolicy':'Native original glTF nodes and float attributes, with only bit-identical full vertex tuples indexed. Apply root translation once; no terrain draping or height correction.','loadingPolicy':'Staging only. Retain the current building until its individual model has loaded and passed verification; unbuilt assets remain null.','counts':counts,'models':records}
 dump(out/'catalogue-all.json',catalogue)
 catalogue['models']=[r for r in records if r['asset']]
 catalogue['inventoryFile']='catalogue-all.json'
 dump(out/'catalogue.json',catalogue);dump(DOC/'compact-assets.json',{'counts':counts,'catalogueSha256':sha((out/'catalogue.json').read_bytes()),'assets':asset_evidence,'routeCandidateSelection':{'source':'route-preflight.json','sha256':sha(route_proof.read_bytes()) if route_proof.exists() else None,'requestedUids':sorted(route_uids),'missingSourceMatches':sorted(route_uids-{r['uid'] for r in records}),'note':'Additional exact source matches at diagnosed candidate-route contacts. Import does not approve passage or alter collision.'},'limits':['Source match is not full architectural or public-access review.','The source geometry and outline dataset have different revision dates. Recorded outline heights remain separate from model bounds.','Gzip wrapping needs native DecompressionStream before the existing GLTFLoader; no custom geometry decoder or new library.','Per-model budget/LOD and runtime source picking are not integrated yet.']});print(json.dumps(counts,indent=2))
if __name__=='__main__':main()
