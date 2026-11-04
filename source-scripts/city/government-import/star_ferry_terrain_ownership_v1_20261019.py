"""Preserve both retained terrain owners; change no rendered payload."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-terrain-ownership-v1-20261019'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-star-ferry-retained-wrapper-metrics-v3-20261019'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()
    receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    candidate=read(PRIOR/'terrain-candidates.json')[0];source=ROOT/candidate['path']
    assert ref(source)['sha256']==candidate['sha256']
    oldpath=ROOT/'3d-viewer'/candidate['replaces']['url'];assert digest(oldpath.read_bytes())==candidate['replaces']['sha256']
    old=read(oldpath);original=read(source);patch=copy.deepcopy(original)
    removed={'government-native-central-hullett-house','government-native-205767-0'}
    oldchildren=[c for c in old['patches']if c['id']in removed];assert len(oldchildren)==2
    retained=sorted({u for c in oldchildren for u in c['meta']['targetUids']});assert retained==['landsd/205767:0','landsd/73140:0']
    children=[c for c in patch['patches']if c['id']=='government-native-210032-0'];assert len(children)==1
    child=children[0];assert child['meta']['targetUids']==['landsd/210032:0'] and not child['nativeMesh'].get('sourceOverlap')
    child['meta']['targetUids']=sorted(retained+['landsd/210032:0'])
    proof=copy.deepcopy(patch)
    next(c for c in proof['patches']if c['id']==child['id'])['meta']['targetUids']=['landsd/210032:0']
    assert proof==original
    publisher=module('star_ferry_ownership_validate',HERE.parent/'island-detail-integration/publish.py')
    publisher.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
    out=LOCAL/'terrain-star-ferry.json';save(out,patch)
    save(DOC/'terrain-candidates.json',[{**candidate,'path':str(out.relative_to(ROOT)),'sha256':digest(out.read_bytes())}])
    save(DOC/'metadata-equivalence.json',dict(previousTerrain=ref(source),replacementTerrain=ref(out),allowedMetadataChanges=['patches[id=government-native-210032-0].meta.targetUids'],retainedTargetUids=retained,replacementTargetUids=child['meta']['targetUids'],completePayloadEqualAfterRemovingOnlyOwnership=True,terrainValidationPassed=True,sourceGeometryChanges=0,renderedGeometryChanges=0,installationApproved=False))
    refs=[Path(__file__),PRIOR/'result.json',oldpath,source,out,HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    module('star_ferry_ownership_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'retained-terrain-ownership-metadata-only',list(dict.fromkeys(refs)),dict(uids=child['meta']['targetUids'],completeGeometryUnchanged=True,terrainValidationPassed=True,installationApproved=False))
if __name__=='__main__':main()
