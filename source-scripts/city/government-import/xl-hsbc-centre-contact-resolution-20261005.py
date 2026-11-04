"""Resolve HSBC Centre terrain from the already verified original source sheet."""
import importlib.util
import json
import subprocess
import sys
import uuid
from run import ROOT,HERE,read,save,digest,reservations

UID='landsd/265848:0'
BATCH='government-xl-hsbc-centre-contact-20261005'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PREVIOUS=ROOT/'docs/astra-city/government-import/government-xl-next-100-20261005'


def start():
    claim=reservations.claim('codex-hsbc-centre-contact-'+str(uuid.uuid4()),
        ['building:'+UID,'terrain-patch:'+UID,'building:landsd/229310:0',
         'terrain-surface:city/data/government-native-229310-0.json'],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)


def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))
    old=read(PREVIOUS/'check-selection.json.gz');row=next(r for r in old['rows'] if r['uid']==UID)
    fresh=LOCAL/'frozen-inputs'
    save(fresh/'check-selection.json.gz',{**old,'rows':[row],
        'previousSelectionSHA256':digest((PREVIOUS/'check-selection.json.gz').read_bytes()),
        'previousManifestSHA256':old['manifestSHA256'],
        'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())})
    context=next(r for r in read(PREVIOUS/'context.json.gz')['rows'] if r['uid']==UID)
    save(fresh/'context.json.gz',{'rows':[context]})
    spec=importlib.util.spec_from_file_location('hsbc_centre_contact',HERE/'xl-contact-resolution-20261005.py')
    resolution=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolution)
    resolution.BATCH=BATCH;resolution.BASE=fresh;resolution.DOC=DOC;resolution.LOCAL=LOCAL
    resolution.UIDS=[UID]
    resolution.RETAIN_NATIVE_URL='city/data/government-native-229310-0.json'
    resolution.owned()


if __name__=='__main__':owned() if 'owned' in sys.argv else start()
