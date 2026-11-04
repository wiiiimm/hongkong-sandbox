"""Lease-fenced preparation test only; cannot apply terrain or install models."""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from fuying_five_member_terrain_stage_v1_20261029 import publication_adapter
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-fuying181489-'
BATCH=PREFIX+'five-member-terrain-publisher-dry-run-v1-20261029';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert '--apply'not in sys.argv
    if '--owned'not in sys.argv:
        assert not DOC.exists()and not LOCAL.exists()
        scope=read(BASE/(PREFIX+'five-member-full-scope-v1-20261029')/'form-obligations.json.gz')
        native=read(BASE/(PREFIX+'five-member-full-scope-v1-20261029')/'scope.json')['touchingNativeUids']
        resources=sorted({'building:'+f['uid']if f['uid'].startswith('landsd/')else'source-form:'+f['uid']for f in scope}|{'building:'+u for u in native}|{'terrain:city/data/terrain.json','terrain:city/data/government-native-fu-wong-original-v1-20261023.json'})
        claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__),HERE/'fuying_five_member_terrain_stage_v1_20261029.py'];pins={};jobs={}
    def take(batch,p):
        if batch not in pins:r,pins[batch]=authenticate(BASE/batch);jobs[batch]=r['jobId'];refs.append(BASE/batch/'result.json')
        assert ref(p)['sha256']==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    browser=PREFIX+'five-member-private-browser-v1-20261029';cfgpath=HERE/'local'/browser/'browser-config-390.json';cfg=take(browser,cfgpath)
    reviewbatch=PREFIX+'source-physical-visual-review-v1-20261029';reviewpath=BASE/reviewbatch/'ROOT-TERRAIN-GROUP-REVIEW.json';review=take(reviewbatch,reviewpath)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=ref(manifest);assert before==review['currentManifest'];refs.append(manifest)
    entries=cfg['terrain']
    for entry in entries:entry.pop('replaces',None)
    plan=dict(areas=[],topLevelTerrainPatches=entries,fuYingWholeNativeTerrainReplacement=dict(proof=review['wholeParentContract'],review=ref(reviewpath)))
    path=DOC/'terrain-only-plan.json';save(path,plan)
    pub=module('fuying_five_group_dry_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher'
    with publication_adapter(pub):
        sys.argv=['publish.py',str(path.relative_to(ROOT))];pub.main()
    report=read(pub.DOC/'publication-plan.json');assert not report['published']and len(report['topLevelTerrainPatches'])==5 and len(report['replacedTerrainPatches'])==1
    assert ref(manifest)==before and reservations.owns(lease)
    result=dict(uids=['landsd/181489:0'],terrainGroupDryRunPassed=True,allOrdinaryPublisherChecksRetained=True,globalRetainedBasicSupportCheckExecuted=True,publicInputsUnchanged=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,evidence=jobs,qualification='Terrain-only preparation with all existing publisher/global support/input guards. One exact old parent replaced logically by5fully validated members; all actual public bytes unchanged. Source installation, approved catalogue, fenced apply, live lifecycle and installed readback still required.')
    save(DOC/'summary.json',result);refs.extend([HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/retained_basic_support.py',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py']);refs.extend(ROOT/p for p in pub.PINNED_INPUTS if False)
    module('fuying_group_terrain_dry_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-member-whole-native-parent-ordinary-publisher-preparation-only',refs,result)
if __name__=='__main__':main()
