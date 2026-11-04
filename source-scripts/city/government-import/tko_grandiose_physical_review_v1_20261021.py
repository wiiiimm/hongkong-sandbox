"""Bounded original-assembly physical interpretation; no publication approval."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-physical-review-v1-20261021';DOC=BASE/BATCH
NAMES=dict(capture='government-xl-tko-grandiose-joint-capture-v1-20261021',ground='government-xl-tko-grandiose-ground-only-v1-20261021',contacts='government-xl-tko-grandiose-current-contacts-v2-20261021',attribution='government-xl-tko-grandiose-burial-attribution-v1-20261021',views='government-xl-tko-grandiose-roof-views-v2-20261021',runtime='government-xl-tko-grandiose-joint-runtime-v2-20261021',role='government-xl-tko-tower3a-facade-role-v1-20261021')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 for k,n in NAMES.items():
  _,pins[k]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
 def take(k,f):
  p=BASE/NAMES[k]/f;key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key];used[key]=pins[k][key];refs.append(p);return read(p)
 rows=take('capture','selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};assert len(sources)==11
 ground=take('ground','summary.json');assert ground['allTerrainChecksPassed'] and len(ground['rows'])==44
 for r in ground['rows']:assert r['passed'] and r['covered']==r['triangles'] and r['buried']==0
 ledger=take('contacts','ledger.json');assert ledger['currentContactInputsMatched'] and len(ledger['accounts'])==36
 for r in ledger['accounts']:assert r['sourceSHA256']==sources[r['uid']] and r['unaccountedContactWarnings']==0
 role=take('role','role-review.json');assert role['roleInterpretationAccepted'] and role['sourceSHA256']==sources['landsd/32024:0'] and not role['aiGeometryModelling']
 attr=take('attribution','summary.json');assert len(attr['rows'])==28;images=[];contexts=[]
 uids=sorted({r['uid']for r in attr['rows']});assert len(uids)==7
 for uid in uids:
  key=uid.split('/')[1];context=take('views',key+'-context.json');original=take('attribution','original/'+key+'.json.gz')
  assert context['flaggedFaceIds']==sorted(r['faceIndex']for r in original['results']['combined']['buriedFaces'])
  path=BASE/NAMES['views']/(key+'-with-podium.png');k=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins['views'][k];refs.append(path);images.append(dict(path=k,sha256=digest(path.read_bytes())))
  contexts.append(dict(uid=uid,exactOriginalFaceIds=context['flaggedFaceIds'],interpretation='Original lower facade/projecting or closure facets situated beneath elevated surfaces of the companion original podium. The highest-surface projection is not ground level here; preserve both source parts and their raw overlap flags.'))
 for r in attr['rows']:
  counts=r['counts'];assert counts['terrainOnly']['buried']==counts['terrainOnly']['uncovered']==0
  assert counts['podiumOnly']['buried']==counts['combined']['buried'] and counts['podiumOnly']['upward']==counts['combined']['upward'] and counts['combined']['uncovered']==0
  proof=take('attribution',r['mode']+'/'+r['uid'].split('/')[1]+'.json.gz');c=next(x for x in ledger['accounts']if x['uid']==r['uid']and x['mode']==r['mode'])
  assert proof['sourceWorldSHA256']==c['sourceWorldSHA256'] and proof['podiumWorldSHA256']==c['supportWorldSHA256']
  assert {x['faceIndex']for x in proof['results']['podiumOnly']['buriedFaces']}=={x['faceIndex']for x in proof['results']['combined']['buriedFaces']}
 runtime=take('runtime','metrics.json');assert len(runtime['rows'])==11
 for r in runtime['rows']:
  assert r['sourceSHA256']==sources[r['uid']] and r['sourcePreserved'] and not r.get('error') and r['missingTerrain']==0 and r['maxSamplerDelta']<=.004
  if r['uid']in ['landsd/265489:0','landsd/246824:0']:assert r['minSurfaceGap']>=-.5 and r['minLowGap']<=.1 and r['maxLowGap']<=1 and r['lowRimChecks']>0
 review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,terrainChecks=44,currentContactAccounts=36,sourceContexts=contexts,imagesActuallyViewed=images,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictFailuresRetained=True,installationApproved=False,publicationApproved=False,basis='Every original facet is covered and clear of actual terrain in four coordinate representations. All child support warnings are bound to exact finite contacts, bounded paths or the previously scoped Tower 3A facade attachments. The seven tower projection warnings reproduce entirely against the original podium, with identical flagged face sets, and do not occur against terrain. Four-angle source views show repeated lower facade projections/closure facets beneath elevated podium layers; these are reviewed as the unchanged original assembly, not as terrain burial. This does not certify structural engineering, assert that every source part is disjoint, or suppress the raw overlap records. Both terrain-founded podiums separately satisfy the existing ground-contact limits.',remainingIndependentChecks=['Complete source identity binding','Current neighbour acceptance binding','Whole assembly desktop/mobile image review','Runtime performance and budget acceptance','Guarded publication and live verification'])
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'acceptance-policy.py');module('joint_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-assembly-physical-interpretation',refs,review)
if __name__=='__main__':main()
