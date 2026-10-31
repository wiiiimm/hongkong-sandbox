"""DRAFT raw original TEXCOORD/index/material→all171 source face/body attribution.
No geometry/texture edit, pixel warp, source role, pose or acceptance.
"""
from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,read,save,digest,connect
from science_museum_open_sided_original_gltf_identity_comparison_v3_20261011 import decode_original
B=ROOT/'docs/astra-city/government-import';A=B/'government-xl-science-museum-open-sided-original-gltf-members-acquisition-v1-20261011';C=B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011';T=B/'government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';DOC=B/'government-xl-science-museum-original-raw-uv-body-atlas-registration-v1-20261011';MODEL='B363151801501063A0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 for folder in [A,C,T]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 a=read(A/'acquisition.json');p=A/'original-members/BUILDING'/MODEL/(MODEL+'.gltf');g=json.loads(p.read_bytes());tri,positions,account=decode_original(p);c=read(C/'diagnostic.json.gz');assert tri.shape==(171,3,3)and digest(tri.astype('<f8').tobytes())==c['completeAuthoredMatrixWorldTrianglesSHA256'];t=read(T/'diagnostic.json.gz');labels={f:b['body']for b in t['originalOpenBodyDetails']for f in b['originalFaces']};zeros=t['originalOpen171FaceCensus']['exactNonrenderingOriginalFaces'];assert set(labels)|set(zeros)==set(range(171));buffers=[(p.parent/v['uri']).read_bytes()for v in g['buffers']]
 def access(i):
  a=g['accessors'][i];assert not a.get('sparse')and not a.get('normalized');v=g['bufferViews'][a['bufferView']];dtype=np.dtype({5126:'<f4',5121:'u1',5123:'<u2',5125:'<u4'}[a['componentType']]);width={'VEC2':2,'SCALAR':1}[a['type']];stride=v.get('byteStride',width*dtype.itemsize);off=v.get('byteOffset',0)+a.get('byteOffset',0);assert a['count']>0 and stride>=width*dtype.itemsize and off>=v.get('byteOffset',0)and off+(a['count']-1)*stride+width*dtype.itemsize<=v.get('byteOffset',0)+v['byteLength']<=len(buffers[v['buffer']]);return np.ndarray((a['count'],width),dtype=dtype,buffer=buffers[v['buffer']],offset=off,strides=(stride,dtype.itemsize)).copy()
 rows=[];face=0;bindings=[]
 for part in account['sourcePrimitives']:
  prim=g['meshes'][part['originalMesh']]['primitives'][part['primitive']];assert prim['mode']==4;uv=access(prim['attributes']['TEXCOORD_0']);ids=access(prim['indices']).reshape(-1);assert uv.dtype==np.dtype('<f4')and np.isfinite(uv).all()and len(uv)==part['allOriginalPositionVertices']and len(ids)%3==0 and (ids<len(uv)).all();mat=g['materials'][prim['material']];texture=mat['pbrMetallicRoughness']['baseColorTexture'];assert texture.get('texCoord',0)==0 and not texture.get('extensions');tex=g['textures'][texture['index']];image=g['images'][tex['source']];assert set(image)=={'uri'};img=p.parent/image['uri'];assert any(ref(img)==m['file']for m in a['completeOriginalMembers']);binding=dict(globalFaceRange=part['globalFaceRange'],materialIndex=prim['material'],originalMaterial=mat,textureIndex=texture['index'],originalTexture=tex,imageIndex=tex['source'],originalImage=ref(img),originalSampler=g['samplers'][tex['sampler']],uvAccessorIndex=prim['attributes']['TEXCOORD_0'],originalUVAccessor=g['accessors'][prim['attributes']['TEXCOORD_0']],originalUVBufferView=g['bufferViews'][g['accessors'][prim['attributes']['TEXCOORD_0']]['bufferView']],indexAccessorIndex=prim['indices'],originalIndexAccessor=g['accessors'][prim['indices']]);bindings.append(binding);assert face==part['globalFaceRange'][0]
  for ix in ids.reshape(-1,3):
   rows.append(dict(originalFace=face,nonzeroEdgeBody=labels.get(face),exactZeroAreaOriginalFace=face in zeros,originalVertexIndices=ix.tolist(),rawOriginalUVTriples=uv[ix].astype(float).tolist(),materialIndex=prim['material'],textureIndex=texture['index'],imageIndex=tex['source'],photographicRoleAccepted=False));face+=1
  assert face==part['globalFaceRange'][1]
 assert face==171 and len(rows)==171;DOC.mkdir();colours=['#e87722','#176fc1','#9f3ba7','#218349','#b12230'];fig,axes=plt.subplots(1,2,figsize=(12,12))
 for material,ax in enumerate(axes):
  for body in range(5):
   faces=[r['rawOriginalUVTriples']for r in rows if r['materialIndex']==material and r['nonzeroEdgeBody']==body];ax.add_collection(PolyCollection(faces,facecolor='none',edgecolor=colours[body],linewidth=.6,label='Body '+str(body)))
  ax.set_xlim(0,1);ax.set_ylim(1,0);ax.set_aspect('equal');ax.set_xlabel('Raw original U');ax.set_ylabel('Raw original V (down on this chart)');ax.set_title('Unchanged UV triangles / material '+str(material));ax.legend();ax.grid(alpha=.2)
 fig.suptitle('171 complete source faces; original image files remain separate/unmodified\nRaw UV/body attribution; no atlas pixel warp, photo-function/attachment/root approval');fig.tight_layout();fig.savefig(DOC/'raw-original-uv-body-context.png',dpi=160);plt.close(fig)
 refs=[ref(Path(__file__)),ref(p),ref(A/'acquisition.json'),ref(A/'result.json'),ref(C/'diagnostic.json.gz'),ref(C/'result.json'),ref(T/'diagnostic.json.gz'),ref(T/'result.json')]+[m['file']for m in a['completeOriginalMembers']];save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,currentAcceptance=False,identityAccepted=False,installationApproved=False,sourceGeometryChanges=0,textureBytesChanged=False,originalSourceCoordinateFrameRecheckedByteIdentical=True,complete171SourceFaceUVBodyRows=rows,completeMaterialImageAccessorBindings=bindings,allFiveBodyObligationsPreserved=True,exactZeroFacesPreserved=zeros,imagePixelWarpPerformed=False,photographicFeatureRoleAccepted=False,qualification='Raw UV/index/material bindings only. Original JPEG visibly includes bilingual Museum frontage, covered entrance and steel members, but atlas photographic pixels do not prove any particular original triangle is a load-bearing solid or any53surface crossing is valid. All5body/3zero-face/native/current/ground/foreign/support and primary-plan-registration obligations remain. UV chart uses raw V downward without editing the atlas; actual production GLTF sampling/texture orientation must be independently verified before feature-level photographic assignment.',evidenceRefs=refs))
if __name__=='__main__':main()
