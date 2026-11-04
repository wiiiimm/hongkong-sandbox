"""Fresh original Citywalk versus actual current ground; no installation or geometry edits."""
from pathlib import Path
import subprocess,sys,json,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-current-foundation-v2-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-citywalk-saved294-source-layer-attribution-v1-20261014/input.json.gz'
JS=HERE/'citywalk_current_ground_capture_v1_20261015.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    if '--owned' not in sys.argv:
        assert not DOC.exists() and not LOCAL.exists()
        claim=reservations.claim('citywalk-foundation-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
        lease=claim['reservation'];save(LOCAL/'lease.json',json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'lease.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    packet=read(SRC);v=np.asarray(packet['sourceWorlds'][0]['position']).reshape(-1,3)
    DOC.mkdir();save(DOC/'plan.json',dict(uid='landsd/134332:0',sourceInput=ref(SRC),expectedManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256'],providerOriginalFaceBounds=[v.min(axis=0).tolist(),v.max(axis=0).tolist()],evidenceRefs=[ref(SRC),ref(JS)]))
    subprocess.run(['node',str(JS),str((DOC/'plan.json').relative_to(ROOT)),str((DOC/'ground.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
    ground=read(DOC/'ground.json.gz');final=module('citywalk_current_foundation_contract',HERE/'xl-final-script-pass.py')
    # Boundary is reporting context only; use the immutable source footprint.
    forms=HERE/'accepted/government-xl-citywalk-source-20261004/source-forms.json';form=read(forms)[0];polygon=Polygon(form['rings'][0],form['rings'][1:]);rows=[]
    for world in packet['sourceWorlds']:
        mode=world['label'];groundmode='actualLiteral' if mode=='providerOriginal' else mode
        f=final.foundation_context(np.asarray(world['position']).reshape(-1,3,3),np.asarray(ground['completeRegionalGroundWorlds'][groundmode]).reshape(-1,3,3),polygon)
        rows.append(dict(mode=mode,foundation=f));print(dict(mode=mode,complete=f['completeTerrainTriangles'],faces=f['triangles'],buried=f['fullyBuriedTriangles'],minimumGapM=f['minimumGapM']),flush=True)
    for p,h in ground['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
    save(DOC/'foundation.json',dict(rows=rows,sourceGeometryChanges=0,installationApproved=False,qualification='Existing foundation_context contract; full source vertices/centroids, not a new exact surface proof. Current terrain only, no candidate replacement.'))
    paths=[Path(__file__),JS,SRC,forms,HERE/'xl-final-script-pass.py']+[ROOT/p for p in ground['inputHashes']]
    module('citywalk_current_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-original-foundation-v1',paths,dict(uids=['landsd/134332:0'],fullAcceptance=False,sourceOnly=True,nextStep='Use current foundation results to choose source functional review or terrain repair; contact junction remains independent.'))
if __name__=='__main__':main()
