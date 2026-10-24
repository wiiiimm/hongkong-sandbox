"""Original-root and Tower1 relationship for Tower2's lower extension; no acceptance."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_source_ownership import document,graph_reasons
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-orchards-lower-extension-attribution-v1-20261017';CURRENT=BASE/'government-xl-three-current-originals-v1-20261017';BATCH='government-xl-orchards-original-connection-context-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 selected=read(CURRENT/'selection.json.gz');row=next(r for r in selected['rows']if r['uid']=='landsd/254629:0');path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw);assert len(t)==11517
 graph=graph_reasons(document(raw),row['modelId'],len(t));assert not graph,graph
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];matches=[]
 for url in read(manifest)['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url
  for entry in read(cat)['models']:
   if entry['uid']=='landsd/254621:0':matches.append((cat,entry))
 assert len(matches)==1;cat,entry=matches[0];asset=cat.parent/entry['asset'];otherraw=asset.read_bytes();assert digest(otherraw)==entry['sha256'];other=decode_original_world_triangles(otherraw)
 attribution=read(PRIOR/'attribution.json.gz');ids=np.asarray(attribution['sourceFaces']);far=t[ids];vertices=np.unique(far.reshape(-1,3),axis=0);closest=module('orchards_nearest',HERE/'xl-popcorn-original-panel-distance-20261009.py').closest;witnesses=[]
 for point in vertices:
  distances,points=closest(point,other);j=int(np.argmin(distances));witnesses.append(dict(originalVertex=point.tolist(),tower1Face=j,distanceM=float(distances[j]),nearestTower1Point=points[j].tolist()))
 nearest=min(witnesses,key=lambda r:r['distanceM']);out=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],wholeSourceGraphVerified=True,sourceRoot=row['modelId'],sourceFaces=len(t),tower1SHA256=entry['sha256'],tower1Faces=len(other),extensionVertexCount=len(vertices),nearestTower1VertexWitness=nearest,allVertexWitnesses=witnesses,installationApproved=False,qualification='Original source graph ownership and floating finite-surface witness context only. Vertex distances neither prove whole-surface separation nor structural support. No new per-component structural gate is imposed.')
 save(DOC/'connection.json.gz',out)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,8),dpi=140);ax=fig.add_subplot(111,projection='3d');shown=[]
 for tris,color in [(other,'#c29b5d'),(t,'#4a8eaf')]:
  lower=tris[tris[:,:,1].max(axis=1)<=45.3];shown.append(lower);ax.add_collection3d(Poly3DCollection(lower[:,:,[0,2,1]],facecolors=color,edgecolors='none',alpha=.65))
 bounds=np.concatenate(shown).reshape(-1,3)[:,[0,2,1]];lo=bounds.min(0);hi=bounds.max(0);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(np.maximum(hi-lo,.1));ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('HKPD height');ax.set_title('Original lower structures: Tower1 gold / Tower2 blue');fig.tight_layout();fig.savefig(DOC/'original-lower-pair.png');plt.close(fig)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'attribution.json.gz',CURRENT/'selection.json.gz',manifest,path,cat,asset,HERE/'original_source_ownership.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-popcorn-original-panel-distance-20261009.py']
 result=module('orchards_connection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-original-root-and-pair-connection-context-v1',refs,dict(uids=[row['uid']],summary={k:out[k]for k in ['wholeSourceGraphVerified','sourceRoot','sourceFaces','tower1Faces','extensionVertexCount','nearestTower1VertexWitness']},fullAcceptance=False,nextStep='Inspect original lower-pair export against primary photograph; retain raw identity and physical gates.'))
 print(dict(jobId=result['jobId'],summary=result['summary']),flush=True)
if __name__=='__main__':main()
