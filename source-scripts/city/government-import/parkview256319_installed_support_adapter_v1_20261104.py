"""Process-local exact Parkview route with full audited parent and seam evidence.
Generic contracts, installed parent flags and original geometry remain unchanged.
"""
from pathlib import Path
from run import ROOT,HERE,read,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
import parkview256319_installed_support_contract_v1_20261104 as contract
BASE=ROOT/'docs/astra-city/government-import'
AUDIT=BASE/'government-xl-parkview-podium-flag-audit-v5-20261104'
CONTEXT=BASE/'government-xl-parkview256319-source-context-review-v2-20261104'

def review_and_refs():
    refs=[Path(__file__),HERE/'parkview256319_installed_support_contract_v1_20261104.py'];data=[]
    for folder,name in [(AUDIT,'audit.json'),(CONTEXT,'ROOT-SOURCE-CONTEXT-REVIEW.json')]:
        _,pins=authenticate(folder)
        for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
        p=folder/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];data.append(read(p));refs.extend([folder/'result.json',*[ROOT/p for p in pins]])
    return data,list(dict.fromkeys(refs))

def configure():
    import installed_support_model_only_qualified_stage_v1_20261027 as stage
    assert stage.CONFIG['prefix']=='government-xl-parkview256319-reviewed-current-original'
    assert stage.SOURCES=={contract.UID:contract.SHA}and stage.SUPPORTS=={contract.UID:contract.PARENT}
    assert stage.CONFIG['parentApprovalAudit']==AUDIT.name and stage.CONFIG['sourceContextReview']==CONTEXT.name
    (audit,context),refs=review_and_refs();assert context['currentManifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
    physical=read(BASE/stage.CONFIG['physical']/'ROOT-PHYSICAL-REVIEW.json')
    assert physical['boundedSourceContext']==context and physical['supportEligibilityAudit']==audit
    assert physical['boundedSourceContextReview']==stage.ref(CONTEXT/'ROOT-SOURCE-CONTEXT-REVIEW.json')and physical['supportEligibilityReview']==stage.ref(AUDIT/'audit.json')
    def metadata(models,sources,supports,original,current):
        fresh,_=review_and_refs();assert fresh==[audit,context]
        return contract.verify_metadata(models,sources,supports,original,current,audit)
    stage.metadata_contract=metadata;stage.native_contract=contract.verify_native_scope
    original_module=stage.module
    def module(name,path):
        loaded=original_module(name,path)
        if Path(path).name=='xl-popcorn-source-investigations-checkpoints-20261009.py':
            freeze=loaded.freeze
            def bound_freeze(batch,recipe,paths,result):
                _,fresh_refs=review_and_refs()
                return freeze(batch,recipe,list(dict.fromkeys([*paths,*fresh_refs,HERE/'parkview256319_qualified_stage_v1_20261104.py',HERE/'fuying_five_member_terrain_stage_v1_20261029.py'])),{**result,'exactInstalledParentAndAdjacentSeamRoute':stage.ref(Path(__file__))})
            loaded.freeze=bound_freeze
        if Path(path).name=='publish.py':
            publish=loaded.main
            def bound_publish():
                from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
                with complete_boundary_validators():return publish()
            loaded.main=bound_publish
        return loaded
    stage.module=module
    return stage
