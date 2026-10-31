"""Read-only current loader check of the exact PolyU original and reviewed terrain."""
from pathlib import Path
import shutil,subprocess
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-polyu-current-loader-validation-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/305582:0'
def main():
 assert not DOC.exists()and not LOCAL.exists();DOC.mkdir();LOCAL.mkdir()
 captured=read(BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/complete-current-actual-source-and-ground-305582-0.json.gz');entry=dict(captured['entry']);assert entry['uid']==UID and entry['triangles']==10536
 source=HERE/'local/government-xl-four-pending-original-inputs-20261007'/entry['asset'];assert digest(source.read_bytes())==entry['sha256'];dest=LOCAL/entry['asset'];dest.parent.mkdir();shutil.copyfile(source,dest)
 entry.update(priority='landmark',proceduralWindows=False,placementReviewed=False,publicationApproved=False,suppressesBuildingUids=[])
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',area='PolyU exact original current validation',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],counts=dict(packedModels=1),models=[entry]));save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']))
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');tile=next(t for t in manifest['tiles']if t['id']=='1_-2');tp=ROOT/'3d-viewer'/tile['url'];building=next(b for b in read(tp)['buildings']if b['uid']==UID)
 old=read(BASE/'government-xl-polyu-four-compatible-parent-current-production-v3-20261014/input.json.gz');assert building==next(b for b in old['exact25CurrentForms']if b['uid']==UID)
 save(LOCAL/'source-forms.json',[building]);save(LOCAL/'source-forms-lookup.json',{UID:dict(tile=tile['url'],tileSHA256=digest(tp.read_bytes()),building=building)})
 outcome=read(BASE/'government-xl-polyu-refined-candidate-metadata-validator-v1-20261014/unchanged-validator-outcome.json');assert outcome['passed']and outcome['allFieldsExceptSourceOverlapExactlyEqual'];candidate=outcome['metadataOnlyCandidate'];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];save(DOC/'terrain-candidates.json',[candidate])
 rel=lambda p:str(p.relative_to(ROOT));cmd=['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms-lookup.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')]
 with(DOC/'validation.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False));assert p.returncode==0
 r=read(DOC/'validation.json');print({k:r[k]for k in ['models','loaderAccepted','checksPassed','exceptions','concerns']},flush=True)
if __name__=='__main__':main()
