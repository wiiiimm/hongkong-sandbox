"""Exact source/companion census and full buried-face context; no model edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-source-context-v1-20261020';DOC=BASE/BATCH;UID='landsd/289787:0'
SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];receipts={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,GROUND]:
   p=folder/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);receipts[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==receipts[folder][str(p.relative_to(ROOT))],str(p);refs.append(p);return read(p)
 selection=take(SRC,SRC/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 groundpath=HERE/'local'/GROUND.name/'289787:0-ground.json.gz';g=np.asarray(take(GROUND,groundpath)['completeAdjoiningTerrain']);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==22002
 old=take(GROUND,GROUND/'289787:0.json');assert old['sourceSHA256']==row['sourceSHA256']
 tile=ROOT/'3d-viewer'/row['source']['tile'];forms=read(tile)['buildings'];own=next(b for b in forms if b['uid']==UID);assert own==row['source']['building'];refs.append(tile);siblings={b['uid']:b for b in forms if b.get('parent')==own['parent']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');sha,registry=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone();assert sha==row['native']['resultSha']
 nominations=[]
 for model in registry['models']:
  matched=[]
  for candidate in model.get('matching',{}).get('officialCandidates',[]):
   for uid,b in siblings.items():
    if candidate.get('objectId')==b['objectId']and candidate.get('buildingCSUID')==b['buildingCSUID']:matched.append(uid)
  if matched:nominations.append(dict(model=model,exactViewerUids=sorted(set(matched))))
 save(DOC/'registry.json.gz',dict(cacheKey=row['native']['cacheKey'],resultSHA256=sha,result=registry))
 save(DOC/'companion-nominations.json',dict(uid=UID,sourceForms=siblings,nominations=nominations,missing=sorted(set(siblings)-{u for m in nominations for u in m['exactViewerUids']}),installationApproved=False))
 final=module('mount_sterling_faces',HERE/'xl-final-script-pass.py');diagnostic=face_diagnostics(final,tri,g);buried=diagnostic['buriedFaces'];ids=[r['faceIndex']for r in buried];up=[r['faceIndex']for r in buried if r['upward']];assert len(ids)==old['foundation']['fullyBuriedTriangles']==851 and len(up)==old['foundation']['fullyBuriedUpwardTriangles']==249
 save(DOC/'complete-face-diagnostic.json.gz',dict(uid=UID,sourceSHA256=row['sourceSHA256'],**diagnostic))
 fig,axes=plt.subplots(1,3,figsize=(18,8))
 for ax,dims,label in zip(axes,[(0,2),(0,1),(2,1)],['Plan X/Z','Elevation X/Y','Elevation Z/Y']):
  ax.add_collection(PolyCollection(tri[:,:,dims],facecolors='#c7d0d9',edgecolors='none',alpha=.22));ax.add_collection(PolyCollection(tri[ids][:,:,dims],facecolors='#e8732b',edgecolors='none',alpha=.8));ax.add_collection(PolyCollection(tri[up][:,:,dims],facecolors='#d82b4b',edgecolors='none',alpha=.9));ax.autoscale();ax.set_title(label);ax.set_xlabel('metres')
  if dims[1]==1:ax.set_ylabel('HKPD metres')
  else:
   ax.set_aspect('equal')
   for uid,b in siblings.items():
    r=np.asarray(b['rings'][0]);ax.plot(r[:,0],r[:,1],lw=.6,color='#2c475e');ax.text(*np.mean(r,axis=0),uid.split('/')[1].split(':')[0],fontsize=6)
 fig.suptitle('Mount Sterling Mall unchanged original: orange851 buried faces; red249 upward\nGrey whole original; exact government adjoining terrain diagnostic, not acceptance.');fig.tight_layout();fig.savefig(DOC/'source-context.png',dpi=160);plt.close(fig)
 rows=[]
 for i in ids:
  t=tri[i];n=np.cross(t[1]-t[0],t[2]-t[0]);length=float(np.linalg.norm(n));edges=np.linalg.norm(t-np.roll(t,1,axis=0),axis=1)
  rows.append(dict(face=i,upward=i in up,area=length/2,minimumAltitude=length/float(max(edges))if max(edges)>0 else 0,bounds=[t.min(0).tolist(),t.max(0).tolist()],unitNormal=(n/length).tolist()if length else [0,0,0]))
 save(DOC/'face-context.json.gz',dict(rows=rows))
 summary=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(tri),coveredFaces=diagnostic['completeTerrainTriangles'],buriedFaces=len(ids),upwardBuriedFaces=len(up),sameParentForms=len(siblings),nominatedOriginals=len(nominations),ownOriginals=[m['model']['modelId']for m in nominations if UID in m['exactViewerUids']],missingCompanions=sorted(set(siblings)-{u for m in nominations for u in m['exactViewerUids']}),sourceGeometryChanges=0,installationApproved=False)
 save(DOC/'summary.json',summary);refs.extend([HERE/'china_ferry_current_foundations_v1_20261020.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('mount_sterling_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-source-companion-and-burial-context',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
if __name__=='__main__':main()
