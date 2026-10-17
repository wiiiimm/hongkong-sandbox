"""Exact unchanged Apex original stage with reviewed regional terrain replacement."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-apex227942-qualified-stage-v1-20261018';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/227942:0';SOURCES={UID:'83cc3270d1de801eace0d72a63dfc470df8e2862b8d6399f0422e0a4ceb8ed0c'}
def folder(n):return BASE/('government-xl-apex227942-'+n+'-20261018')
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
 old=HERE/'local'/folder('private-browser-v1').name;cat=read(old/'catalogue.json');assert len(cat['models'])==1;row=read(folder('original-terrain-capture-v3')/'selection.json.gz')['rows'][0];m=cat['models'][0];assert m['uid']==UID and m['sha256']==SOURCES[UID]and not m.get('supportDependencies')and not m.get('suppressesBuildingUids')
 m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,originalSourceKey=row['native']['cacheKey']+'/'+row.get('modelId',row['native']['model']['modelId']),sourceIdentityReview=ref(review/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(review/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original1x source; raw diagnostics resolved by exact source-specific sloping-ground contact and exact identity review, whole foundation and existing neighbour interfaces reviewed, desktop/mobile views verified.')
 dest=STAGE/m['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(old/m['asset'],dest);assert ref(dest)['sha256']==m['sha256'];save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));shutil.copyfile(old/'source-forms.json',STAGE/'source-forms.json')
 candidate=decision['terrainCandidate'];check(dict(path=candidate['path'],sha256=candidate['sha256']));terrain_file=STAGE/'government-regional-apex-original-v1-20261018.json';shutil.copyfile(ROOT/candidate['path'],terrain_file)
 terrain=dict(source=str(terrain_file.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+terrain_file.name,resolution=5,area='The Apex original terrain',replaces=candidate['replaces'])
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='The Apex unchanged original',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=[terrain]))
 config=read(old/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[terrain]);save(STAGE/'browser-config.json',config)
 save(DOC/'qualification.json',dict(privateStageQualified=True,sourceSHA256ByUid=SOURCES,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),sourceReviews=[ref(review/'ROOT-SOURCE-REVIEW.json')],noTerrainChange=False,terrainCandidate=terrain,retainedNeighbours=read(folder('retained-contacts-v1')/'summary.json'),publication=False))
 pub=module('yoho_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for e in pins.values():check(e)
 out=module('yoho_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex227942-qualified-original-stage-v1',[Path(__file__),review/'result.json',*[ROOT/p for p in pins],*[p for p in STAGE.rglob('*')if p.is_file()]],dict(uids=[UID],privateStageQualified=True,publisherDryRunPassed=True,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
