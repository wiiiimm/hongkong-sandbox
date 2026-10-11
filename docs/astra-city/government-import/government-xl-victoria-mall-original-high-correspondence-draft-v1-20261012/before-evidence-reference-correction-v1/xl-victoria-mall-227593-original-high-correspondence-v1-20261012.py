"""DRAFT ONLY: original source hierarchy/exact correspondence and saved contact loci."""
import gzip,importlib.util,json,struct,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-victoria-mall-complete-source-lower-joins-context-v1-20261012'
JOB='3d46c227dda1224d4987e59a8d44ae7e494959b4efeedd4eccaff31df0340700'
RESULT_SHA='f28431be8db96b7de9a396d2abf059096ead3e8d0bfb2efef68870f2c3a93f57'
CONTEXT_SHA='cba1d2e5a005384335c81544858ee906ec4195852a3d4486eec23f5bf48e757f'
MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
P,T,T2,T1='landsd/227593:0','landsd/251609:0','landsd/251614:0','landsd/251615:0'
BATCH='government-xl-victoria-mall-original-high-correspondence-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
METHOD=BASE/'government-xl-victoria-mall-original-high-correspondence-draft-v1-20261012/METHOD.md'
PRIMARY=BASE/'government-xl-victoria-mall-bounded-primary-project-packet-v1-20261012'
def preflight():
 assert not DOC.exists();assert digest((PRIOR/'result.json').read_bytes())==RESULT_SHA and digest((PRIOR/'context.json.gz').read_bytes())==CONTEXT_SHA
 r=read(PRIOR/'result.json');o=read(PRIOR/'context.json.gz');assert r['jobId']==JOB and len(r['evidenceRefs'])==431
 assert len(o['all1276ClassificationsVerbatim'])==1276 and sum(x['properTriangleInteriorCrossing']for x in o['all1276ClassificationsVerbatim'])==1136 and len(o['all9RawFailureContextsVerbatim'])==9
 assert o['currentAcceptance']is False and o['noArchitecturalInterpretationAccepted']and o['noRuntimeOrApprovalTransfer']
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 cat=read(ROOT/'3d-viewer/city/data/official-models/support-review-20260909/catalogue.json');assert [x for x in cat['models']if x['uid']==T]==[o['completeInstalledTower3EntryVerbatim']]
 refs=[Path(__file__),METHOD,PRIOR/'result.json',PRIOR/'context.json.gz',HERE/'run.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'popcorn_original_ancillary_identity_20261009.py']+[HERE.parent/'shared-modelling'/x for x in ['db.py','jobs.py','reservations.py','reservation_runner.py']]
 for pin in r['evidenceRefs']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 packet=read(PRIMARY/'packet-file-bindings.json');refs.append(PRIMARY/'packet-file-bindings.json')
 for pin in packet['bindings']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 validate_contact_schema(o)
 for uid,a in o['sourceActorsVerbatim'].items():
  raw=(ROOT/a['sourceTupleVerbatim']['assetPath']).read_bytes();h=source_hierarchy(raw,a['sourceTupleVerbatim']['faces']);verify_hierarchy_order(raw,h,np.asarray(o['all4CompleteOriginalWorldTriangles'][uid],dtype='<f8'))
 return r,o,refs,{str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
def source_hierarchy(raw,total_faces):
 data=gzip.decompress(raw);magic,version,total=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and total==len(data)
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a;doc=json.loads(data[20:20+size]);rows=[];cursor=0
 def visit(i,anc):
  nonlocal cursor
  assert i not in anc;node=doc['nodes'][i]
  if 'mesh'in node:
   mesh=doc['meshes'][node['mesh']]
   for n,p in enumerate(mesh['primitives']):
    assert p.get('mode',4)==4 and 'indices'in p;count=doc['accessors'][p['indices']]['count'];assert count%3==0
    rows.append(dict(nodeIndex=i,ancestorNodeIndices=anc,nodeVerbatim=node,meshIndex=node['mesh'],meshName=mesh.get('name'),primitiveOrdinal=n,primitiveVerbatim=p,firstOriginalFace=cursor,exclusiveEndOriginalFace=cursor+count//3));cursor+=count//3
  for c in node.get('children',[]):visit(c,anc+[i])
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,[])
 assert cursor==total_faces
 return dict(completeProviderGLTFDocument=doc,completeOriginalFaceRanges=rows,completeFaceCount=cursor,namesAreNotOwnershipOrArchitecturalCertification=True)
def primitive_reference(o,uid,face,dimension):
 a=o['sourceActorsVerbatim'][uid];top=a['completeOriginalTopology'];assert isinstance(face,int)and 0<=face<a['sourceTupleVerbatim']['faces']
 component=a['completeFaceToComponent'].get(str(face))
 if face in top['exactNonrenderingOriginalFaces']:
  assert component is None and dimension in (0,1)
  return dict(uid=uid,sourceFace=face,kind='exact-zero-area-original-primitive-uncredited',primitiveDimension=dimension,component=None,rootOrBridgeCredit=False)
 assert isinstance(component,int)and 0<=component<len(top['sharedEdgeConnectedComponents'])and face in top['sharedEdgeConnectedComponents'][component]and dimension==2
 return dict(uid=uid,sourceFace=face,kind='positive-area-original-component-member',primitiveDimension=2,component=component,rootOrBridgeCredit=False)
def validate_contact_schema(o):
 rows=[]
 for i,row in enumerate(o['all1276ClassificationsVerbatim']):
  c=row['contactVerbatim'];assert isinstance(c['exactPoints'],list)and c['exactPoints']
  for p in c['exactPoints']:
   assert len(p)==3 and all(isinstance(x,str)for x in p);q=[Fraction(x)for x in p];assert len(q)==3
  ra=primitive_reference(o,P,c['sourceFaceA'],c['sourcePrimitiveDimensionA']);rb=primitive_reference(o,T,c['sourceFaceB'],c['sourcePrimitiveDimensionB'])
  if ra['component']is None or rb['component']is None:
   assert not row['properTriangleInteriorCrossing']and row['structuralSupportCredit']is False
  rows.append(dict(recordIndex=i,sourcePrimitiveA=ra,sourcePrimitiveB=rb))
 assert len(rows)==1276 and sum(x['sourcePrimitiveA']['component']is None or x['sourcePrimitiveB']['component']is None for x in rows)==16
 return rows
def verify_hierarchy_order(raw,h,world):
 data=gzip.decompress(raw);size,_=struct.unpack_from('<II',data,12);binary=data[28+size:];doc=h['completeProviderGLTFDocument']
 def accessor(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];assert not a.get('normalized')and not a.get('sparse')and v['buffer']==0
  width={'VEC3':3,'SCALAR':1}[a['type']];dtype=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']]);stride=v.get('byteStride',width*dtype.itemsize);assert stride>=width*dtype.itemsize
  return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,dtype.itemsize))
 cursor=0
 for r in h['completeOriginalFaceRanges']:
  assert r['firstOriginalFace']==cursor;transform=np.eye(4)
  for node_index in r['ancestorNodeIndices']+[r['nodeIndex']]:
   n=doc['nodes'][node_index];assert not any(k in n for k in ['translation','rotation','scale']);transform=transform@np.asarray(n.get('matrix',np.eye(4).reshape(-1,order='F').tolist()),float).reshape(4,4,order='F')
  p=r['primitiveVerbatim'];v=accessor(p['attributes']['POSITION']).astype(float);ids=accessor(p['indices']).reshape(-1);assert len(ids)%3==0 and (ids>=0).all()and (ids<len(v)).all()
  actual=((np.c_[v,np.ones(len(v))]@transform.T)[:,:3]+np.array([-834500,0,816500]))[ids].reshape(-1,3,3);expected=world[r['firstOriginalFace']:r['exclusiveEndOriginalFace']]
  assert actual.shape==expected.shape and np.array_equal(actual,expected)and actual.astype('<f8').tobytes()==expected.astype('<f8').tobytes()
  cursor=r['exclusiveEndOriginalFace']
 assert cursor==len(world)==h['completeFaceCount']
 return dict(completeOrderedFaceCount=cursor,everyPrimitiveOrderedWorldSliceByteEqual=True,completeWorldSHA256=digest(world.tobytes()))
def vertex_key(v):return struct.pack('<3d',*map(float,v))
def triangle_key(tri):return tuple(sorted(vertex_key(v)for v in tri))
def exact_triangle_account(a,b,azeros,bzeros):
 index=defaultdict(list)
 for j,tri in enumerate(b):index[triangle_key(tri)].append(j)
 rows=[]
 for i,tri in enumerate(a):
  ka=[vertex_key(v)for v in tri]
  for j in index.get(triangle_key(tri),[]):
   kb=[vertex_key(v)for v in b[j]];same=any(ka==kb[n:]+kb[:n]for n in range(3));rev=list(reversed(kb));opposite=any(ka==rev[n:]+rev[:n]for n in range(3))
   rows.append(dict(sourceFaceA=i,sourceFaceB=j,sameCyclicWinding=same,reversedCyclicWinding=opposite,zeroPrimitiveA=i in azeros,zeroPrimitiveB=j in bzeros,noDuplicateRemovalOrSupportCredit=True))
 return rows
def finish(fig,name,scope):
 fig.suptitle('PROVIDER ORIGINAL / SAVED EXACT CONTACT DIAGRAM — no registration, role or approval',fontsize=11);fig.tight_layout(rect=[0,0,1,.95]);p=DOC/name;fig.savefig(p,dpi=150);plt.close(fig)
 with Image.open(p)as im:assert im.size==(2400,1800)
 return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),width=2400,height=1800,scope=scope)
def axes_labels(ax,axes):
 ax.set_xlabel('source '+'XYZ'[axes[0]]+' m');ax.set_ylabel('source '+'XYZ'[axes[1]]+' m');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7)
def owned(state):
 r,o,refs,pins=state;lease=read(LEASE);assert lease['resources']==['building:'+u for u in sorted([P,T,T2,T1])]and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',r)
 w={u:np.asarray(x,dtype='<f8')for u,x in o['all4CompleteOriginalWorldTriangles'].items()};hierarchy={}
 for u,a in o['sourceActorsVerbatim'].items():
  s=a['sourceTupleVerbatim'];assert w[u].shape==(s['faces'],3,3)and digest(w[u].tobytes())==a['completeWorldSHA256'];raw=(ROOT/s['assetPath']).read_bytes();assert digest(raw)==s['sourceSHA256'];hierarchy[u]=source_hierarchy(raw,s['faces']);hierarchy[u]['orderedWorldVerification']=verify_hierarchy_order(raw,hierarchy[u],w[u])
 zeros={u:set(a['completeOriginalTopology']['exactNonrenderingOriginalFaces'])for u,a in o['sourceActorsVerbatim'].items()};exact=exact_triangle_account(w[P],w[T],zeros[P],zeros[T]);vi=defaultdict(list)
 for f,tri in enumerate(w[T]):
  for c,v in enumerate(tri):vi[vertex_key(v)].append([f,c])
 vertices=[dict(sourceFaceA=f,originalCornerA=c,coordinate=v.tolist(),allExactTower3FaceCornerIncidences=vi[vertex_key(v)])for f,tri in enumerate(w[P])for c,v in enumerate(tri)if vertex_key(v)in vi]
 primitive_refs=validate_contact_schema(o);records=o['all1276ClassificationsVerbatim'];loc=[]
 for i,row in enumerate(records):
  contact=row['contactVerbatim'];pts=contact['exactPoints'];assert pts
  coord=np.asarray([[float(Fraction(x))for x in p]for p in pts]);loc.append(dict(recordIndex=i,sourcePrimitiveReferences=primitive_refs[i],contactAndClassificationVerbatim=row,displayOnlyFloatingCoordinates=coord.tolist(),sourceFacetACoordinates=w[P][contact['sourceFaceA']].tolist(),sourceFacetBCoordinates=w[T][contact['sourceFaceB']].tolist(),componentA=o['sourceActorsVerbatim'][P]['completeFaceToComponent'].get(str(contact['sourceFaceA'])),componentB=o['sourceActorsVerbatim'][T]['completeFaceToComponent'].get(str(contact['sourceFaceB'])),exactContactYExtremaRational=[str(min(Fraction(p[1])for p in pts)),str(max(Fraction(p[1])for p in pts))]))
 DOC.mkdir();exports=[];fig=plt.figure(figsize=(16,12))
 for n,axes in enumerate([(0,1),(0,2),(2,1)],1):
  ax=fig.add_subplot(1,3,n)
  for uid,col in [(P,'#95a9b8'),(T,'#356ac3')]:ax.add_collection(PolyCollection(w[uid][:,:,axes],facecolors=col,edgecolors=col,alpha=.035,linewidths=.1))
  for rec in loc:
   v=np.asarray(rec['displayOnlyFloatingCoordinates']);ax.plot(v[:,axes[0]],v[:,axes[1]],color='#c0008c'if rec['contactAndClassificationVerbatim']['properTriangleInteriorCrossing']else'#008c65',linewidth=.5,marker='.',markersize=1)
  ax.autoscale_view();axes_labels(ax,axes);ax.set_title('Saved1276 actual contact loci; magenta1136 proper\nSource facets pale; no new intersection computation',fontsize=9)
 exports.append(finish(fig,'complete-source-facets-and-saved1276-contact-loci-2400x1800.png','Complete P/T3 facets; all exact saved loci converted to floats only for display; no role or geometry disposition.'))
 fig=plt.figure(figsize=(16,12))
 for i,family in enumerate(o['complete9FamiliesVerbatim'][1:]):
  ax=fig.add_subplot(3,3,i+1);facets=[];labels=[]
  for uid,component in family:
   ids=o['sourceActorsVerbatim'][uid]['completeOriginalTopology']['sharedEdgeConnectedComponents'][component];facets.extend(w[uid][ids]);labels.extend((uid,component,f)for f in ids)
  q=np.asarray(facets);sp=np.ptp(q.reshape(-1,3),axis=0);choices=[(0,1),(0,2),(2,1)];axes=max(choices,key=lambda a:sp[a[0]]*sp[a[1]])
  ax.add_collection(PolyCollection(q[:,:,axes],facecolors='#4383ac',edgecolors='#2d5978',alpha=.3,linewidths=.8));ax.autoscale_view();axes_labels(ax,axes)
  for tri,label in zip(q,labels):
   v=tri.mean(0);ax.text(v[axes[0]],v[axes[1]],str(label[2]),fontsize=7)
  ax.set_title('Family'+str(i+1)+' '+str(family)+'\ncomplete original vertices, view aspect auto',fontsize=7);ax.set_aspect('auto')
 exports.append(finish(fig,'eight-isolated-source-families-coordinate-labelled-2400x1800.png','All8 isolated complete source families, coordinate-labelled2D; display aspect auto does not change source.'))
 component_coverage=[]
 for uid,a in o['sourceActorsVerbatim'].items():
  for i,ids in enumerate(a['completeOriginalTopology']['sharedEdgeConnectedComponents']):
   assert a['componentFullBounds'][i]['component']==i and a['componentFullBounds'][i]['completeOriginalFaceIDs']==ids
   contact=[x['recordIndex']for x in loc if (uid==P and x['componentA']==i)or(uid==T and x['componentB']==i)];component_coverage.append(dict(uid=uid,component=i,completeFaceIDs=ids,completeCoordinates=w[uid][ids].tolist(),savedFullBoundsVerbatim=a['componentFullBounds'][i],allSavedCrossRecordIndices=contact,sourceHierarchyFaceRangesVerbatim=hierarchy[uid]['completeOriginalFaceRanges']))
 result=dict(uids=[P,T,T2,T1],sourceActorsVerbatim=o['sourceActorsVerbatim'],completeProviderHierarchyByActor=hierarchy,allActorComponentsComplete=component_coverage,completeOriginalTriangleCorrespondences=exact,allExactMallVertexCornerCorrespondences=vertices,all1276SavedLociAndSourceFacets=loc,all1136ProperRecordsPreserved=True,all9OldFailuresVerbatim=o['all9RawFailureContextsVerbatim'],allZeroPrimitiveIDsVerbatim=o['allZeroPrimitiveOriginalIDsByActor'],all4WorldsVerbatim=o['all4CompleteOriginalWorldTriangles'],installedTower3EntryVerbatim=o['completeInstalledTower3EntryVerbatim'],primaryPacketFindingsVerbatim=(PRIMARY/'PRIMARY_FINDINGS.md').read_text(),primaryImagesActuallyInspectedNotRegistered=True,noPlaneContactGradeRimDistancePredicatesRerun=True,exactCorrespondenceDoesNotProveOwnershipOrValidJoin=True,precisePrimaryRegistration=False,architecturalRoleAccepted=False,groundRootCredit=False,sourceGeometryChanges=0,terrainChanges=0,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0,exports=exports)
 save(DOC/'diagnostic.json.gz',result);refs.append(DOC/'diagnostic.json.gz');refs.extend(ROOT/x['path']for x in exports)
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for p,sha in pins.items():assert digest((ROOT/p).read_bytes())==sha
 spec=importlib.util.spec_from_file_location('victoria_high_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 frozen=m.freeze(BATCH,'source-only-exact-provider-hierarchy-high-part-correspondence-and-saved-contact-loci',refs,dict(uids=[P,T,T2,T1],priorSourceContext=JOB,exactOriginalTrianglePairs=len(exact),exactOriginalVertexIncidences=len(vertices),completeSavedContactRecords=1276,properCrossingsPreserved=1136,all9FailuresPreserved=True,sourceOnly=True,precisePrimaryRegistration=False,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 assert reservations.owns(lease)
 for p,sha in pins.items():assert digest((ROOT/p).read_bytes())==sha
 print(json.dumps(dict(jobId=frozen['jobId'],exports=len(exports),currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('victoria-original-high-correspondence-'+str(uuid.uuid4()),['building:'+u for u in sorted([P,T,T2,T1])],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
