"""Exact Miu Fat preview metadata contract; no identity or publication approval."""
from copy import deepcopy
from original_supported_catalogue_scope_v1_20261024 import verify as verify_supports
SOURCES={'landsd/165889:0':'5c2a3560515f4ad2f80e6f2d5b634988ae4d655a9268c137bd55c5952e00b862','landsd/233638:0':'0bd1fc65477e3b4f84805586f62cb2c0e8aca133532de79822eb413e88dcdf91','landsd/241215:0':'901fd6a0098ede2e783deeb9b308f9594fe31dc0ca44ef2c6e1790adb169ba7a'}
PRIMARY='landsd/165889:0';HALL='landsd/241215:0';GATE='landsd/197385:0';SUPPORTS={HALL:PRIMARY}

def verify_metadata(models,coverage):
    assert coverage['sourceSHA256']==SOURCES[PRIMARY]and coverage['secondaryUid']==GATE
    assert coverage['requiredOriginalAssembly']==SOURCES and coverage['coverageApprovedForStagedValidation']is True
    assert coverage['stagedProposal']==dict(uid=PRIMARY,suppressesBuildingUids=[GATE])
    worlds=coverage['completeFourWorldCoverage'];assert len(worlds)==4 and {r['mode']for r in worlds}=={'original','literal','leftF32','balancedF32'}
    assert all(r['completeSourceProjectionCoversRecord']is True for r in worlds)
    assert coverage['allInstalledActorsChecked']==6873 and coverage['installedSupportUsers']==[]
    assert coverage['sourceGeometryChanges']==coverage['sourcePoseChanges']==0
    clean=deepcopy(models)
    for m in clean:
        assert m['uid']in SOURCES and m['rootTranslation']==[-834500,0,816500]
        assert m.get('verticalPlacementOffsetHKPD',0)==0 and not m.get('sourceWorldBounds')
        assert not m.get('retainedBasicSupportDependencies')
        if m['uid']==PRIMARY:
            assert m.get('suppressesBuildingUids')==[GATE];m.pop('suppressesBuildingUids')
        else:assert not m.get('suppressesBuildingUids')
    return verify_supports(clean,SOURCES,SUPPORTS)
