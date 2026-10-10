"""Generate an unpublished terrain-only proposal; preserve complete source bytes.

The single-source diagnostic is historical evidence, not current acceptance.
All upward Villa facets constrain this conservative terrain proposal. No
source face is moved, removed, merged or accepted through a tolerance waiver.
"""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_upward_facets_conservative_terrain_ceiling_20261010 import ceiling

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-villa-complete-upward-terrain-ceiling-proposal-v1-20261010'
DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-villa-complete-original-current-physical-v1-20261010'
UID='landsd/89917:0'
SOURCE_SHA='4407cbd52574f50e6b6bdddc6e581c96bbd0653426f89df0e490ae0b2096935d'
TERRAIN_SHA='196dd62bf6564d20d19e3661e4faa48a2348d2d413bb71d889af2d695277af4f'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists() and not LOCAL.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
    row=next(r for r in read(PRIOR/'selection.json.gz')['rows'] if r['uid']==UID)
    source=ROOT/row['candidate']['path'];raw=source.read_bytes()
    assert digest(raw)==SOURCE_SHA==row['sourceSHA256']
    original=decode_original_world_triangles(raw);assert original.shape==(16669,3,3)
    runtime_path=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz'
    runtime=read(runtime_path)
    g=next(r for r in runtime['rows'] if r['uid']==UID)
    assert g['sourceSHA256']==SOURCE_SHA
    literal=np.asarray(g['position'],np.float64).reshape(-1,3)[np.asarray(g['index'],np.uint32).reshape(-1,3)]
    patch=read(PRIOR/'terrain-candidates.json')[0]
    terrain_path=ROOT/patch['path'];assert ref(terrain_path)['sha256']==TERRAIN_SHA==patch['sha256']
    terrain=read(terrain_path)
    raw_positions=np.asarray(terrain['nativeMesh']['position'],np.float64).reshape(-1,3)
    # Production native-terrain.js uses Float32Array(mesh.position).
    p=raw_positions.astype(np.float32).astype(np.float64)
    idx=np.asarray(terrain['nativeMesh']['index'],np.uint32).reshape(-1,3)
    assert len(idx)==1252
    try:
        changed,proof=ceiling(original,literal,p,idx)
    except AssertionError as e:
        result=dict(proposalCreated=False,remainingReason=str(e),sourceSHA256=SOURCE_SHA,
                    sourceGeometryChanges=0,publication=False,currentAcceptancePassed=False)
        save(DOC/'proposal-diagnostic.json',result)
        paths=[Path(__file__),source,terrain_path,runtime_path,PRIOR/'foundation.json']
    else:
        # Numeric data only. Original X/Z coordinates and every terrain index
        # stay fixed; source model bytes and all earlier proposals are untouched.
        assert np.array_equal(np.asarray(changed,np.float32).astype(np.float64),changed),'Proposal must be exactly representable in renderer Float32'
        changed_ids=np.asarray(proof['changedRawVertexRecords'],np.int64)
        proposal_positions=raw_positions.copy();proposal_positions[changed_ids,1]=changed[changed_ids,1]
        assert np.array_equal(proposal_positions[:,[0,2]],raw_positions[:,[0,2]])
        assert np.array_equal(proposal_positions.astype(np.float32).astype(np.float64),changed)
        terrain['nativeMesh']['position']=proposal_positions.reshape(-1).tolist()
        terrain['terrainCeilingProposal']=dict(originalTerrain=ref(terrain_path),source=ref(source),
            algorithm=ref(HERE/'original_upward_facets_conservative_terrain_ceiling_20261010.py'),
            qualification='Unpublished conservative terrain correction; not installation or current support acceptance.')
        output=LOCAL/'government-native-89917-0.json';save(output,terrain)
        proposed={**patch,'path':str(output.relative_to(ROOT)),'sha256':ref(output)['sha256']}
        save(DOC/'terrain-candidates.json',[proposed]);save(DOC/'complete-roof-ceiling-proof.json.gz',proof)
        result=dict(proposalCreated=True,sourceSHA256=SOURCE_SHA,completeOriginalFaces=16669,
            candidateTerrainVertexRecordsChanged=proof['terrainGeometryChanges'],
            maximumTerrainLoweringM=proof['maximumTerrainLoweringM'],
            completeUpwardSourceFaces=proof['completeUpwardSourceFaces'],
            candidateTerrain=ref(output),sourceGeometryChanges=0,publication=False,currentAcceptancePassed=False,
            qualification='Candidate terrain only. Requires fresh single-source physics, all-component support, continuous facets and browser checks before any installation.')
        save(DOC/'proposal-diagnostic.json',result)
        paths=[Path(__file__),source,terrain_path,runtime_path,PRIOR/'foundation.json',output]
    paths.extend([ROOT/'3d-viewer/city/native-terrain.js'])
    paths.extend([HERE/'original_upward_facets_conservative_terrain_ceiling_20261010.py',
        HERE/'test_original_upward_facets_conservative_terrain_ceiling_20261010.py',
        HERE/'exact_original_projection_coverage_20261009.py',
        HERE/'exact_packed_world_geometry_20261009.py',manifest])
    assert ref(manifest)==start and digest(source.read_bytes())==SOURCE_SHA
    spec=importlib.util.spec_from_file_location('villa_roof_proposal_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.freeze(BATCH,'complete-upward-original-and-literal-terrain-ceiling-proposal-v2',paths,
        {**result,'uids':[UID],'manifestSHA256':start['sha256'],'humanStatus':'held-for-compute',
         'humanDecisionRequired':False,'aiGeometryModellingRequired':False})
    print({k:v for k,v in result.items() if k!='candidateTerrain'},flush=True)

if __name__=='__main__':main()
