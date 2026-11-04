"""View the exact original platform extension behind the raw identity extent flag."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-extent-closeup-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-next-five-original-extent-context-v1-20261018';SEL=BASE/'government-xl-next-five-original-identity-v1-20261018'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 historical_manifest=None
 for e in r['evidenceRefs']:
  p=ROOT/e['path']
  if e['path']=='3d-viewer/city/data/manifest.json':historical_manifest=dict(historicalSHA256=e['sha256'],currentSHA256=digest(p.read_bytes()));continue
  assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 current=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';cr=read(current/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cr['jobId'],)).fetchone()==('complete',cr)
 refs.append(current/'result.json')
 for e in cr['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 info=read(SRC/'281463:0.json');row=next(r for r in read(SEL/'selection.json.gz')['rows']if r['uid']=='landsd/281463:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==info['sourceSHA256'];currentrow=next(r for r in read(current/'selection.json.gz')['rows']if r['uid']==row['uid']);assert currentrow['sourceSHA256']==row['sourceSHA256']and currentrow['source']['building']==row['source']['building'];t=decode_original_world_triangles(raw);assert digest(np.asarray(t,dtype='<f8').tobytes())==info['worldSHA256'];ids=info['completeOver10mFaceIds'];far=t[ids];lo=far.min((0,1));hi=far.max((0,1));mask=(t[:,:,0].max(1)>=lo[0]-12)&(t[:,:,0].min(1)<=hi[0]+12)&(t[:,:,2].max(1)>=lo[2]-12)&(t[:,:,2].min(1)<=hi[2]+12);context=t[mask];DOC.mkdir(parents=True)
 fig=plt.figure(figsize=(14,7))
 for pane,az in enumerate([-45,135]):
  ax=fig.add_subplot(1,2,pane+1,projection='3d');ax.add_collection3d(Poly3DCollection(context[:,:,[0,2,1]],facecolor='#a8c3cb',edgecolor='#627b85',linewidth=.15,alpha=.22));ax.add_collection3d(Poly3DCollection(far[:,:,[0,2,1]],facecolor='#df6253',edgecolor='#622020',linewidth=.4,alpha=.95));ax.set(xlim=(lo[0]-12,hi[0]+12),ylim=(lo[2]-12,hi[2]+12),zlim=(context[:,:,1].min()-1,context[:,:,1].max()+1));ax.view_init(28,az);ax.set_box_aspect((hi[0]-lo[0]+24,hi[2]-lo[2]+24,np.ptp(context[:,:,1])+2));ax.set_title('Opposite source view '+str(pane+1))
 fig.suptitle('Unchanged platform: red facets beyond footprint +10m; full nearby source shown');fig.tight_layout();fig.savefig(DOC/'extent-closeup.png',dpi=160);plt.close(fig)
 summary=dict(historicalManifestRebound=historical_manifest,currentSourceAndFootprintUnchanged=True,uid=row['uid'],sourceSHA256=row['sourceSHA256'],farFaces=len(ids),faceIds=ids,farBounds=[lo.tolist(),hi.tolist()],contextFaces=int(mask.sum()),installationApproved=False);save(DOC/'summary.json',summary)
 module('extent_closeup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-platform-outlying-extent-closeup',list(dict.fromkeys(refs)),dict(uids=[row['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
