"""Bind complete raw support accounts and scoped authored-facade attachment evidence."""
from pathlib import Path
import json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-physical-review-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-sol-city-'+v+'-20261021' for k,v in dict(capture='complete-capture-v1',foundation='five-foundations-v1',runtime='five-runtime-v1',renderContacts='rendered-tower-contacts-v1',renderPaths='rendered-tower-paths-v2',renderFacade='rendered-facade-paths-v2',originalFacade='original-facade-paths-v1',oldContacts='original-contacts-v1',oldPaths='original-paths-v3',newContacts='additional-tower-contacts-v1',newPaths='additional-tower-paths-v3',role2='tower2-facade-role-v1',role5='tower5-facade-role-v1').items()}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   d=BASE/n;r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(k,f):
  p=BASE/NAMES[k]/f;key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key];used[key]=pins[k][key];refs.append(p);return read(p)
 def witnesses(rows,key):return sorted(json.dumps(r[key],sort_keys=True)for r in rows)
 rows=[r for r in take('capture','selection.json.gz')['rows']if r['uid']not in {'landsd/65157:0','landsd/76890:0'}];assert len(rows)==5;accounts=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  for r in rows:
   uid=r['uid'];key=uid.split('/')[1];folder=mode+'/'+key+'/'
   f=take('foundation',folder+'foundation.json');assert f['triangles']==f['completeTerrainTriangles']==r['triangles'] and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
   inp=take('foundation',folder+'input.json.gz');raw=inp['rows'][0];assert raw['uid']==uid
   tri=np.asarray(raw['position']).reshape(-1,3)[np.asarray(raw['index']).reshape(-1,3)];support=np.asarray(inp['podium']).reshape(-1,3,3)
   s=take('foundation',folder+'support.json.gz')['rows'][0]['proof'];assert s['wallIntersections']==len(s['resolved']) and s['strictContacts']+s['wallIntersections']+len(s['unresolved'])==s['samples']
   assert s['strictContacts']>0 and s['maximumEmbeddingM']<=.5
   for wall in s['resolved']:assert wall['sourceWallFaces'] and wall['supportFaces'] and wall['contactGapM']==0 and -wall['gap']<=s['maximumEmbeddingM']
   failures=s['unresolved'];finite=bounded=facade=0
   if failures:
    ck,pk=('renderContacts','renderPaths')if mode!='original'else(('newContacts','newPaths')if uid in {'landsd/251569:0','landsd/268424:0'}else('oldContacts','oldPaths'))
    c=take(ck,mode+'/'+key+'.json.gz');assert digest(tri.tobytes())==c['sourceWorldSHA256'] and digest(support.tobytes())==c['podiumWorldSHA256']
    assert sorted(json.dumps(x,sort_keys=True)for x in failures)==witnesses(c['targets'],'witness')
    finite=sum(bool(x['positiveContacts'])for x in c['targets']);remaining=[x for x in c['targets']if not x['positiveContacts']]
    p=take(pk,mode+'/'+key+'.json.gz');assert p['sourceWorldSHA256']==c['sourceWorldSHA256'] and p['supportWorldSHA256']==c['podiumWorldSHA256'];assert witnesses(p['rows'],'witness')==witnesses(remaining,'witness')
    for x in p['rows']:
     v=x['verifiedPath']
     if v:assert v['maximumResidualM']<=.001 and v['withinEndpointHeight'] and v['maximumPathHeightM']<=v['endpointHeightCeilingM']+1e-9;bounded+=1
    residual=[x for x in p['rows']if not x['verifiedPath']]
    if residual:
     assert uid in {'landsd/268424:0','landsd/273080:0'}
     role=take('role5'if uid=='landsd/268424:0'else'role2','role-review.json');assert role['roleInterpretationAccepted'] and role['sourceSHA256']==r['sourceSHA256']
     a=take('originalFacade'if mode=='original'else'renderFacade',mode+'/'+key+'.json.gz');assert a['sourceWorldSHA256']==c['sourceWorldSHA256'] and a['supportWorldSHA256']==c['podiumWorldSHA256'];assert witnesses(a['rows'],'witness')==witnesses(residual,'witness')
     for x in a['rows']:
      v=x['verifiedAttachmentPath'];assert v and v['maximumResidualM']<=.001 and x['rawBoundedPathFailureRetained'];assert set(x['incidentFaces'])<=set(role['exactIncidentFaceIds']);assert v['contact']['dimension']>0 and v['contact']['sourcePrimitiveDimensionA']==v['contact']['sourcePrimitiveDimensionB']==2
     facade=len(a['rows'])
   assert finite+bounded+facade==len(failures)
   accounts.append(dict(uid=uid,mode=mode,samples=s['samples'],strictContacts=s['strictContacts'],existingPolicyWallContacts=s['wallIntersections'],rawUnresolved=len(failures),finiteIncidentContacts=finite,finiteEndpointBoundedPaths=bounded,reviewedFacadeAttachmentPaths=facade,remainingUninterpretedWarnings=0,wholeFoundationTriangles=f['triangles']))
 runtime=take('runtime','metrics.json');assert {r['uid']for r in runtime['rows']}=={r['uid']for r in rows}
 for row in runtime['rows']:assert not row.get('error') and row['missingTerrain']==0 and row['maxSamplerDelta']<=.004
 review=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},accounts=accounts,rawStrictFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publicationApproved=False,sourceSpecificPhysicalInterpretationAccepted=True,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,basis='Every complete original source checked against actual candidate terrain/support in four coordinate representations. Existing exact wall-interface contacts retained. All other raw warnings have finite incident contacts, endpoint-bounded continuous paths, or individually reviewed facade-face attachment paths. The latter retain failed endpoint bounds and apply only to the exact reviewed faces. No generic support threshold changed; no structural certification. Independent identity, neighbours and browser/publication acceptance still required.')
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('sol_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-source-specific-physical-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
