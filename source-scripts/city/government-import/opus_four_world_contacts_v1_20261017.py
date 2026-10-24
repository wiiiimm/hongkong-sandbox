"""Revalidate saved Opus triangle contacts in original and actual renderer worlds."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-opus-actual-render-attributes-v2-20261017';CONTACT=BASE/'government-xl-opus-triangle-intersections-v1-20261017';BATCH='government-xl-opus-four-world-contacts-v1-20261017';DOC=BASE/BATCH

def weights(p,t):
 uv=np.linalg.lstsq(np.column_stack((t[1]-t[0],t[2]-t[0])),p-t[0],rcond=None)[0]
 return np.array([1-uv.sum(),*uv])

def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,CONTACT]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 # Validate exact consumed originals and current renderer capture, not old mutable map context.
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 inp=consume(CAP/'input.json.gz');captured=consume(CAP/'attributes.json.gz');saved=consume(CONTACT/'contacts.json.gz')['rows']
 for p,h in captured['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 worlds={'original':{r['uid']:decode_original_world_triangles((ROOT/r['path']).read_bytes()) for r in inp['rows']}}
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
  worlds[mode]={r['uid']:np.asarray(r[key]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in captured['rows']}
 results=[]
 for mode,world in worlds.items():
  rows=[]
  for row in saved:
   w=row['witness'];detail=dict(uid=row['uid'],originalPosition=row['position'],hasSavedWitness=w is not None,verified=False)
   if w:
    st=np.array(w['sourceTriangle']);sf=w['sourceFace'];target=world[row['uid']][sf];sp=world['landsd/248432:0'][w['supportFace']]
    pweights=weights(np.array(row['position']),st);qweights=weights(np.array(w['contact']),st);p=pweights@target;q=qweights@target
    normal=np.cross(target[1]-target[0],target[2]-target[0]);norm=np.linalg.norm(normal);normal=normal/norm if norm else normal
    source_distance=float(np.linalg.norm(closest(q,target)-q));support_distance=float(np.linalg.norm(closest(q,sp)-q));travel=float(np.linalg.norm(q-p))
    checks=dict(startInsideOriginalFace=bool(min(pweights)>=-1e-7),contactInsideOriginalFace=bool(min(qweights)>=-1e-7),sourceContactWithinOneMillimetre=source_distance<=.001,podiumContactWithinOneMillimetre=support_distance<=.001,travelWithinHalfMetre=travel<=.5,notBelowRim=bool(q[1]>=p[1]-.001),wallFace=bool(norm>0 and abs(normal[1])<=.1))
    detail.update(position=p.tolist(),contact=q.tolist(),sourceFace=sf,supportFace=w['supportFace'],podiumDistanceM=support_distance,travelM=travel,checks=checks,verified=all(checks.values()))
   rows.append(detail)
  results.append(dict(mode=mode,samples=len(rows),savedWitnesses=sum(x['hasSavedWitness'] for x in rows),verified=sum(x['verified'] for x in rows),rows=rows))
 DOC.mkdir();save(DOC/'contacts.json.gz',dict(rows=results,fullAcceptance=False,qualification='Saved contacts independently mapped on original source triangles, and checked against actual renderer-world podium faces. Two original missing witnesses retained; no strict-support or publication approval.'))
 save(DOC/'world-triangles.json.gz',{mode:{uid:t.tolist() for uid,t in world.items()} for mode,world in worlds.items()})
 summary=dict(rows=[{k:v for k,v in r.items() if k!='rows'} for r in results],fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 out=module('opus_four_contact_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-four-world-contact-revalidation-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in inp['rows']],**summary));print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()
