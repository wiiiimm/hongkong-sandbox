"""Source-bound contact interpretation only; neighbours and publication independent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-physical-review-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-siu-hong-'+v+'-20261021'for k,v in dict(capture='private-capture-v2',foundation='actual-foundations-v4',contacts='actual-contacts-v4',paths='actual-paths-v4',runtime='private-runtime-v4').items()}
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
   if failures:
    c=take('contacts',mode+'/'+key+'.json.gz');assert {tuple(x['position'])for x in failures}=={tuple(x['witness']['position'])for x in c['targets']};finite=sum(bool(x['positiveContacts'])for x in c['targets']);remaining=[x for x in c['targets']if not x['positiveContacts']]
    if remaining:
     p=take('paths',mode+'/'+key+'.json.gz');assert p['sourceWorldSHA256']==c['sourceWorldSHA256']and p['supportWorldSHA256']==c['podiumWorldSHA256'];assert {tuple(x['witness']['position'])for x in p['rows']}=={tuple(x['witness']['position'])for x in remaining}
     for x in p['rows']:
      v=x['verifiedPath'];assert v and v['maximumResidualM']<=.001 and v['withinEndpointHeight'] and v['maximumPathHeightM']<=v['endpointHeightCeilingM']+1e-9
     paths=len(p['rows'])
   assert finite+paths==len(failures)
   accounts.append(dict(uid=uid,mode=mode,samples=s['samples'],strictContacts=s['strictContacts'],wallIntersections=s['wallIntersections'],rawUnresolved=len(failures),finiteIncidentContacts=finite,finiteEndpointBoundedPaths=paths,remainingContactWarnings=0,wholeFoundationTriangles=f['triangles']))
 runtime=take('runtime','metrics.json');assert len(runtime['rows'])==2
 for row in runtime['rows']:
  assert not row.get('error') and row['missingTerrain']==0 and row['maxSamplerDelta']<=.004
 review=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},accounts=accounts,rawStrictFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publicationApproved=False,sourceSpecificPhysicalInterpretationAccepted=True,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,basis='Complete original facets checked against the actual drawn candidate terrain in four coordinate representations: no wholly buried or upward buried faces. Every raw support warning has a finite incident contact or a continuous original-face path within its own endpoint-height bound. Podium contacts are checked against actual drawn terrain, upper contacts against the unchanged original podium. Raw global ground gaps remain recorded; this is exact source-specific contact interpretation, not structural certification. No publication or visual approval is granted by this review.',remainingIndependentChecks=['Current exact source identity and two-form scope review','Neighbour review','Desktop and mobile visual acceptance and failure recovery','Guarded live publication'])
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('yoho_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-specific-foundation-contact-and-runtime-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
