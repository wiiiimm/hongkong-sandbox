"""Bind original tower sources whose existing basic podium contacts passed; unapproved."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-two-basic-supported-original-selection-v1-20261023';out=base/batch;assert not out.exists()
    prior='government-xl-remaining-current-basic-podium-contacts-v1-20261023';receipt,pins=authenticate(base/prior);refs=[Path(__file__),base/prior/'result.json']
    def take(name):
        p=base/prior/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    inputs=take('input.json.gz');report=take('checks.json.gz');positive=[r for r in report['rows']if r['usableBasicSupportDiagnostic']]
    assert {r['uid']for r in positive}=={'landsd/312858:0','landsd/6801:0'}
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);assert digest(manifestpath.read_bytes())==inputs['manifestSHA256'];refs.append(manifestpath)
    forbidden={u for r in positive for u in [r['uid'],r['supportUid']]}
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;models=read(p)['models'];assert not forbidden&{m['uid']for m in models};assert not forbidden&{u for m in models for u in m.get('suppressesBuildingUids',[])};refs.append(p)
    sourcebyuid={r['uid']:r for r in inputs['rows']};rows=[];bindings=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for checked in positive:
            r=sourcebyuid[checked['uid']];source=deepcopy(r['source']);assert source['sourceSHA256']==checked['sourceSHA256']
            p=ROOT/source['candidate']['path'];assert digest(p.read_bytes())==source['sourceSHA256'];refs.append(p)
            for form in [source['source'],r['supportForm']]:
                p=ROOT/'3d-viewer'/form['tile'];assert digest(p.read_bytes())==form['tileSHA256'];assert[form['building']]==[f for f in read(p)['buildings']if f['uid']==form['building']['uid']];refs.append(p)
            native=source['native'];record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert record and record[0]==native['resultSha'];assert next(m for m in record[1]['models']if m['modelId']==source['modelId'])==native['model']
            for flag in ['publicationApproved','placementReviewed','sourceIdentityReviewed','identityReviewApproved']:assert not source['candidate']['entry'].get(flag)
            rows.append(source);bindings.append(dict(uid=r['uid'],supportUid=r['supportUid'],supportForm=r['supportForm'],supportFormSHA256=digest(__import__('json').dumps(r['supportForm']['building'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),supportGeometrySHA256=checked['supportGeometrySHA256'],sourceSHA256=source['sourceSHA256'],basicIsCurrentFinalSupport=True,supportApproved=False))
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=inputs['manifestSHA256']));save(out/'support-bindings.json',bindings)
    result=dict(uids=[r['uid']for r in rows],sources=2,retainedBasicSupportUids=[r['supportUid']for r in bindings],sourceGeometryChanges=0,installationApproved=False,publication=False,status='unapproved-two-current-basic-supported-originals',qualification='Exact original sources/current records and currently rendered basic supports are bound after canonical contact diagnostics. Basic podiums must remain unchanged/visible; all-world support, whole-source clearance, collision, current-scene and browser acceptance remain required. No native podium import, terrain edit or support approval.')
    save(out/'summary.json',result);module('two_basic_supported_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-two-originals-retaining-basic-podiums-selection',refs,result);print(dict(sources=2),flush=True)

if __name__=='__main__':main()
