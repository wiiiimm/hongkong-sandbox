"""Prepare guarded replacement of four legacy originals and nested regional terrain."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-qualified-publication-plan-v1-20261018';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;REVIEW=BASE/'government-xl-west-wing-source-review-v1-20261018';OLD=HERE/'local/government-xl-west-wing-browser-1280-v6-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();receipt=read(REVIEW/'result.json');refs=[Path(__file__),REVIEW/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 decision=read(REVIEW/'ROOT-SOURCE-REVIEW.json');assert decision['originalSourceReviewAccepted'];manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==decision['currentManifest'];before=read(manifest);after=copy.deepcopy(before);cat=read(OLD/'catalogue.json');sources=decision['sourceSHA256ByUid'];assert {m['uid']:m['sha256']for m in cat['models']}==sources;roster={r['uid']:r for r in read(REVIEW/'roster.json')['models']};edits=[];assets=[];allold=[];matched=[];retained=[]
 for e in cat['models']:
  uid=e['uid'];assert [d['uid']for d in e['supportDependencies']]==decision['supportDependencies'].get(uid,[])
  e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,originalSourceKey=roster[uid]['sourceKey'],sourceIdentityReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Complete unchanged government original at fixed1x placement; exact source-role identity and embedded-grade review, whole four-mode foundations/support, retained neighbours/exterior and desktop/mobile dependency, picking, collision and fallback checks.')
  for d in e['supportDependencies']:assert d['sha256']==sources[d['uid']];d['state']='installed'
  target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/e['asset'],target);assert digest(target.read_bytes())==e['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=4,catalogues=['catalogue.json']));shutil.copyfile(OLD/'source-forms.json',STAGE/'source-forms.json')
 url='city/data/official-models/'+BATCH+'/catalogue.json'
 for oldurl in before['officialModelCatalogues']:
  oldpath=ROOT/'3d-viewer'/oldurl;c=read(oldpath);allold.extend(c['models']);hits=[m for m in c['models']if m['uid']in sources]
  if not hits:continue
  for m in hits:assert m['sha256']==sources[m['uid']];matched.append(m['uid'])
  kept=[m for m in c['models']if m['uid']not in sources]
  if kept:
   replacement={**c,'models':kept,'counts':{**c['counts'],'packedModels':len(kept)}};dest=STAGE/'retained-catalogues'/(digest(oldurl.encode())+'.json');save(dest,replacement);edits.append(dict(destination=str(oldpath.relative_to(ROOT)),beforeSHA256=digest(oldpath.read_bytes()),source=ref(dest)));retained.append(dict(url=oldurl,source=str(dest.relative_to(ROOT)),originalSHA256=digest(oldpath.read_bytes())))
  else:after['officialModelCatalogues'].remove(oldurl)
 assert len(matched)==len(set(matched))==4 and set(matched)==set(sources);assert len(allold)==len({m['uid']for m in allold})
 after['officialModelCatalogues'].append(url);edits.append(dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')))
 for e in cat['models']:assets.append(dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+e['asset'],source=ref(STAGE/e['asset'])))
 candidate=decision['terrainCandidate'];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];terrainfile=STAGE/'government-regional-west-wing-original-v1-20261018.json';shutil.copyfile(ROOT/candidate['path'],terrainfile);terrain=dict(source=str(terrainfile.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+terrainfile.name,resolution=5,area='West Wing original assembly terrain',replaces=candidate['replaces'])
 pub=module('west_private_terrain_validator',HERE.parent/'island-detail-integration/publish.py');terrain_edits={};terrain_report={};pub.stage_top_level_terrain(dict(topLevelTerrainPatches=[terrain]),before,after,terrain_edits,terrain_report);pub.verify_inputs()
 for dest,raw in terrain_edits.items():
  assert not dest.exists();prepared=STAGE/'terrain-publication'/dest.name;prepared.parent.mkdir(parents=True,exist_ok=True);prepared.write_bytes(raw);edits.append(dict(destination=str(dest.relative_to(ROOT)),beforeSHA256=None,source=ref(prepared)))
 save(STAGE/'manifest.json',after);edits.append(dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=digest(manifest.read_bytes()),source=ref(STAGE/'manifest.json')))
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=BASE/'government-xl-nobhill-original-installed-v1-20261018/full-xl-current-count.json';delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId'])
 config=read(OLD/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[terrain],catalogueReplacements=retained,catalogueRemovals=[u for u in before['officialModelCatalogues']if u not in after['officialModelCatalogues']],viewportWidths=[1280,390]);save(STAGE/'browser-config.json',config);live={**config,'catalogueReplacements':[],'catalogueRemovals':[]};save(STAGE/'live-browser-config.json',live)
 for e in edits+assets:
  dest=ROOT/e['destination'];assert (digest(dest.read_bytes())if dest.exists()else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 save(DOC/'publication-plan.json',dict(edits=edits,assets=assets,sourceSHA256ByUid=sources,existingModelReverification=sorted(sources),newModels=[],newVisibleModels=0,newRuntimeCount=len(allold),delta=delta,previousXLCount=ref(previous),terrainReplacement=terrain,terrainValidation=terrain_report,currentManifest=ref(manifest),sourceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),publication=False))
 refs.extend([HERE.parent/'island-detail-integration/publish.py',previous,pointer,REVIEW/'ROOT-SOURCE-REVIEW.json',*[p for p in STAGE.rglob('*')if p.is_file()]]);result=module('west_publication_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-replacement-plan-with-terrain-validation',list(dict.fromkeys(refs)),dict(uids=list(sources),qualifiedForLiveVerification=True,publication=False,newVisibleModels=0,delta=delta));print(result['jobId'],flush=True)
if __name__=='__main__':main()
