"""Run existing highest-surface terrain validation on an unchanged saved candidate.

Private validation only; changed-domain, model placement and publication remain unapproved.
"""
from pathlib import Path
import argparse, copy
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','diagnostic']:
        p.add_argument('--'+k,required=True)
    a=p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.diagnostic])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert not out.exists() and not local.exists()
    _,pins=authenticate(base/a.diagnostic);refs=[Path(__file__),base/a.diagnostic/'result.json']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    diagnostic=take(base/a.diagnostic/'summary.json')
    assert diagnostic['terrainValidationPassed'] is False and diagnostic['reason']=='Native terrain contains overlapping height surfaces'
    path=ROOT/diagnostic['candidate']['path'];patch=take(path)
    assert digest(path.read_bytes())==diagnostic['candidate']['sha256']
    assert not patch['nativeMesh'].get('sourceOverlap')
    assert len(patch['nativeMesh']['index'])//3==diagnostic['candidateFaces']<=25000,'terrain-runtime-budget'
    parentpath=ROOT/'3d-viewer'/patch['meta']['parentTerrain'];parent=take(parentpath)
    assert digest(parentpath.read_bytes())==patch['meta']['parentSha256']
    original=copy.deepcopy(patch);source_files=[]
    for source in patch['meta']['source']['nativeSources']:
        sourcepath=ROOT/source['path'];gltf=take(sourcepath)
        assert digest(sourcepath.read_bytes())==source['sha256']
        source_files.append(source)
        for buffer in gltf.get('buffers',[]):
            member=sourcepath.parent/buffer['uri'];take(member) if member.suffix=='.json' else None
            assert digest(member.read_bytes())==pins[str(member.relative_to(ROOT))]
            refs.append(member);source_files.append(dict(path=str(member.relative_to(ROOT)),sha256=digest(member.read_bytes())))
    overlap=module('private_saved_overlap',HERE/'native_patch_resolution.py')
    evidence=out/'highest-surface-evidence.json'
    audit=overlap.approve_original_overlap(patch,path,evidence,source_files)
    patch['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT))
    overlap.finalize_overlap_evidence(patch,evidence)
    stripped=copy.deepcopy(patch);stripped['nativeMesh'].pop('sourceOverlap')
    assert stripped==original,'Candidate geometry or metadata changed outside overlap evidence'
    builder=module('saved_overlap_validator',HERE/'resolve-pass-indexed-parent-clipping.py')
    passed=False;failure=None
    try:builder.validate_patch(patch,parent)
    except AssertionError as error:failure=str(error)
    else:passed=True
    candidate=local/'candidate-terrain.json';save(candidate,patch)
    refs.extend([candidate,evidence,HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',HERE.parent/'island-detail-integration/publish.py'])
    result=dict(uids=diagnostic['uids'],candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=digest(candidate.read_bytes())),candidateFaces=diagnostic['candidateFaces'],existingTerrainValidatorPassed=passed,remainingValidatorFailure=failure,highestSurfaceSamples=audit['float32HighestRayAgreement']['samples'],maximumSamplerRayErrorM=audit['float32HighestRayAgreement']['maxError'],candidateMeshUnchanged=True,sourceGeometryChanges=0,sourcePoseChanges=0,productionTerrainChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Only existing highest-native-surface evidence metadata added to the exact saved private candidate. Full canonical terrain validator runs without guard changes. Changed-domain obligations, complete model placement and source identity remain separate; no installation approval.')
    save(out/'summary.json',result)
    module('saved_overlap_validation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'saved-private-terrain-existing-highest-surface-validator',refs,result)
    print(result,flush=True)


if __name__=='__main__':main()
