"""Resolve Sun Yat Sen Sports Centre contact using exact source terrain only."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
import zipfile
from run import ROOT,HERE,read,save,digest,reservations
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import canonical_bytes,scan,acquire,_convert_one

UID='landsd/239367:0'
BATCH='government-xl-sun-yat-sen-contact-20261005'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PREVIOUS=ROOT/'docs/astra-city/government-import/government-xl-next-100-20261005'


def start():
    claim=reservations.claim('codex-sun-yat-sen-contact-'+str(uuid.uuid4()),
        ['building:'+UID,'terrain-patch:'+UID],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)


def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))
    old=read(PREVIOUS/'check-selection.json.gz');row=next(r for r in old['rows'] if r['uid']==UID)
    source=LOCAL/'sheets/11-SW-2D'
    pinned=read(HERE/'local/government-xl-contact-resolution-20261005/sun-yat-sen-source-directory.json')
    current,_=scan({'SHEETNO':'11-SW-2D','Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},source/'directory')
    current['models']=[m for m in current['models'] if m['modelId']==row['modelId']]
    assert len(current['models'])==1
    download=acquire(current,source/'directory/zip-directory.bin',source/'original',include_terrain=True)
    packed=source/'packed';packed.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source/'original/11-SW-2D.zip') as archive:
        converted=_convert_one(archive,archive.getinfo(row['native']['model']['sourceEntry']),source/'decoded',packed,{}, {'modelId':row['modelId']})
        raw=canonical_bytes((packed/converted['asset']['asset']).read_bytes(),row['sourceSHA256'])
        assert len(raw)==row['native']['model']['asset']['bytes']
        for e in download['entries']:
            if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):
                dest=source/'terrain'/e['name'];dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(archive.read(e['name']));assert digest(dest.read_bytes())==e['sha256']
    fresh=LOCAL/'frozen-inputs'
    save(fresh/'check-selection.json.gz',{**old,'rows':[row],
        'previousSelectionSHA256':digest((PREVIOUS/'check-selection.json.gz').read_bytes()),
        'previousManifestSHA256':old['manifestSHA256'],
        'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())})
    context=next(r for r in read(PREVIOUS/'context.json.gz')['rows'] if r['uid']==UID)
    save(fresh/'context.json.gz',{'rows':[context]})
    save(DOC/'source-recovery.json',{'modelId':row['modelId'],'sourceSHA256':row['sourceSHA256'],
        'exactOriginalSHARecreated':True,'sourceDirectorySHA256':current['directorySHA256'],
        'sourceArchiveSHA256':download['sha256'],'sourceDirectoryChanged':current['directorySHA256']!=pinned['directorySHA256'],
        'transferredBytes':download['newThisInvocationBytes'],'scriptExternalAICalls':0,'modelGeometryChanges':0})
    adjacent_sources=[]
    for sheet,pinned_adjacent in read(HERE/'local/government-xl-contact-resolution-20261005/sun-yat-sen-adjacent-directories.json').items():
        adjacent=LOCAL/'sheets'/sheet
        directory,_=scan({'SHEETNO':sheet,'Format_glTF':pinned_adjacent['sourceURL'],
            'REVISIONDATE':pinned_adjacent['revision']},adjacent/'directory')
        directory['models']=[]
        receipt=acquire(directory,adjacent/'directory/zip-directory.bin',adjacent/'original',include_terrain=True)
        with zipfile.ZipFile(adjacent/'original'/f'{sheet}.zip') as archive:
            for e in receipt['entries']:
                if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):
                    dest=adjacent/'terrain'/e['name'];dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes(archive.read(e['name']));assert digest(dest.read_bytes())==e['sha256']
        adjacent_sources.append(adjacent)
        save(DOC/('adjacent-source-'+sheet+'.json'),{'sheet':sheet,'directorySHA256':directory['directorySHA256'],
            'archiveSHA256':receipt['sha256'],'transferredBytes':receipt['newThisInvocationBytes'],
            'terrainFiles':[e for e in receipt['entries'] if e['name'].startswith('TERRAIN')],
            'modelGeometryChanges':0,'scriptExternalAICalls':0})
    spec=importlib.util.spec_from_file_location('sun_yat_sen_contact',HERE/'xl-contact-resolution-20261005.py')
    resolution=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolution)
    resolution.BATCH=BATCH;resolution.BASE=fresh;resolution.DOC=DOC;resolution.LOCAL=LOCAL
    resolution.SOURCE=source;resolution.UIDS=[UID]
    resolution.PARENT_URL='city/data/terrain-central-with-hullett.json';resolution.NESTED_PARENT=True
    resolution.ADJACENT_SOURCES=adjacent_sources
    resolution.owned()


if __name__=='__main__':owned() if 'owned' in sys.argv else start()
