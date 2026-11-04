"""Source-bound contact interpretation only; neighbours and publication independent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-contact-accounting-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-manhattan-'+v+'-20261021'for k,v in dict(capture='assembly-capture-v1',foundation='assembly-foundations-v1',contacts='assembly-contacts-v1',paths='remaining-paths-v1').items()}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,name in NAMES.items():
   folder=BASE/name;r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[key]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(key,file):
  p=BASE/NAMES[key]/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[key][k];used[k]=pins[key][k];refs.append(p);return read(p)
 rows=take('capture','selection.json.gz')['rows'];accounts=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  for r in rows:
   uid=r['uid'];key=uid.split('/')[1];folder=mode+'/'+key+'/'
   f=take('foundation',folder+'foundation.json');assert f['triangles']==f['completeTerrainTriangles']==r['triangles']and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
   s=take('foundation',folder+'support.json.gz')['rows'][0]['proof'];failures=s['unresolved'];finite=0;paths=0
   if uid=='landsd/276331:0':
    accounts.append(dict(uid=uid,mode=mode,wholeFoundationTriangles=f['triangles'],rawUnresolved=len(failures),interpretation='Terrain-supported parent: actual runtime terrain-policy review remains independent.'))
    continue
   if failures:
    c=take('contacts',mode+'/'+key+'.json.gz');assert {tuple(x['position'])for x in failures}=={tuple(x['witness']['position'])for x in c['targets']};finite=sum(bool(x['positiveContacts'])for x in c['targets']);remaining=[x for x in c['targets']if not x['positiveContacts']]
    if remaining:
     p=take('paths',mode+'/'+key+'.json.gz');assert p['sourceWorldSHA256']==c['sourceWorldSHA256']and p['supportWorldSHA256']==c['podiumWorldSHA256'];assert {tuple(x['witness']['position'])for x in p['rows']}=={tuple(x['witness']['position'])for x in remaining}
     for x in p['rows']:
      v=x['verifiedPath'];assert v and v['maximumResidualM']<=.001 and v['withinEndpointHeight'] and v['maximumPathHeightM']<=v['endpointHeightCeilingM']+1e-9
     paths=len(p['rows'])
   assert finite+paths==len(failures)
   accounts.append(dict(uid=uid,mode=mode,samples=s['samples'],strictContacts=s['strictContacts'],wallIntersections=s['wallIntersections'],rawUnresolved=len(failures),finiteIncidentContacts=finite,finiteEndpointBoundedPaths=paths,remainingContactWarnings=0,wholeFoundationTriangles=f['triangles']))
 review=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},accounts=accounts,rawStrictFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publicationApproved=False,sourceSpecificPhysicalInterpretationAccepted=False,remainingIndependentChecks=['Parent actual-runtime terrain interpretation','Visual contact review','Complete neighbours','Final mobile retry and publication review'])
 save(DOC/'CONTACT-ACCOUNTING.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('yoho_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-foundation-and-finite-contact-accounting-only',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
