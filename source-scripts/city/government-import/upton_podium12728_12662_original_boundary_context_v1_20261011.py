"""DRAFT visualization and provider-root context only; no identity/solid judgement."""
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from original_source_ownership import document,graph_reasons
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-podium12728-12662-original-boundary-context-v1-20261011';DOC=B/BATCH
SOURCE=B/'government-xl-upton-podium12728-12662-original-foreign-conflict-proposal-v1-20261011/source-inputs.json';RAW=B/'government-xl-upton-podium12728-12662-complete-original-foreign-conflict-attribution-v1-20261011/diagnostic.json.gz';RECOVERY=B/'government-xl-upton-podium12728-12662-frozen-json-key-readback-recovery-v1-20261011/result.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not (DOC/'context.json').exists()and not list(DOC.glob('*.png'));r=read(RECOVERY)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 d=read(RAW);sources=read(SOURCE)['sources'];assert len(sources)==2 and len(d['allExactFiniteOriginalContacts'])==23
 refs=[ref(p)for p in [Path(__file__),SOURCE,RAW,RECOVERY,HERE/'original_source_ownership.py',HERE/'exact_packed_world_geometry_20261009.py']];tris={};roots=[]
 for s in sources:
  uid=s['uid'];asset=ROOT/s['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==s['sourceSHA256'];refs.append(ref(asset));t=decode_original_world_triangles(raw);assert len(t)==s['triangles']and digest(t.astype('<f8').tobytes())==d['sourceTuples'][uid][4];tris[uid]=t
  g=document(raw);assert not graph_reasons(g,s['modelId'],len(t));root=g['nodes'][g['scenes'][0]['nodes'][0]];roots.append(dict(uid=uid,sourceSHA256=s['sourceSHA256'],modelId=s['modelId'],buildingCSUID=s['source']['building']['buildingCSUID'],sourceEntry=s['native']['model']['sourceEntry'],nativeCacheKey=s['native']['cacheKey'],nativeResultSHA256=s['native']['resultSha'],originalRoot=root,wholeOriginalFaces=len(t),genuineBodies=len(d['completeOriginalCensuses'][uid]['sharedEdgeConnectedComponents']),zeroOriginalFaces=d['completeOriginalCensuses'][uid]['exactNonrenderingOriginalFaces']))
 contacts=[np.asarray([[float(Fraction(v))for v in p]for p in x['exactPoints']])for x in d['allExactFiniteOriginalContacts']];points=np.concatenate(contacts);colors=['#dd8626','#207aad'];allv=np.concatenate(list(tris.values())).reshape(-1,3);lo,hi=allv.min(0),allv.max(0);cl,ch=points.min(0),points.max(0);DOC.mkdir(parents=True,exist_ok=True)
 fig=plt.figure(figsize=(16,8));plan=fig.add_subplot(121);view=fig.add_subplot(122,projection='3d')
 for (uid,t),color in zip(tris.items(),colors):
  plan.add_collection(PolyCollection(t[:,:,[0,2]],facecolors=color,edgecolors=color,linewidths=.08,alpha=.25));view.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.04,alpha=.15))
 for p in contacts:plan.plot(p[:,0],p[:,2],color='#bb123c',lw=1);view.plot(p[:,0],p[:,2],p[:,1],color='#bb123c',lw=1.8)
 plan.set(xlim=(lo[0]-2,hi[0]+2),ylim=(lo[2]-2,hi[2]+2),xlabel='Original world X (m)',ylabel='Original world Z (m)',title='Complete originals: orange12728 / blue12662; red23crossings');plan.set_aspect('equal');view.set(xlim=(lo[0]-2,hi[0]+2),ylim=(lo[2]-2,hi[2]+2),zlim=(lo[1]-2,hi[1]+2),xlabel='X',ylabel='Z',zlabel='Y / HKPD',title='Complete original source; display view only');view.set_box_aspect((hi-lo)[[0,2,1]]);view.view_init(elev=22,azim=-55);fig.tight_layout();whole=DOC/'complete-original-podiums-plan-and-3d-3200x1600.png';fig.savefig(whole,dpi=200);plt.close(fig)
 fig=plt.figure(figsize=(12,8));ax=fig.add_subplot(111,projection='3d')
 for (uid,t),color in zip(tris.items(),colors):ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.10,alpha=.20))
 for p in contacts:ax.plot(p[:,0],p[:,2],p[:,1],color='#bb123c',lw=2.2)
 ax.set(xlim=(cl[0]-1,ch[0]+1),ylim=(cl[2]-1,ch[2]+1),zlim=(cl[1]-1,ch[1]+1),xlabel='Original X',ylabel='Original Z',zlabel='Y / HKPD',title='Crossing boundary crop only; complete triangles submitted');ax.set_box_aspect((ch-cl+2)[[0,2,1]]);ax.view_init(elev=22,azim=-55);fig.tight_layout();crop=DOC/'original23-main-body-crossings-context-crop-2400x1600.png';fig.savefig(crop,dpi=200);plt.close(fig)
 for e in refs:assert ref(ROOT/e['path'])==e
 save(DOC/'context.json',dict(sourceOnly=True,visualizationOnly=True,sourceGeometryChanges=0,identityAccepted=False,ownershipOrEngineeringRelationInferred=False,solidCollisionProven=False,providerRootContext=roots,all23MainBody0ToMainBody0CrossingsPreserved=True,originalCompleteFaces=2047,outputRefs=[ref(whole),ref(crop)],outputDimensions=[[3200,1600],[2400,1600]],displayOnlyRationalPointsConvertedToBinary64=True,completeSourcePlanesAndVerticesUnchanged=True,cropNotWholeSceneVisibility=True,evidenceRefs=refs,qualification='Both unchanged complete source actors have separate exact named FME roots and own original provider entries. Those graph facts prove source container provenance only, not common architectural ownership, intended shared interfaces, solid intersection, support, footprint authority or current acceptance. Original23proper finite crossings remain open. No pose fit, vertex snap, face removal or identity waiver.'))
if __name__=='__main__':main()
