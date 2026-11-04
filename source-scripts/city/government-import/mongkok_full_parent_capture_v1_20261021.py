"""Capture actual complete terrain for the expanded stadium repair domain, without edits."""
from pathlib import Path
import subprocess,json,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-full-parent-capture-v1-20261021';DOC=BASE/BATCH

def main():
    assert not DOC.exists();scopefolder=BASE/'government-xl-mongkok-expanded-regional-scope-v1-20261021';_,pins=authenticate(scopefolder)
    p=scopefolder/'scope.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];scope=read(p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==pins[str(manifest.relative_to(ROOT))]
    assert scope['regionalCoarseCells']==[510,387,514,390]
    refs=[Path(__file__),p,scopefolder/'result.json'];script=HERE/'mongkok_full_parent_capture_v1_20261021.mjs'
    for q in [manifest,ROOT/'3d-viewer/city/data/terrain.json',ROOT/'3d-viewer/city/data/government-native-240527-0.json']:
        assert digest(q.read_bytes())==pins[str(q.relative_to(ROOT))];refs.append(q)
    inputdata=dict(uid='landsd/240332:0',currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),completeOutwardRoundedDomainXZBounds=scope['regionalParentExtent'],evidenceRefs=[dict(path=str(q.relative_to(ROOT)),sha256=digest(q.read_bytes()))for q in refs])
    claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['terrain-capture:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        save(DOC/'input.json.gz',inputdata)
        with (DOC/'worker.log').open('w')as log:
            subprocess.run(['node',str(script),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'ground.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        ground=read(DOC/'ground.json.gz');assert ground['proposedCoarseRoutingCells']==scope['regionalCoarseCells']
        for name,h in ground['inputHashes'].items():assert digest((ROOT/name).read_bytes())==h;refs.append(ROOT/name)
        assert reservations.owns(lease)
        result=dict(uids=['landsd/240332:0'],retainedUids=scope['touchingNativeUids'],ordinaryNeighbourCount=scope['intersectingForms'],regionalCoarseCells=scope['regionalCoarseCells'],completeCapturedGroundFacets=len(ground['completeClosedDomainAABBActualGroundFacets']),restoredRootGroundFacets=len(ground['completeRestoredOriginalParentFacetsInsideRoutingMask']),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False)
        save(DOC/'summary.json',result)
        module('stadium_parent_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-current-stadium-parent-terrain-capture',list(dict.fromkeys(refs+[script])),result)
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
