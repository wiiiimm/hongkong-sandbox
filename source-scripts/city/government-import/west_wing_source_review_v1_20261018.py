"""Compose complete unchanged four-source acceptance; publication remains separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-source-review-v1-20261018';DOC=BASE/BATCH
NAMES=['identity-review-v1','cgo-identity-review-v1','companion-extent-review-v1','small-identity-review-v1','grade-role-review-v2','runtime-foundations-v2','runtime-support-v2','runtime-wall-paths-v1','exterior-capture-v2','runtime-checks-v3','native-scope-v2','nested-terrain-v2','standard-validation-v2','browser-1280-v6','browser-390-v5','fallback-390-v2']
def folder(n):return BASE/('government-xl-west-wing-'+n+'-20261018')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=folder(name)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def checked(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p;refs.append(p);return read(p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 cap=folder('runtime-checks-v3');selection=checked(cap/'selection.json.gz');rows=selection['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};assert len(rows)==len(sources)==4
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 identities={'landsd/26195:0':folder('identity-review-v1')/'ROOT-IDENTITY-REVIEW.json','landsd/322270:0':folder('cgo-identity-review-v1')/'ROOT-IDENTITY-REVIEW.json','landsd/315069:0':folder('companion-extent-review-v1')/'315069:0.json','landsd/319534:0':folder('small-identity-review-v1')/'ROOT-IDENTITY-REVIEW.json'};roster=[]
 for r in rows:
  uid=r['uid'];identity=checked(identities[uid]);assert identity['uid']==uid and identity['sourceSHA256']==sources[uid];assert identity.get('identityAccepted',identity.get('passed')) and not identity.get('reasons',[])
  assert digest((ROOT/r['candidate']['path']).read_bytes())==sources[uid]==r['candidate']['entry']['sha256'];refs.append(ROOT/r['candidate']['path']);assert r['source']['building']in checked(ROOT/'3d-viewer'/r['source']['tile'])['buildings']
  modelid=r['candidate']['entry']['modelId'];roster.append(dict(uid=uid,sourceSHA256=sources[uid],modelId=modelid,sourceKey='828133bbea286a52de1484a5163766bfab7ee42b0b4c07a8be3e756f0cabe7e6/'+modelid,buildingCSUID=r['candidate']['entry']['buildingCSUID'],identityAccepted=True,identityEvidence=ref(identities[uid])))
 west=checked(identities['landsd/26195:0']);assert west['manifestSHA256']==selection['manifestSHA256'] and west['sourceSHA256ByUid']==sources
 gradepath=folder('grade-role-review-v2')/'ROOT-GRADE-REVIEW.json';grade=checked(gradepath);assert grade['gradeSourceRoleAccepted'] and grade['embeddedRimPaths']==100 and grade['rawContactFailuresPreserved']
 assert {(x['uid'],x['mode'])for x in grade['gradeEvidence']}=={(u,m)for u in sources for m in ['original','literal','left','balanced']}
 for x in grade['gradeEvidence']:assert x['sourceSHA256']==sources[x['uid']]
 foundations=checked(folder('runtime-foundations-v2')/'summary.json');after=[r for r in foundations['rows']if r['stage']=='after'];assert foundations['allAfterPassed'] and len(after)==16 and all(r['passed']and r['covered']==r['faces']and r['buried']==r['upwardBuried']==0 for r in after)
 support=checked(folder('runtime-support-v2')/'checks.json.gz')['rows'];assert len(support)==16
 for r in support:
  assert r['supportUids']==(['landsd/26195:0']if r['uid']=='landsd/322270:0'else[])
  if r['uid']in ['landsd/322270:0','landsd/319534:0']:assert r['interface']['passed']and not r['unresolved']
 exterior=read(folder('exterior-capture-v2')/'result.json');assert exterior['strictExteriorUnchanged']
 scope=checked(folder('native-scope-v2')/'scope.json');native=checked(cap/'native-neighbour-checks.json');nativeby={r['uid']:r for r in native['rows']};assert set(nativeby)==set(scope['touchingNativeUids'])-set(sources) and len(nativeby)==9 and all(r['passed']for r in nativeby.values())
 for r in checked(cap/'neighbour-checks.json')['rows']:
  assert not r['reasons']or(r['reasons']==['existing-native-neighbour-requires-full-mesh-check']and r['uid']in nativeby and nativeby[r['uid']]['passed'])
 val=checked(folder('standard-validation-v2')/'validation.json');assert val['loaderAccepted']==val['checksPassed']==4 and val['exceptions']==0
 candidate=checked(cap/'terrain-candidates.json')[0];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];refs.append(ROOT/candidate['path']);assert candidate['bounds']==scope['changedParentExtent'];proof=checked(folder('nested-terrain-v2')/'retained-parent-proof.json');assert proof['gridAndChildCoordinatesAndIndicesUnchanged']and proof['sourceOutsideRegionRetainsExistingTerrain']and len(proof['retainedChildren'])==12
 deps={'landsd/322270:0':['landsd/26195:0']};browsers=[]
 for width in [1280,390]:
  name=f'browser-{width}-v{6 if width==1280 else 5}';path=folder(name)/'staged-browser.json';report=checked(path);assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==8 and {(v['uid'],v['time'])for v in views}=={(u,t)for u in sources for t in ['15:00','22:00']}
  cat=checked(HERE/'local'/folder(name).name/'catalogue.json');assert {m['uid']:[d['uid']for d in m['supportDependencies']]for m in cat['models']}=={u:deps.get(u,[])for u in sources}
  for v in views:assert v['sourceSHA256']==sources[v['uid']]and v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']
  assert len(report['retainedNativeOwnViews'])==18 and {r['uid']for r in report['retainedNativeOwnViews']}==set(nativeby);browsers.append(ref(path))
 fallbackpath=folder('fallback-390-v2')/'staged-browser.json';fallback=checked(fallbackpath);assert fallback['passed']and not fallback['errors'];failed=[v for v in fallback['views']if v.get('phase')=='failed-download'];assert len(failed)==4 and {v['uid']for v in failed}==set(sources)and all(v['fallbackRetained']and v['fallbackFaces']>0 for v in failed)
 save(DOC/'roster.json',dict(models=roster));save(DOC/'ROOT-SOURCE-REVIEW.json',dict(uids=list(sources),originalSourceReviewAccepted=True,sourceSHA256ByUid=sources,identityRoster=ref(DOC/'roster.json'),supportDependencies=deps,requiredAssemblyOriginals=west['requiredAssemblyOriginals'],terrainCandidate=candidate,browserEvidence=browsers,fallbackEvidence=ref(fallbackpath),sourceSpecificReviewEvidence=[ref(gradepath),*[ref(p)for p in identities.values()]],currentManifest=ref(manifest),rawDiagnosticsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,reviewer='Codex ROOT',limitations=['Exact source-specific acceptance; no engineering certification or global threshold changes.','Mobile/desktop v5 retains selection for normal loader residency; prior desktop v3 establishes unselected solid appearance. Mobile controls and selection outlines obscure part of the view; no physical-device performance claim.','Publication and live verification remain required.']))
 refs.extend(ROOT/p for p in pins);out=module('west_final_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-unchanged-original-source-acceptance-v1',list(dict.fromkeys(refs)),dict(uids=list(sources),originalSourceReviewAccepted=True,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
