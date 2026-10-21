"""Capture the two complete Hanford originals on current terrain, without publication."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hanford-pair-runtime-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/276187:0','landsd/203884:0']

def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))and not DOC.exists()
    refs=[Path(__file__)];rows=[]
    for name,uid in [('government-xl-remaining-forty-original-identity-v2-20261021',UIDS[0]),('government-xl-hanford-support-recovery-v2-20261021',UIDS[1])]:
        folder=BASE/name;_,pins=authenticate(folder);p=folder/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);row=next(r for r in read(p)['rows']if r['uid']==uid)
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[str(asset.relative_to(ROOT))];refs.append(asset)
        native=row['native']['model'];b=row['source']['building'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
        matches=[c for c in native['matching']['officialCandidates']if c['objectId']==b['objectId']and c['buildingCSUID']==b['buildingCSUID']];assert len(matches)==1
        entry=dict(matches[0],**native['asset'],uid=uid,modelId=row['modelId'],worldBounds=native['worldBounds'],triangles=row['triangles'],rootTranslation=[-834500,0,816500],recordedBaseHeight=b.get('baseHeightHKPD'),recordedTopHeight=b.get('topHeightHKPD'),placementReviewed=False,publicationApproved=False)
        dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());row['candidate']=dict(path=str(dest.relative_to(ROOT)),entry=entry);rows.append(row);refs.append(dest)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=mh))
    tool=HERE/'acceptance-metrics-multi-retained.mjs';cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
    with(DOC/'worker.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==2 and digest(manifest.read_bytes())==mh
    for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    refs.extend([tool,LOCAL/'runtime-geometry.json.gz'])
    assert reservations.owns(read(LOCAL/'reservation.json'))
    result=dict(uids=UIDS,rows=metrics['rows'],sourceGeometryChanges=0,installationApproved=False)
    module('hanford_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-current-runtime',list(dict.fromkeys(refs)),result)

def main():
    if '--owned'in sys.argv:return owned()
    assert not DOC.exists()and not LOCAL.exists()
    c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(p),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
