"""Freeze exact private fixture and honest failed legacy harness receipts."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from peninsula_private_group_roof_contract_v2_20261029 import apply
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-group-roof-private-fixture-v1-20261029'
def main():
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    old='government-xl-peninsula-pair-retained-roof-private-browser-v1-20261029';prior=HERE/'local'/old;cat=take(old,prior/'catalogue.json');reviewname='government-xl-peninsula-private-group-roof-review-v1-20261029';review=take(reviewname,BASE/reviewname/'ROOT-PRIVATE-EXPERIMENT-REVIEW.json');scope='government-xl-peninsula-pair-current-v1-20261029-model-scope';forms={r['building']['uid']:r['building']for r in take(scope,BASE/scope/'270876:0-forms.json.gz')}
    cat['models']=apply(cat['models'],forms,review);out.mkdir();local.mkdir(parents=True)
    for model in cat['models']:
        p=prior/model['asset'];assert digest(p.read_bytes())==model['sha256'];refs.append(p);dest=local/model['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    save(local/'catalogue.json',cat)
    for file in ['source-forms.json','validation-forms.json']:
        p=prior/file;take(old,p);shutil.copyfile(p,local/file)
    cfg=take(old,prior/'browser-config-390.json');cfg.update(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',failureTestUids=[]);save(local/'browser-config-390.json',cfg)
    failures=[]
    for n,reason in [('government-xl-peninsula-pair-group-roof-private-browser-v2-20261029','Unchanged catalogue schema rejects OSM way suppressions; exact runtime binding added and61tests passed afterwards.'),('government-xl-peninsula-pair-group-roof-private-browser-v3-20261029','Desktop group/roof preview passed. Mobile legacy independent-source retry permits only one of two intentionally denied peers, so an atomic group correctly remains on BASIC; per-peer fresh-context lifecycle required.')]:
        d=BASE/n;assert not(d/'result.json').exists();entry=dict(batch=n,reason=reason,installationCredit=0,permanentSourceRejection=False)
        for p in d.rglob('*'):
            if p.is_file():refs.append(p)
        for width in [1280,390]:
            p=d/('command-'+str(width)+'.json')
            if p.exists():entry[str(width)]=read(p)
        failures.append(entry)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==review['currentManifest']['sha256'];refs.append(manifest)
    files=['3d-viewer/city/official-model-reviewed-osm-roof.js','3d-viewer/city/official-model-assets.js','3d-viewer/city/streaming.js','3d-viewer/city/official-models.js','3d-viewer/city/app.js','3d-viewer/city.html'];refs.extend(ROOT/f for f in files)
    result=dict(uids=[m['uid']for m in cat['models']],sourceSHA256ByUid={m['uid']:m['sha256']for m in cat['models']},previewOnly=True,privateFixtureOnly=True,failedLegacyHarnesses=failures,terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Exact reviewed pair, source-bound roof declaration and original asset bytes prepared privately; all approval flags false. Both failed legacy harness runs preserved verbatim, neither a source corruption nor installation credit. Current-code private browser and complete per-peer atomic/roof lifecycle remain mandatory.')
    save(out/'summary.json',result);refs.extend(p for p in local.rglob('*')if p.is_file());refs.extend([HERE/'peninsula_private_group_roof_contract_v1_20261029.py',HERE/'peninsula_private_group_roof_contract_v2_20261029.py']);module('peninsula_private_fixture',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-private-original-pair-roof-fixture-and-preserved-legacy-harness-failures',refs,result)
if __name__=='__main__':main()
