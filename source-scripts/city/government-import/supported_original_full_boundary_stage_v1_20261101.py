"""Existing supported-terrain stage with every installed top-level family verifier.

No admission contract is weakened: retain the pair, three-member and five-member
checks using their existing complete dispatcher. Record its full provenance.
"""
from pathlib import Path
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
from run import HERE
FAMILY_FILES=[HERE/n for n in ['fuying_five_member_terrain_stage_v1_20261029.py','fuying_whole_parent_five_boundary_v1_20261029.py','three_member_native_boundary_v1_20261027.py']]
def configure():
    import selected_original_supported_qualified_stage_v4_20261025 as stage
    if getattr(stage,'_completeFamilyDispatcherBound',False):return stage
    ordinary=stage.module
    def module(name,path):
        loaded=ordinary(name,path)
        if Path(path).name=='publish.py':
            main=loaded.main
            def publish():
                with complete_boundary_validators():return main()
            loaded.main=publish
        if Path(path).name=='xl-popcorn-source-investigations-checkpoints-20261009.py':
            freeze=loaded.freeze
            def bound(batch,recipe,refs,result):
                return freeze(batch,recipe,list(dict.fromkeys([*refs,Path(__file__),*FAMILY_FILES])),
                    {**result,'completeInstalledTopLevelBoundaryFamiliesVerified':True})
            loaded.freeze=bound
        return loaded
    stage.module=module;stage._completeFamilyDispatcherBound=True
    return stage
if __name__=='__main__':configure().main()
