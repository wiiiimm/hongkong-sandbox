"""Bind eleven exact current original identities; no placement/publication approval."""
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pathlib import Path
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-identity-review-v1-20261021';DOC=BASE/BATCH
NAMES=dict(capture='government-xl-tko-grandiose-joint-capture-v1-20261021',neighbour='government-xl-tko-neighbour-identity-v1-20261021',tower3='government-xl-tko-tower3-identity-v1-20261021',popcorn='government-xl-tko-popcorn-identity-v1-20261021',tko='government-xl-tko-podium-identity-review-v1-20261021',grandiose='government-xl-grandiose-podium-identity-review-v1-20261021')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   d=BASE/n;r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(k,f):
  p=BASE/NAMES[k]/f;path=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][path];used[path]=pins[k][path];refs.append(p);return read(p)
 selected=take('capture','selection.json.gz')['rows'];assert len(selected)==11;out=[]
 for r in selected:
  uid=r['uid'];key=uid.split('/')[1];kind={'landsd/265489:0':'tko','landsd/246824:0':'grandiose','landsd/32147:0':'tower3','landsd/81731:0':'popcorn'}.get(uid,'neighbour')
  podium=kind in {'tko','grandiose'}
  p=take(kind,'ROOT-IDENTITY-REVIEW.json' if podium else key+'/identity.json')
  assert p['sourceSHA256']==r['sourceSHA256']
  if podium: assert p['uids']==[uid] and p['sourceIdentityAccepted'] and p['uniqueCurrentGeoRef']
  else: assert p['uid']==uid and p['passed']
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==r['source']['building'];refs.append(tile)
  out.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],sourceIdentityAccepted=True,reviewKind=kind,rawReasonsRetained=p.get('rawReasonsRetained',p.get('rawNativeIdentityReasons',[])),installationApproved=False))
 result=dict(uids=[r['uid']for r in selected],rows=out,identityOnlyApproved=True,publicationApproved=False,sourceGeometryChanges=0,aiGeometryModelling=False)
 save(DOC/'ROOT-IDENTITY-REVIEW.json',result)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('sol_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eleven-original-current-source-identity-binding',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
