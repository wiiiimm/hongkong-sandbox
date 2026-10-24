"""Exact unchanged Apex original stage with reviewed regional terrain replacement."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-royal-green3-qualified-stage-v2-20261018';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/11093:0';SOURCES={UID:'99a6f4988219a941b614c8575a4d8fcc8746ce717a99a102e76ffcd80d1b5975'}
def folder(n):return BASE/('government-xl-royal-green3-'+n+'-20261018')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
 assert not DOC.exists()and not STAGE.exists();review=folder('source-review-v1');r=read(review/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e;pins[e['path']]=e
 for e in pins.values():check(e)
 decision=read(review/'ROOT-SOURCE-REVIEW.json');assert decision['originalSourceReviewAccepted']and decision['policyReasons']==[]and decision['sourceSHA256']==SOURCES[UID]
 old=HERE/'local'/folder('private-browser-v2').name;cat=read(old/'catalogue.json');assert len(cat['models'])==1;row=read((BASE/'government-xl-royal-green3-retained-terrain-v1-20261017')/'selection.json.gz')['rows'][0];m=cat['models'][0];assert m['uid']==UID and m['sha256']==SOURCES[UID]and not m.get('supportDependencies')and not m.get('suppressesBuildingUids')
 m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,originalSourceKey=row['native']['cacheKey']+'/'+row.get('modelId',row['native']['model']['modelId']),sourceIdentityReview=ref(review/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(review/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original1x source; raw diagnostics resolved by exact source-specific lower-wall sloping-ground interface and exact identity review, whole foundation and existing neighbour interfaces reviewed, desktop/mobile views verified.')
 dest=STAGE/m['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(old/m['asset'],dest);assert ref(dest)['sha256']==m['sha256'];save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));shutil.copyfile(old/'source-forms.json',STAGE/'source-forms.json')
 candidate=decision['terrainCandidate'];check(dict(path=candidate['path'],sha256=candidate['sha256']));terrain_file=STAGE/'government-royal-green3-original-v1-20261018.json';shutil.copyfile(ROOT/candidate['path'],terrain_file)
 terrain=dict(source=str(terrain_file.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+terrain_file.name,resolution=5,area='Royal Green Tower 3 original terrain',replacesMany=candidate['replacesMany'])
 patch=read(ROOT/candidate['path']);fullcheck=folder('current-neighbours-v1')/'native-neighbour-checks.json';native=read(fullcheck);assert set(r['uid']for r in native['rows']if r['passed'])>=set(u for r in candidate['replacesMany']for u in r['retainedUids'])
 for i,replacement in enumerate(terrain['replacesMany']):
  native_decision=dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=candidate['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(fullcheck),qualification='Exact scripted full-mesh checks of retained unchanged originals; all ten whole-parent nominated actors checked.')
  rp=DOC/('native-replacement-review-'+str(i)+'.json');save(rp,native_decision);replacement['nativeReview']=ref(rp)
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Royal Green Tower 3 unchanged original',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=[terrain]))
 config=read(old/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[terrain]);save(STAGE/'browser-config.json',config)
 save(DOC/'qualification.json',dict(privateStageQualified=True,sourceSHA256ByUid=SOURCES,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),sourceReviews=[ref(review/'ROOT-SOURCE-REVIEW.json')],noTerrainChange=False,terrainCandidate=terrain,retainedNeighbours=read(folder('current-neighbours-v1')/'summary.json'),publication=False))
 pub=module('yoho_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';adapter=module('royal_multi_native_adapter',HERE/'reviewed_multi_native_terrain_publication_20261009.py');original_stage=pub.stage_top_level_terrain;pub.stage_top_level_terrain=lambda plan,original,manifest,edits,report:adapter.stage_top_level(pub,plan,original,manifest,edits,report,original_stage);sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for e in pins.values():check(e)
 out=module('yoho_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'royal-green3-qualified-original-stage-v1',[Path(__file__),HERE/'reviewed_multi_native_terrain_publication_20261009.py',review/'result.json',*[ROOT/p for p in pins],*[p for p in STAGE.rglob('*')if p.is_file()]],dict(uids=[UID],privateStageQualified=True,publisherDryRunPassed=True,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
