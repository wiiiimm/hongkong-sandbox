"""Exact packed attributes vs saved JSON, only NORMAL scalar ±0 transport."""
import gzip,hashlib,json,math,struct

def digest(b):return hashlib.sha256(b).hexdigest()
def verify(raw,capture):
 data=gzip.decompress(raw)
 assert len(data)>=28 and struct.unpack_from('<III',data)==(0x46546c67,2,len(data))
 n,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 doc=json.loads(data[20:20+n]);bn,bkind=struct.unpack_from('<II',data,20+n)
 assert bkind==0x004e4942 and 28+n+bn==len(data)
 binary=data[28+n:];assert len(binary)==bn
 assert len(doc['meshes'])==1 and len(doc['meshes'][0]['primitives'])==1
 primitive=doc['meshes'][0]['primitives'][0]
 assert primitive.get('mode',4)==4 and set(primitive['attributes'])=={'POSITION','NORMAL','COLOR_0'}
 def packed(index,width,allowed):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
  assert a['componentType']in allowed and a['type']==('VEC3'if width==3 else'SCALAR')
  assert a.get('normalized',False)is False and 'sparse'not in a and v.get('buffer',0)==0
  unit={5126:4,5123:2,5125:4}[a['componentType']]
  assert v.get('byteStride',unit*width)==unit*width
  count=a['count'];assert isinstance(count,int)and count>0
  offset=v.get('byteOffset',0)+a.get('byteOffset',0);size=count*width*unit
  assert 0<=offset and offset+size<=len(binary)
  return binary[offset:offset+size],count,a['componentType']
 assert len(capture['actualSourceMeshes'])==1
 mesh=capture['actualSourceMeshes'][0];sourceIndex,ic,it=packed(primitive['indices'],1,{5123,5125})
 assert mesh['indexArrayType']=={5123:'Uint16Array',5125:'Uint32Array'}[it]
 ids=list(struct.unpack('<'+('H'if it==5123 else'I')*ic,sourceIndex))
 assert ic%3==0 and ic//3==capture['completeOriginalFaceCount']==15140
 assert ids==mesh['completeIndex']==capture['completeOriginalIndex']
 result={'sourceSHA256':digest(raw),'originalIndexSHA256':digest(sourceIndex),'indexType':mesh['indexArrayType'],'completeIndexCount':ic,'completeIndexOrderExact':True,'attributes':{},'onlyNORMALZeroSignTransportPermitted':True}
 for sourceName,capturedName in [('POSITION','position'),('NORMAL','normal'),('COLOR_0','color')]:
  original,count,kind=packed(primitive['attributes'][sourceName],3,{5126});a=mesh['completeAttributes'][capturedName]
  assert a['arrayType']=='Float32Array'and a['itemSize']==3 and a['count']==count and a['normalized']is False
  values=a['values'];assert len(values)==count*3 and all(isinstance(v,(int,float))and not isinstance(v,bool)and math.isfinite(v)for v in values)
  assert all(0<=i<count for i in ids)
  packedJSON=struct.pack('<'+'f'*len(values),*values)
  assert all(float(v)==w for v,w in zip(values,struct.unpack('<'+'f'*len(values),packedJSON))),'JSON scalar not exact expanded Float32'
  obits=struct.unpack('<'+'I'*len(values),original);cbits=struct.unpack('<'+'I'*len(values),packedJSON)
  changes=[]
  for i,(o,c)in enumerate(zip(obits,cbits)):
   if o==c:continue
   assert capturedName=='normal'and(o^c)==0x80000000 and(o&0x7fffffff)==0 and(c&0x7fffffff)==0,'Nonzero or non-NORMAL bit difference'
   changes.append({'scalarIndex':i,'vertexIndex':i//3,'axis':i%3,'originalUint32Bits':o,'capturedJSONRepackedUint32Bits':c,'originalFloat32Hex':original[4*i:4*i+4].hex(),'capturedJSONFloat32Hex':packedJSON[4*i:4*i+4].hex(),'numericallyZeroBoth':True})
  def indexed_bytes(b):return b''.join(b[12*i:12*i+12]for i in ids)
  result['attributes'][capturedName]={'completeOriginalUnusedScalarCount':len(values),'originalFullFloat32SHA256':digest(original),'capturedJSONRepackedFullFloat32SHA256':digest(packedJSON),'originalIndexedFloat32TriangleSHA256':digest(indexed_bytes(original)),'capturedJSONRepackedIndexedFloat32TriangleSHA256':digest(indexed_bytes(packedJSON)),'completeOriginalFloat32BytesExactlyEqual':original==packedJSON,'zeroSignTransportRecords':changes,'nonzeroBitDifferences':0}
 return result
