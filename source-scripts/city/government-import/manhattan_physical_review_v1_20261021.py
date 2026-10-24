"""Source-bound contact interpretation only; neighbours and publication independent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-physical-review-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-manhattan-'+v+'-20261021'for k,v in dict(capture='assembly-capture-v1',foundation='assembly-foundations-v1',contacts='assembly-contacts-v1',paths='remaining-paths-v1',browser='private-browser-v2',runtime='private-runtime-v3').items()}
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
 runtime=take('runtime','metrics.json');assert len(runtime['rows'])==1
 parent=runtime['rows'][0];assert parent['uid']=='landsd/276331:0' and parent['sourceSHA256']==next(r['sourceSHA256']for r in rows if r['uid']==parent['uid'])
 assert parent['sourcePreserved']and not parent.get('error')and parent['missingTerrain']==0 and parent['minSurfaceGap']>=-.5 and parent['minLowGap']>=-.5 and parent['maxLowGap']<=1 and parent['maxSamplerDelta']<=.004
 for path,h in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 browser=take('browser','1280/staged-browser.json');assert browser['passed']and not browser['errors'];images=[]
 for file in ['staged-local-joint-companion-original-join-1280.png','staged-landsd-276331-0-1280-1500.png']:
  p=BASE/NAMES['browser']/'1280'/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins['browser'][k];refs.append(p);images.append(dict(path=k,sha256=digest(p.read_bytes())))
 review=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},accounts=accounts,parentRuntime=parent,rawStrictFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publicationApproved=False,sourceSpecificPhysicalInterpretationAccepted=True,reviewer='Codex ROOT',imagesActuallyViewed=images,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,basis='All original facets have complete foundation coverage with no wholly buried or upward buried faces in four coordinate representations. Every companion strict-contact exception has a finite incident contact or a continuous original-face path within its endpoint-height bound. The terrain-supported podium separately passes the unchanged runtime ground policy; its support-interface warnings are preserved, not treated as companion engineering requirements. Viewed original join close-up shows the adjoining roof body; eastern overview shows podium frontage and surrounding terrain. The low-rim close-up is obstructed and is not used as clearance evidence. Numeric whole-source coverage supplies clearance evidence. No source geometry or pose changed.',remainingIndependentChecks=['Complete current neighbour interpretation','Whole assembly visual review','Mobile failure/retry review','Guarded live publication'])
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('yoho_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-specific-foundation-contact-and-runtime-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
