"""ROOT-executed saved-array diagnostic only; no decoder/DB/lease or approval."""
import argparse,gzip,hashlib,json,math,struct
from pathlib import Path
PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[3]
CONTRACT=PACKET/'input-contract.json'
OUTPUT=PACKET/'saved-source-context-output-v1'
UID='landsd/281463:0'
SOURCE='1480540e0a32849425d5238eeea7ecb3a7124633226c1eae9cab2d041b968d86'
WORLD='d8ab9b872ef0696d3d95d8e47df0f64db2e540229961f0142d1e83af7cf08b22'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
JOB='26011fd1f69bb7190fcb7d4852a188899f3c34888f8c4506bb69b902922cc3be'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def fence(c,cs):
 assert sha(CONTRACT)==cs
 for path,value in c['filePins'].items():assert sha(ROOT/path)==value,(path,value)
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 assert sha(Path(__file__))==c['callerSHA256']
def load_saved(c):
 a=read(ROOT/c['diagnosticPath']);r=read(ROOT/c['resultPath']);v=read(ROOT/c['rootVerificationPath'])
 assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback'] is True and v['leaseReleased'] is True
 assert a['uid']==UID and a['sourceSHA256']==SOURCE and a['worldTrianglesSHA256']==WORLD
 assert len(a['completeComponents'])==37 and len(a['historicalNonrenderingOriginalFacesUncredited'])==17
 assert a['completeOriginalFaces']==37577 and a['originalCoordinateView']=='providerOriginal only; no runtime arithmetic views captured'
 triangles={};owners={}
 for comp in a['completeComponents']:
  assert len(comp['completeOriginalFaceIds'])==len(comp['completeOriginalWorldTriangles'])
  for face,tri in zip(comp['completeOriginalFaceIds'],comp['completeOriginalWorldTriangles']):
   assert face not in triangles;triangles[face]=tri;owners[face]=comp['component']
 zero=a['historicalNonrenderingOriginalFacesUncredited']
 for face,tri in zip(zero,a['exactNonrenderingOriginalPrimitiveWorldTriangles']):
  assert face not in triangles;triangles[face]=tri;owners[face]=None
 assert sorted(triangles)==list(range(37577)) and len(zero)==17
 h=hashlib.sha256()
 for face in range(37577):
  tri=triangles[face];assert len(tri)==3 and all(len(p)==3 and all(math.isfinite(x) for x in p) for p in tri)
  h.update(struct.pack('<9d',*(x for p in tri for x in p)))
 assert h.hexdigest()==WORLD # Representation binding to already decoded array; no source decode.
 far=a['historicalFarFaceIdsRecovered'];assert len(far)==len(set(far))==106 and all(owners[f]==0 for f in far)
 assert a['completeComponents'][0]['component']==0 and len(a['completeComponents'][0]['completeOriginalFaceIds'])==34463
 actors=a['providerAndOperatorScopeRecordVerbatim']['sevenIndependentForeignActorsVerbatim'];assert len(actors)==7
 assert all(a[k] is False for k in ('sourceRoleAccepted','identityAccepted','physicalAccepted','currentAcceptance'))
 return a,triangles,owners,far,zero
def edge_keys(tri):
 # Equality of saved finite double tuples is exact original endpoint equality.
 # No collinear partial-edge merge, point glue or inferred source contact.
 return [tuple(sorted((tuple(tri[i]),tuple(tri[(i+1)%3])))) for i in range(3) if tri[i]!=tri[(i+1)%3]]
def within_closed_box(tri,lo,hi):
 return all(max(p[k] for p in tri)>=lo[k] and min(p[k] for p in tri)<=hi[k] for k in range(3))
def view_only_context(triangles,owners,far,zero):
 wanted={e for f in far for e in edge_keys(triangles[f])}
 incidents={e:[] for e in wanted}
 for f,tri in triangles.items():
  if f in zero:continue
  for e in set(edge_keys(tri)):
   if e in incidents:incidents[e].append(f)
 rows=[{'endpoints':e,'incidentOriginalFaceIds':sorted(ids),'incidentComponentIds':[owners[f] for f in sorted(ids)]} for e,ids in sorted(incidents.items())]
 adjacent=sorted({f for ids in incidents.values() for f in ids}-set(far))
 lo=[min(p[k] for f in far for p in triangles[f])-10 for k in range(3)]
 hi=[max(p[k] for f in far for p in triangles[f])+10 for k in range(3)]
 local=sorted(f for f,t in triangles.items() if within_closed_box(t,lo,hi))
 # 10m here is a declared viewing window only, never an identity/clearance threshold.
 return rows,adjacent,local,[lo,hi]
def export_views(a,triangles,far,local):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 def plane(ax,ids,x,y,title,color,alpha):
  ax.add_collection(PolyCollection([[(p[x],p[y]) for p in triangles[f]] for f in ids],facecolors=color,edgecolors=color,linewidths=.2,alpha=alpha));ax.autoscale_view();ax.set_aspect('equal',adjustable='datalim');ax.set_xlabel('XYZ'[x]+' source world (m)');ax.set_ylabel('XYZ'[y]+' source world (m)');ax.set_title(title)
 def oblique(ax,ids,title,elev,azim):
  ax.add_collection3d(Poly3DCollection([[(p[0],p[2],p[1]) for p in triangles[f]] for f in ids],facecolor='#999999',edgecolor='#666666',linewidth=.15,alpha=.35))
  ax.add_collection3d(Poly3DCollection([[(p[0],p[2],p[1]) for p in triangles[f]] for f in far],facecolor='#ff00cc',edgecolor='#990077',linewidth=.4,alpha=1))
  points=[p for f in ids for p in triangles[f]];bounds=[(min(p[k] for p in points),max(p[k] for p in points)) for k in (0,2,1)]
  for fn,b in zip((ax.set_xlim,ax.set_ylim,ax.set_zlim),bounds):fn(*b)
  ax.set_box_aspect([max(b[1]-b[0],.01) for b in bounds]);ax.view_init(elev=elev,azim=azim);ax.set_xlabel('X (m)');ax.set_ylabel('Z (m)');ax.set_zlabel('Y (m)');ax.set_title(title)
 footer='ProviderOriginal saved coordinates only. Magenta diagnostic overlay; not GPU visibility or registered primary imagery. No source/identity/ground/root/foreign acceptance.'
 files=[]
 fig=plt.figure(figsize=(15,9),dpi=200);ax=fig.add_subplot(111)
 plane(ax,sorted(triangles),0,2,'Complete original 37,577 source facets; far106 magenta', '#999999',.35);plane(ax,far,0,2,'Complete source plan and exact far subset','#ff00cc',1)
 rings=a['providerAndOperatorScopeRecordVerbatim']['currentFormVerbatim']['rings']
 for ring in rings:
  pts=ring+[ring[0]];ax.plot([p[0] for p in pts],[p[1] for p in pts],color='#0033cc',linewidth=.8)
 ax.text(.01,.01,'Blue: current original form ring; source-overlay only, no primary-plan registration',transform=ax.transAxes)
 fig.text(.03,.02,footer,fontsize=8);fig.savefig(OUTPUT/'whole-source-plan-3000x1800.png');plt.close(fig);files.append('whole-source-plan-3000x1800.png')
 fig=plt.figure(figsize=(15,9),dpi=200)
 oblique(fig.add_subplot(121,projection='3d'),local,'Complete closed-box local facets + far106; view A',30,-55)
 oblique(fig.add_subplot(122,projection='3d'),local,'Same unchanged local source facets; view B',35,130)
 fig.text(.03,.02,footer,fontsize=8);fig.savefig(OUTPUT/'far-local-two-oblique-3000x1800.png');plt.close(fig);files.append('far-local-two-oblique-3000x1800.png')
 fig=plt.figure(figsize=(15,9),dpi=200)
 oblique(fig.add_subplot(221,projection='3d'),far,'Far106 isolated; original winding/coordinates retained',30,-55)
 for slot,x,y in ((222,0,1),(223,0,2),(224,2,1)):
  plane(fig.add_subplot(slot),far,x,y,'Far106 isolated '+ 'XYZ'[x]+'/'+'XYZ'[y], '#ff00cc',.7)
 fig.text(.03,.02,footer+' Exact facet labels/ABC coordinates are in context.json; thin projections may be visually unresolved.',fontsize=8)
 fig.savefig(OUTPUT/'far-isolated-projections-3000x1800.png');plt.close(fig);files.append('far-isolated-projections-3000x1800.png')
 # Inspect actual saved raster headers; no preview/rescale credit.
 for f in files:
  raw=(OUTPUT/f).read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(3000,1800)
 return [{'path':str((OUTPUT/f).relative_to(ROOT)),'sha256':sha(OUTPUT/f),'dimensions':[3000,1800]} for f in files]
def main():
 p=argparse.ArgumentParser();p.add_argument('--preflight-only',action='store_true');p.add_argument('--export-saved-source-context-only',action='store_true');args=p.parse_args();assert args.preflight_only != args.export_saved_source_context_only
 c=read(CONTRACT);cs=sha(CONTRACT);fence(c,cs);a,triangles,owners,far,zero=load_saved(c);assert not OUTPUT.exists()
 if args.preflight_only:
  fence(c,cs);print(json.dumps({'passed':True,'completeSavedOriginalFaces':37577,'component0Faces':34463,'farFacesInComponent0':106,'nonrenderingOriginalFaces':17,'priorCompleteJob':JOB,'noSourceDecode':True,'noEdgeCalculation':True,'noRender':True,'noDB':True,'noLease':True,'currentAcceptance':False}));return
 OUTPUT.mkdir();rows,adjacent,local,bounds=view_only_context(triangles,owners,far,zero)
 out={'uid':UID,'sourceSHA256':SOURCE,'worldTrianglesSHA256':WORLD,'priorCompleteJob':JOB,'allInputHashes':c['filePins'],'completeOriginalFaceCount':37577,'completeSourceComponentCount':37,'component0Faces':34463,'farOriginalFaceIds':far,'farOriginalTrianglesABC':[{'face':f,'component':owners[f],'A':triangles[f][0],'B':triangles[f][1],'C':triangles[f][2]} for f in far],'completeEndpointEdgeIncidences':rows,'exactEdgeAdjacentOriginalFaceIds':adjacent,'adjacentOriginalTriangles':[{'face':f,'component':owners[f],'triangle':triangles[f]} for f in adjacent],'closedViewBox':bounds,'completeLocalBoxFaceIds':local,'completeLocalTriangles':[{'face':f,'component':owners[f],'triangle':triangles[f]} for f in local],'nonrenderingOriginalFacesRetainedUncredited':zero,'sevenIndependentForeignActorsVerbatim':a['providerAndOperatorScopeRecordVerbatim']['sevenIndependentForeignActorsVerbatim'],'priorRoleRecordVerbatim':a['priorRoleRecordVerbatim'],'primaryImagesNotRegistered':True,'viewBoxHasNoAcceptanceMeaning':True,'sourceRoleAccepted':False,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'geometryChanges':0,'modelReviewWrites':0,'newlyInstalled':0}
 out['actualExports']=export_views(a,triangles,far,local);fence(c,cs)
 (OUTPUT/'context.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 (OUTPUT/'terminal.json').write_text(json.dumps({'complete':True,'contextSHA256':sha(OUTPUT/'context.json'),'codeSHA256':sha(Path(__file__)),'contractSHA256':cs,'allInputHashesUnchanged':True,'actualExports':out['actualExports'],'noSourceDecode':True,'noDB':True,'noLease':True,'currentAcceptance':False},sort_keys=True,indent=2)+'\n')
 print(json.dumps({'complete':True,'contextSHA256':sha(OUTPUT/'context.json'),'adjacentFaces':len(adjacent),'localViewFaces':len(local),'actualExports':out['actualExports'],'currentAcceptance':False}))
if __name__=='__main__':main()
