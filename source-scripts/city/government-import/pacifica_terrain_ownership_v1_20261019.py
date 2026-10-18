"""Retain installed terrain ownership without changing any rendered geometry."""
from pathlib import Path
import copy, shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-pacifica-terrain-ownership-v1-20261019'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-pacifica-expanded-grid-v4-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def geometry(p):
    p=copy.deepcopy(p);p['meta'].pop('targetUids');p['nativeMesh'].pop('sourceOverlap');return p
def main():
    assert not DOC.exists()
    receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    candidate=read(PRIOR/'terrain-candidates.json')[0]
    original=read(ROOT/candidate['path']);patch=copy.deepcopy(original)
    oldpath=ROOT/'3d-viewer'/candidate['replaces']['url'];assert digest(oldpath.read_bytes())==candidate['replaces']['sha256']
    old=read(oldpath);retained=old['meta']['targetUids'];assert retained==['landsd/265478:0']
    assert patch['meta']['targetUids']==['landsd/283036:0']
    patch['meta']['targetUids']=sorted(set(retained+patch['meta']['targetUids']))
    prior_evidence=ROOT/original['nativeMesh']['sourceOverlap']['evidencePath']
    assert digest(prior_evidence.read_bytes())==original['nativeMesh']['sourceOverlap']['evidenceSHA256']
    DOC.mkdir(parents=True);evidence=DOC/'native-overlap.json';shutil.copyfile(prior_evidence,evidence)
    patch['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT))
    repair=module('pacifica_ownership_rebind',HERE/'native_patch_resolution.py');repair.finalize_overlap_evidence(patch,evidence)
    assert geometry(patch)==geometry(original)
    old_audit=read(prior_evidence);new_audit=read(evidence)
    old_audit.pop('stagedGeometrySha256');new_audit.pop('stagedGeometrySha256');assert old_audit==new_audit
    publisher=module('pacifica_ownership_validate',HERE.parent/'island-detail-integration/publish.py')
    publisher.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
    out=LOCAL/'terrain-pacifica-mall.json';save(out,patch)
    updated={**candidate,'path':str(out.relative_to(ROOT)),'sha256':digest(out.read_bytes())}
    save(DOC/'terrain-candidates.json',[updated])
    save(DOC/'metadata-equivalence.json',dict(previousTerrain=ref(ROOT/candidate['path']),replacementTerrain=ref(out),
        allowedMetadataChanges=['meta.targetUids','nativeMesh.sourceOverlap.evidencePath','nativeMesh.sourceOverlap.evidenceSHA256'],
        originalTargetUids=original['meta']['targetUids'],retainedTargetUids=retained,replacementTargetUids=patch['meta']['targetUids'],
        completePayloadEqualAfterRemovingOnlyOwnershipAndEvidenceReference=True,
        overlapEvidenceEqualExceptPayloadBinding=True,terrainValidationPassed=True,
        sourceGeometryChanges=0,renderedGeometryChanges=0,installationApproved=False))
    refs=[Path(__file__),PRIOR/'result.json',oldpath,prior_evidence,HERE/'native_patch_resolution.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',out]
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    module('pacifica_ownership_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-terrain-ownership-metadata-only',list(dict.fromkeys(refs)),dict(uids=patch['meta']['targetUids'],completeGeometryUnchanged=True,terrainValidationPassed=True,installationApproved=False))
if __name__=='__main__':main()
