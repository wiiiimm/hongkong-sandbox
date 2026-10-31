"""Source-authored vertical wall context in all four coordinate modes; no approval."""
from pathlib import Path
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-vertical-context-v1-20261019';DOC=BASE/BATCH
names=['government-xl-lai-chi-kok-all-contact-ground-attribution-v2-20261019','government-xl-lai-chi-kok-four-mode-foundations-v3-20261019','government-xl-lai-chi-kok-runtime-buried-coverage-v4-20261019']+['government-xl-lai-chi-kok-buried-coverage-'+m+'-v1-20261019' for m in ['literal','explicitLeftF32','explicitBalancedF32']]
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   r=read(BASE/name/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(BASE/name/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 groundpath=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/281463:0-ground.json.gz';assert str(groundpath.relative_to(ROOT)) in pins
 terrain=np.asarray(read(groundpath)['completeAdjoiningTerrain']);polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;terrain=terrain[valid];tree=shapely.STRtree(polys[valid]);helper=module('vertical_samples',HERE/'xl-final-script-pass.py');rows=[]
 for mode,name in zip(['original','literal','explicitLeftF32','explicitBalancedF32'],names[2:]):
  ids=read(BASE/name/'exposed-terrain-checks.json')['projectedVerticalBuriedFaceIds'];f=read(BASE/names[1]/('281463:0-'+mode+'.json'));byid={v['faceId']:v for v in f['buriedFaces']};t=np.asarray([byid[i]['vertices'] for i in ids]);points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);heights=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain,tree).reshape(-1,4);assert np.isfinite(heights).all();gaps=points[:,:,1]-heights;cg=np.asarray([byid[i]['gaps']for i in ids]);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ratios=np.abs(norm[:,1])/np.linalg.norm(norm,axis=1)
  detail=[dict(faceId=i,vertices=t[k].tolist(),normalYRatio=float(ratios[k]),originalGaps=gaps[k].tolist(),candidateGaps=cg[k].tolist(),candidateMinusOriginalTerrain=(gaps[k]-cg[k]).tolist()) for k,i in enumerate(ids)]
  summary=dict(mode=mode,faces=len(ids),sourceBuriedFaces=int((gaps<-.5).all(1).sum()),maxNormalYRatio=float(ratios.max()),maximumTerrainRaisedMetres=float((gaps-cg).max()),maximumTerrainLoweredMetres=float((cg-gaps).max()),wholeWorldSHA256=f['wholeWorldSHA256'],installationApproved=False);rows.append(summary);save(DOC/(mode+'.json'),dict(summary=summary,faces=detail));print(summary,flush=True)
  if mode=='original':
   fig=plt.figure(figsize=(14,8));ax=fig.add_subplot(projection='3d');ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor='crimson',edgecolor='black',linewidth=.25,alpha=.8));lo=t.min((0,1));hi=t.max((0,1));ax.set(xlim=(lo[0]-5,hi[0]+5),ylim=(lo[2]-5,hi[2]+5),zlim=(lo[1]-1,hi[1]+1),xlabel='World X',ylabel='World Z',zlabel='Height');ax.set_box_aspect((hi[0]-lo[0],hi[2]-lo[2],max(20,hi[1]-lo[1])));ax.view_init(25,-65);ax.set_title('71 original buried vertical faces — source coordinates, no geometry edits');fig.savefig(DOC/'vertical-faces.png',dpi=140);plt.close(fig)
 save(DOC/'summary.json',dict(rows=rows,installationApproved=False,sampledComparisonOnly=True))
 refs.append(HERE/'xl-final-script-pass.py');module('vertical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-vertical-wall-source-terrain-context',list(dict.fromkeys(refs)),dict(uids=['landsd/281463:0'],rows=rows,installationApproved=False,sampledComparisonOnly=True))
if __name__=='__main__':main()
