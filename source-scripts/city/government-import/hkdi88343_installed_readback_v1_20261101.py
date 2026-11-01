"""Independent all-old-assets/full521 readback using the exact HKDI contract."""
from pathlib import Path
import installed_support_model_only_installed_readback_v2_20261101 as verifier
from hkdi88343_installed_parent_contract_v1_20261101 import verify_metadata
from run import ROOT, HERE, read, digest
REVIEW=ROOT/'docs/astra-city/government-import/government-xl-hkdi22089-component-identity-review-v1-20261101/ROOT-COMPONENT-IDENTITY-REVIEW.json'
GENERIC=Path(verifier.__file__)
def metadata(models,sources,supports,original,current):
    # Generic independent readback authenticates this exact review file against
    # the completed installed receipt before metadata admission is called.
    return verify_metadata(models,sources,supports,original,current,read(REVIEW))
verifier.metadata_contract=metadata
load_module=verifier.module
def module(name,path):
    loaded=load_module(name,path)
    if Path(path).name=='xl-popcorn-source-investigations-checkpoints-20261009.py':
        freeze=loaded.freeze
        def bound(batch,recipe,refs,result):
            return freeze(batch,recipe,list(dict.fromkeys([*refs,Path(__file__),GENERIC,REVIEW,
                HERE/'hkdi88343_installed_parent_contract_v1_20261101.py'])),result)
        loaded.freeze=bound
    return loaded
verifier.module=module
if __name__=='__main__':verifier.main()
