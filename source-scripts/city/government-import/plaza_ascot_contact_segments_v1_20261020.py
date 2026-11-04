"""Finite same-face paths for all unresolved original terrain contact witnesses."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-contact-segments-v1-20261020';DOC=BASE/BATCH
CAP=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020';CONTACT=BASE/'government-xl-plaza-ascot-finite-ground-contacts-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,CONTACT]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 row=take(CAP,HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];t=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];targets=take(CONTACT,CONTACT/'literal-targets.json.gz')['rows'];out=[]
 for target in targets:
  start=np.asarray(target['rawWitness']['position']);choices=[]
  for contact in target['contactRows']:
   end=np.asarray([[float(Fraction(x)) for x in point] for point in contact['exactPoints']]).mean(0);face=t[contact['sourceFaceA']];normal=np.cross(face[1]-face[0],face[2]-face[0]);normal/=np.linalg.norm(normal)
   residual=max(float(np.linalg.norm(closest(p,face)-p)) for p in [start,end]);choices.append(dict(sourceFace=contact['sourceFaceA'],groundFace=contact['sourceFaceB'],end=end.tolist(),lengthM=float(np.linalg.norm(end-start)),residualM=residual,absoluteNormalY=float(abs(normal[1]))))
  assert choices;best=min(choices,key=lambda x:(x['residualM']>1e-8,x['lengthM']));out.append(dict(witness=target['rawWitness'],**best))
 save(DOC/'segments.json.gz',dict(rows=out,installationApproved=False));summary=dict(uids=[row['uid']],targets=len(out),finiteSameFaceSegments=sum(r['residualM']<=1e-8 for r in out),maximumResidualM=max(r['residualM'] for r in out),maximumLengthM=max(r['lengthM'] for r in out),maximumAbsoluteNormalY=max(r['absoluteNormalY'] for r in out),uniqueIncidentFaces=len({r['sourceFace'] for r in out}),installationApproved=False)
 save(DOC/'summary.json',summary);module('ascot_segments_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'finite-same-source-face-terrain-contact-paths',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
