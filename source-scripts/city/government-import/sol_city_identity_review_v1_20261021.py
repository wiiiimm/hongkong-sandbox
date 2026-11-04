"""Bind five exact current original identities; no placement/publication approval."""
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pathlib import Path
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-identity-review-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-sol-city-'+v+'-20261021'for k,v in dict(capture='complete-capture-v1',neighbour='neighbour-identity-v1',current='current-identity-v1',tower3='tower3-identity-v1',podium='podium-identity-review-v1').items()}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   d=BASE/n;r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(k,f):
  p=BASE/NAMES[k]/f;path=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][path];used[path]=pins[k][path];refs.append(p);return read(p)
 selected=[r for r in take('capture','selection.json.gz')['rows']if r['uid']not in {'landsd/65157:0','landsd/76890:0'}];assert len(selected)==5;out=[]
 for r in selected:
  uid=r['uid'];key=uid.split('/')[1];kind='podium'if uid=='landsd/273271:0'else'tower3'if uid=='landsd/260034:0'else'current'if uid=='landsd/273080:0'else'neighbour'
  p=take(kind,key+'-review.json'if kind=='podium'else key+'/identity.json');assert p['uid']==uid and p['sourceSHA256']==r['sourceSHA256']
  assert (p['identityOnlyApproved']and p['identityReviewApproved'])if kind=='podium'else p['passed']
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==r['source']['building'];refs.append(tile)
  out.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],sourceIdentityAccepted=True,reviewKind=kind,rawReasonsRetained=p.get('rawReasonsRetained',p.get('rawNativeIdentityReasons',[])),installationApproved=False))
 result=dict(uids=[r['uid']for r in selected],rows=out,identityOnlyApproved=True,publicationApproved=False,sourceGeometryChanges=0,aiGeometryModelling=False)
 save(DOC/'ROOT-IDENTITY-REVIEW.json',result)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('sol_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-current-source-identity-binding',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
