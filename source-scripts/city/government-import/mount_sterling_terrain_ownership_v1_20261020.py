"""Bind eight original assembly owners to private terrain, without geometry changes."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-terrain-ownership-v1-20261020'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists()
    prior=BASE/'government-xl-mount-sterling-terrain-validation-v2-20261020'
    attr=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
    refs=[Path(__file__)];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for d in [prior,attr]:
            r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            refs.append(d/'result.json');pins.update({e['path']:e['sha256'] for e in r['evidenceRefs']})
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    candidate=take(prior/'terrain-candidates.json')[0];src=ROOT/candidate['path'];old=take(src)
    rows=take(attr/'input.json.gz')['rows'];sources={r['uid']:r['entry']['sha256'] for r in rows};assert len(sources)==8
    patch=copy.deepcopy(old);previous=old['meta']['targetUids'];patch['meta']['targetUids']=sorted(set(previous)|set(sources))
    tool=module('mount_owner_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');tool.DOC=DOC;tool.overlap_proof(patch,[src,Path(__file__)])
    check=copy.deepcopy(patch);check['meta']['targetUids']=previous;check['nativeMesh'].pop('sourceOverlap',None)
    original=copy.deepcopy(old);original['nativeMesh'].pop('sourceOverlap',None);assert check==original
    pub=module('mount_owner_validate',HERE.parent/'island-detail-integration/publish.py');terrain=ROOT/'3d-viewer/city/data/terrain.json';pub.validate_patch(patch,read(terrain))
    out=LOCAL/'candidate-terrain.json';save(out,patch)
    save(DOC/'terrain-candidates.json',[{**candidate,'path':str(out.relative_to(ROOT)),'sha256':digest(out.read_bytes()),'uids':sorted(sources)}])
    save(DOC/'metadata-equivalence.json',dict(previousTargetUids=previous,targetUids=patch['meta']['targetUids'],sourceSHA256ByUid=sources,completeRenderedPayloadEqual=True,terrainValidationPassed=True,sourceOverlapProofRecomputed=True,renderedGeometryChanges=0,installationApproved=False))
    refs.extend([out,terrain,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py'])
    module('mount_owner_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-terrain-ownership-metadata-only',refs,dict(uids=sorted(sources),completeGeometryUnchanged=True,terrainValidationPassed=True,installationApproved=False))
if __name__=='__main__':main()
