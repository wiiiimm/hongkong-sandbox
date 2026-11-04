"""Preview an unapproved unchanged original; never grants physical/publication approval."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json'
    receipt,pins=authenticate(base/a.runtime);selectionpath=base/a.runtime/'selection.json.gz';assert digest(selectionpath.read_bytes())==pins[str(selectionpath.relative_to(ROOT))];selection=read(selectionpath);row=next(r for r in selection['rows']if r['uid']==a.uid)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']
    if not a.owned:
        assert not doc.exists()and not local.exists();claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),['building:'+a.uid],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(leasepath,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(leasepath),sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(leasepath);assert reservations.owns(lease)and not doc.exists();doc.mkdir();refs=[Path(__file__),base/a.runtime/'result.json',selectionpath,manifest]
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==a.uid)==row['source']['building'];refs.append(tile)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');native=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(row['native']['cacheKey'],)).fetchone()
    assert native and native[1]==row['native']['resultSha']
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);entry=copy.deepcopy(row['candidate']['entry']);entry.update(sourceTile=native[0],priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
    entry['asset']='assets/'+row['sourceSHA256']+'.glb.gz';dest=local/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes())
    save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',diagnosticOnly=True,physicalAcceptance=False,publicationApproved=False,datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)))
    save(local/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(local/'source-forms.json',[row['source']['building']]);save(local/'validation-forms.json',{a.uid:row['source']})
    config=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',terrain=[],browserUids=[a.uid],fitBox=True,captureDirectionByModel={a.uid:[1,.65,-1]},retainedBuildingUids=[],jointUids=[a.uid],nativeSupportUidsByModel={},viewportWidths=[1280],failureTestUids=[],doc=str(doc.relative_to(ROOT))+'/')
    configpath=local/'browser-config.json';save(configpath,config);tool=HERE/'ronsdale_three_live_browser_v4_20261022.mjs';refs.append(tool)
    with(doc/'preflight.log').open('w')as log:subprocess.run(['node',str(tool),'preflight',str(configpath.relative_to(ROOT)),str((local/'source-forms.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert reservations.owns(lease)
    with(doc/'browser.log').open('w')as log:subprocess.run(['node',str(tool),'staged',str(configpath.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200,check=True)
    report=read(doc/'staged-browser.json');assert report['passed']and not report['errors']
    assert digest(manifest.read_bytes())==selection['manifestSHA256']and reservations.owns(lease)
    refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],diagnosticOnly=True,visualAcceptance=False,physicalAcceptance=False,architectureReview=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,scriptExternalAICalls=0,qualification='Actual unapproved original in unchanged current viewer scene, for source/incident-face review only. No architectural-role, source identity, contact, physical or publication approval.')
    module('original_diagnostic_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-original-current-scene-desktop-diagnostic-exports',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
