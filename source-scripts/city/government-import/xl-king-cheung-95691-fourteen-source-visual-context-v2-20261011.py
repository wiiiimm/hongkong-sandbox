"""Complete original14 unresolved visual shapes and conditional envelope context.

Source-only architectural interpretation evidence. Unchanged .1m full-boundary
negatives remain; no distance rerun, placement fitting, function or root credit.
"""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID,SOURCE_SHA
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
MOUNTS=BASE/'government-xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v2-20261011'
GRAPH=BASE/'government-xl-king-cheung-95691-complete908-source-component-interfaces-v2-20261011'
FOUNDATION=BASE/'government-xl-king-cheung-95691-current-foundation-skin-role-proposal-v2-20261011'
BATCH='government-xl-king-cheung-95691-fourteen-source-visual-context-v2-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UN=[35,36,37,38,849,856,858,859,860,861,862,863,866,867]
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,MOUNTS,GRAPH,FOUNDATION]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');capt=read(INPUT/'complete-current-actual-source-and-ground.json.gz');mounts=read(MOUNTS/'diagnostic.json.gz');graph=read(GRAPH/'diagnostic.json.gz');assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==capt['inputHashes']['3d-viewer/city/data/manifest.json']
 rows=[]
 for mode,stream in data['completeWorldStreams'].items():
  w=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert digest(w.tobytes())==stream['completeWorldTriangleSHA256']
  m=next(r for r in mounts['rows']if r['arithmetic']==mode);g=next(r for r in graph['rows']if r['arithmetic']==mode);parts=g['completeOriginalTopology']['sharedEdgeConnectedComponents'];assert m['unresolvedCompleteBoundaryComponents']==UN
  mapping={i:k for k,ids in enumerate(parts)for i in ids};out=[]
  for component in UN:
   record=next(r for r in m['completeDetachedComponentDispositions']if r['originalComponent']==component);ids=parts[component];t=w[ids];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);size=np.linalg.norm(normal,axis=1)
   failed=[]
   for edge in record['completeBoundaryEdgeFiniteHostBandProofs']:
    if edge['fullEdgeAssociated']:continue
    failed.append(dict(originalBoundaryEdgeIndex=edge['originalBoundaryEdgeIndex'],completeOriginalEdge=edge['completeOriginalEdge'],
     unchangedFiniteBandTrials=[dict(coordinatePermutation=x['coordinatePermutation'],verifiedCompleteOriginalEdgeFiniteFacadeBand=x['completeFiniteHostBandProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'],
      exactCertifiedMergedIntervals=x['completeFiniteHostBandProof']['exactFacetAndEdgeCertifiedMergedIntervals'],strictBandM=x['completeFiniteHostBandProof']['strictBandM'])for x in edge['completeCoordinatePermutationTrials']],emptyHostScopeExplicitlyUnqualified=edge['emptyHostScopeExplicitlyUnqualified']))
   near=record['completeHostCandidateFaceIds'];assert not record['completeBoundaryAssociated'] and failed
   out.append(dict(originalComponent=component,completeOriginalFaces=ids,completeOriginalGeometry=t.tolist(),completeWorldBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],
    completeRealFacetNormals=normal.tolist(),normalYRatios=np.divide(normal[:,1],size).tolist(),
    completeOriginalClosedBoundaryLoops=record['completeEveryOriginalClosedBoundaryLoop'],completeUnqualifiedBoundaryEdges=failed,
    completeConditionalNearHostFaceIds=near,completeConditionalNearHostComponents=sorted({mapping[i]for i in near}),completeConditionalNearHostGeometry=w[near].tolist(),
    complete177OtherVisualDetailsRemainSeparatelyQualified=True,interpretedArchitecturalRoleAccepted=False,structuralRootCredit=False))
  rows.append(dict(arithmetic=mode,completeWorldSHA256=stream['completeWorldTriangleSHA256'],complete14UnresolvedOriginalParts=out))
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,raw191MountFailurePreserved=True,
  sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 w=np.asarray(data['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8');m=next(r for r in mounts['rows']if r['arithmetic']=='providerOriginal');g=next(r for r in graph['rows']if r['arithmetic']=='providerOriginal');parts=g['completeOriginalTopology']['sharedEdgeConnectedComponents'];images=[]
 for label,chosen,zlimits in [('roof-four',UN[:4],[129.6,133]),('lower-ten',UN[4:],[17.5,22.5]),('whole-building-all-fourteen',UN,[12,134])]:
  fig=plt.figure(figsize=(12,9),dpi=200);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(w[:,:,[0,2,1]],facecolors='#91a2ae',edgecolors='#526570',linewidths=.09,alpha=.08))
  for k in chosen:
   ids=parts[k];p=w[ids];record=next(r for r in m['completeDetachedComponentDispositions']if r['originalComponent']==k)
   near=record['completeHostCandidateFaceIds'];ax.add_collection3d(Poly3DCollection(w[near][:,:,[0,2,1]],facecolors='#60a6c3',edgecolors='#2d677f',linewidths=.3,alpha=.35))
   ax.add_collection3d(Poly3DCollection(p[:,:,[0,2,1]],facecolors='#d87536',edgecolors='#823016',linewidths=.45,alpha=.85))
   center=p.mean((0,1));ax.text(center[0],center[2],center[1],str(k),fontsize=8,color='#7c240f')
   for e in record['completeBoundaryEdgeFiniteHostBandProofs']:
    if not e['fullEdgeAssociated']:
     line=np.asarray(e['completeOriginalEdge']);ax.plot(line[:,0],line[:,2],line[:,1],color='#d90030',linewidth=1.8)
  owned=w[np.concatenate([parts[k]for k in chosen])];lo=owned.min((0,1));hi=owned.max((0,1));margin=2 if label!='whole-building-all-fourteen'else 3
  ax.set_xlim(lo[0]-margin,hi[0]+margin);ax.set_ylim(lo[2]-margin,hi[2]+margin);ax.set_zlim(*zlimits);ax.set_box_aspect((hi[0]-lo[0]+2*margin,hi[2]-lo[2]+2*margin,zlimits[1]-zlimits[0]));ax.view_init(elev=28,azim=-52)
  ax.set_xlabel('Original world X / m');ax.set_ylabel('Original world Z / m');ax.set_zlabel('HKPD / m');ax.set_title('Complete original '+label+'; unresolved original boundary edges red\nBlue = actual .1m-nominated qualified-source envelope; no mount/root/function credit')
  fig.tight_layout();image=DOC/(label+'-source-context-2400x1800.png');fig.savefig(image,dpi=200);plt.close(fig);images.append(image)
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in capt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 s=importlib.util.spec_from_file_location('king14_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'complete14-original-visual-shapes-near-hosts-failed-boundaries-and-actual-context',refs+[DOC/'diagnostic.json.gz']+images,dict(uids=[UID],completeOriginalVisualParts=14,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('king-cheung14-context-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
