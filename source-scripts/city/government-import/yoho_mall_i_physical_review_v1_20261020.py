"""Source-bound contact interpretation only; neighbours and publication independent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-physical-review-v1-20261020';DOC=BASE/BATCH
NAMES={k:'government-xl-yoho-mall-i-'+v+'-20261020'for k,v in dict(capture='assembly-capture-v1',foundation='assembly-foundations-v1',contacts='assembly-contacts-v1',paths='remaining-paths-v1',browser='private-browser-v2').items()}
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
 browser=take('browser','1280/staged-browser.json');assert browser['passed']and not browser['errors'];views={v['id']:v for v in browser['localJointViews']};images=[]
 for name in ['tower8-lower-body','mall-low-rim']:
  v=views[name];p=BASE/NAMES['browser']/'1280'/v['file'];k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins['browser'][k];refs.append(p);images.append(dict(path=k,sha256=digest(p.read_bytes())))
 review=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},sourceSpecificPhysicalInterpretationAccepted=True,scope='Whole-source foundation coverage and original source-to-podium/terrain contact interpretation only.',accounts=accounts,reviewer='Codex ROOT',imagesActuallyViewed=images,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,remainingIndependentChecks=['Complete current neighbour interpretation','Retained-source acceptance applicability','Foreign BASIC collision interpretation','Whole assembly visual review and guarded live publication'],basis='Every original facet has terrain/podium foundation coverage without wholly buried or upward buried faces. Every strict low-rim exception has either a positive finite incident contact or a continuous finite source-face path to a positive contact within its own endpoint height in all four coordinate representations. The actual close-up views show the Tower 8 lower body adjoining the podium and the mall lower facade meeting terrain. These are authored source joins, not engineering or per-component structural claims. All original parts, raw warnings and exact pose remain unchanged.')
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 module('yoho_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-specific-complete-foundation-and-contact-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
