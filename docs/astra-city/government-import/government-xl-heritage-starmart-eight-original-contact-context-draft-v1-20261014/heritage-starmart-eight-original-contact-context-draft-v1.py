"""ROOT-only saved source-coordinate diagrams, no new predicates or acceptance."""
import argparse,gzip,hashlib,json,sys
from fractions import Fraction
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[3];HERE=ROOT/'source-scripts/city/government-import';C=D/'input-contract.json';OUT=D/'source-coordinate-context-output-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def save(p,o):
 b=json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
def fence(c,h):
 assert sha(C)==h and sha(Path(__file__))==c['callerSHA256']
 for p,v in c['filePins'].items():assert sha(ROOT/p)==v,p
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==c['currentManifestSHA256']
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--preflight-only',action='store_true');g.add_argument('--export-saved-source-context-only',action='store_true');p.add_argument('--lease-file',type=Path)
 a=p.parse_args();c=read(C);ch=sha(C);fence(c,ch);assert not OUT.exists()
 museum=read(ROOT/c['museumArrayPath']);star=read(ROOT/c['starArrayPath']);diag=read(ROOT/c['savedCompleteContactDiagnosticPath'])
 assert museum['completeOriginalFaceCount']==15140 and star['completeOriginalFaceCount']==91
 assert museum['sourceSHA256']==c['museumSourceSHA256']and star['sourceSHA256']==c['starSourceSHA256']
 rows=diag['allFourViews'];assert len(rows)==4 and {r['arithmetic']for r in rows}=={'providerOriginal','literal','leftFloat32','balancedFloat32'}
 pairs={(12150,10),(12150,11),(12151,10),(12346,10),(12347,6),(12347,10),(12348,6),(12349,6)}
 for r in rows:
  hits=r['pairs']['Museum-vs-originalStar']['contacts']['contacts'];assert len(hits)==8 and {(x['sourceFaceA'],x['sourceFaceB'])for x in hits}==pairs
  assert all(x['dimension']==1 and x['crossingDiagnostic']['classification']=='proper-noncoplanar-triangle-relative-interior-crossing'and x['crossingDiagnostic']['volumetricCollisionProved']is False for x in hits)
 if a.preflight_only:
  assert a.lease_file is None;fence(c,ch);print(json.dumps({'passed':True,'sourceFaces':[15140,91],'existingContacts':8,'originalFacetsSelected':[6,3],'noNewGeometryPredicatesOrDBLease':True,'resources':c['canonicalResources']}));return
 sys.path.insert(0,str(HERE));from run import reservations,connect
 lease=read(a.lease_file);assert lease['resources']==c['canonicalResources']and reservations.owns(lease);assert reservations.heartbeat(lease,ttl=3600)['ok']
 def receipts():
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY')
   for p in c['priorCompleteReceipts']:
    q=read(ROOT/p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 receipts();OUT.mkdir()
 try:
  import numpy as np
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from matplotlib.collections import LineCollection
  from mpl_toolkits.mplot3d.art3d import Poly3DCollection
  from PIL import Image
  mt=np.asarray(museum['completeOrderedOriginalTriangles'],dtype='<f8');st=np.asarray(star['completeOrderedOriginalTriangles'],dtype='<f8')
  assert mt.shape==(15140,3,3)and st.shape==(91,3,3)
  assert hashlib.sha256(mt.tobytes()).hexdigest()==museum['worldTrianglesSHA256']==c['museumOriginalWorldSHA256']
  assert hashlib.sha256(st.tobytes()).hexdigest()==star['worldTrianglesSHA256']==c['starOriginalWorldSHA256']
  mid=[12150,12151,12346,12347,12348,12349];sid=[6,10,11];hits=next(r for r in rows if r['arithmetic']=='providerOriginal')['pairs']['Museum-vs-originalStar']['contacts']['contacts']
  segments=[np.asarray([[float(Fraction(v))for v in point]for point in x['exactPoints']])for x in hits]
  forms=read(ROOT/c['currentFormsPath']);exports=[]
  def closefig(fig,name):
   path=OUT/name;fig.savefig(path,dpi=150);plt.close(fig)
   with Image.open(path)as im:assert im.size==(3000,1800)
   exports.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'width':3000,'height':1800,'sourceCoordinateDiagramNotGPUVisibility':True})
  def edges(tri,axes):return[np.vstack([t[:,axes],t[0,axes]])for t in tri]
  fig,ax=plt.subplots(figsize=(20,12));ax.add_collection(LineCollection(edges(mt,[0,2]),colors='#bbbbbb',linewidths=.25));ax.add_collection(LineCollection(edges(st,[0,2]),colors='#008ea2',linewidths=.7));ax.add_collection(LineCollection(edges(mt[mid],[0,2]),colors='#c024a5',linewidths=1.4))
  for r in forms:
   for ring in r['form']['rings']:ax.plot([v[0]for v in ring],[v[1]for v in ring],'--',lw=1,label=r['form']['uid'])
  for line in segments:ax.plot(line[:,0],line[:,2],'k-',lw=2)
  ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Original world X = E−834500 (m)');ax.set_ylabel('Original world Z =816500−N (m); increasing Z is SOUTH');ax.legend(loc='upper right');ax.set_title('Complete Museum15140 + proposed original Star91; magenta Museum6, cyan Star, black saved8 loci. No ownership/role approval.')
  closefig(fig,'whole-original-pair-plan-3000x1800.png')
  fig=plt.figure(figsize=(20,12))
  for i,az in enumerate([35,215],1):
   ax=fig.add_subplot(1,2,i,projection='3d');ax.add_collection3d(Poly3DCollection(st,facecolors='#78bfcc',edgecolors='#20758a',alpha=.18,linewidths=.55));ax.add_collection3d(Poly3DCollection(mt[mid],facecolors='#db6cbd',edgecolors='#a42c85',alpha=.3,linewidths=.9))
   for line in segments:ax.plot(*line.T,color='black',lw=2)
   points=np.concatenate([st.reshape(-1,3),mt[mid].reshape(-1,3)]);lo,hi=points.min(axis=0),points.max(axis=0)
   ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[1]-.5,hi[1]+.5);ax.set_zlim(lo[2]-1,hi[2]+1);ax.set_box_aspect(hi-lo);ax.view_init(elev=24,azim=az);ax.set_xlabel('X');ax.set_ylabel('Y');ax.set_zlabel('Z');ax.set_title('Complete91 Star / complete6 Museum interface facets; source-coordinate oblique '+str(az)+'°')
  fig.suptitle('Opposite original source views; black exact saved crossings. Transparent diagnostic overlays do not prove hidden status, root or GPU quality.')
  closefig(fig,'complete-star-and-museum-corner-opposite-oblique-3000x1800.png')
  fig,axs=plt.subplots(1,3,figsize=(20,12))
  for ax,axes,label in zip(axs,[[0,2],[0,1],[2,1]],['X/Z plan','X/Y elevation','Z/Y elevation']):
   ax.add_collection(LineCollection(edges(mt[mid],axes),colors='#c024a5',linewidths=1.1));ax.add_collection(LineCollection(edges(st[sid],axes),colors='#008ea2',linewidths=1.1))
   for t,f in zip(mt[mid],mid):q=t.mean(axis=0);ax.annotate('M'+str(f),q[axes],xytext=(4,8+(mid.index(f)%3)*9),textcoords='offset points',fontsize=8,color='#962075')
   for t,f in zip(st[sid],sid):q=t.mean(axis=0);ax.annotate('S'+str(f),q[axes],xytext=(4,-12-sid.index(f)*9),textcoords='offset points',fontsize=8,color='#00687a')
   for line in segments:ax.plot(line[:,axes[0]],line[:,axes[1]],'k-',lw=2)
   ax.autoscale();ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(axis='x',labelrotation=35);ax.set_title(label);ax.set_xlabel(['X','Y','Z'][axes[0]]);ax.set_ylabel(['X','Y','Z'][axes[1]])
  fig.suptitle('Only full original Museum6 and Star3 facets, no clipping/resizing source. Exact IDs/ABC/rational loci remain in record; no normal-as-function interpretation.')
  fig.subplots_adjust(top=.88,bottom=.17,wspace=.35);closefig(fig,'isolated-nine-interface-facets-orthographic-3000x1800.png')
  assert reservations.heartbeat(lease,ttl=3600)['ok'];fence(c,ch);receipts();assert reservations.owns(lease)
  out={'uids':['landsd/165054:0','landsd/57455:0'],'completeSourceCount':[15140,91],'selectedOriginalFacets':{'Museum':[{'face':f,'ABC':mt[f].tolist()}for f in mid],'Star':[{'face':f,'ABC':st[f].tolist()}for f in sid]},'allFourSavedContactRowsVerbatim':rows,'actualExports':exports,'allInputHashes':c['filePins'],'sourceCoordinatesUnmodified':True,'noNewContactGradeRootOrCoveragePredicate':True,'primaryPlansNotRegisteredToSource':True,'properCrossingsAreNotVolumetricOrOwnershipProof':True,'sourceRoleAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'installationApproved':False}
  save(OUT/'context.json.gz',out);save(OUT/'result.json',{'uids':out['uids'],'complete':True,'contextSHA256':sha(OUT/'context.json.gz'),'actualExports':exports,'physicalAccepted':False,'sourceRoleAccepted':False,'newlyInstalled':0});print(json.dumps(read(OUT/'result.json')),flush=True)
 except BaseException as e:save(OUT/'failure.json',{'complete':False,'errorType':type(e).__name__,'error':str(e),'sourceCorruptionInferred':False});raise
if __name__=='__main__':main()
