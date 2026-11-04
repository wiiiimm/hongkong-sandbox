"""Replay every recorded finite rim contact against actual renderer coordinates."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-rim-contact-replay-v1-20261019';DOC=BASE/BATCH;PATHS=BASE/'government-xl-lai-chi-kok-rim-contact-paths-v1-20261019';ATTR=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_original_shell_intersections_20261009.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PATHS,ATTR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 data=read(SRC/'input.json.gz');allground=np.asarray(data['podium']);ng=len(allground)-37577;assert ng>0;ground=allground[:ng];captures={r['uid']:r for r in read(ATTR/'attributes.json.gz')['rows']};summaries=[]
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  world={u:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for u,r in captures.items()};support=np.concatenate([ground,world['landsd/281463:0']])
  for source in data['rows']:
   uid=source['uid'];t=world[uid];paths=read(PATHS/(uid.split('/')[1]+'.json'))['rows'];out=[]
   for r in paths:
    contact=r['finiteSupportContact'];assert contact;path=r['originalSourcePath'];edgechecks=[]
    for a,b in zip(path,path[1:]):
     common=set(map(tuple,t[a]))&set(map(tuple,t[b]));edgechecks.append(len(common)>=2)
    points=intersection_points(rational_face(t[contact['sourceFace']]),rational_face(support[contact['supportFace']]))
    out.append(dict(sample=r['sample'],sourcePath=path,sharedEdgesPreserved=all(edgechecks),positiveDimensionalContact=len(points)>1,contact=dict(sourceFace=contact['sourceFace'],supportFace=contact['supportFace'],points=[[float(v)for v in p]for p in sorted(points)])))
   summary=dict(uid=uid,mode=mode,samples=len(out),sharedEdgePathsPreserved=sum(r['sharedEdgesPreserved']for r in out),finiteContactsPreserved=sum(r['positiveDimensionalContact']for r in out),wholeWorldSHA256=digest(np.asarray(t,dtype='<f8').tobytes()));summaries.append(summary);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(summary=summary,rows=out));print(summary,flush=True)
 save(DOC/'summary.json',dict(rows=summaries,installationApproved=False,qualification='Replay of original failed sample generator paths and contacts in renderer coordinates. Does not claim newly resampled per-mode raw rim sets are identical or replace acceptance.'))
 module('rim_replay_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-rim-finite-contact-renderer-replay',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in data['rows']],rows=summaries,installationApproved=False))
if __name__=='__main__':main()
