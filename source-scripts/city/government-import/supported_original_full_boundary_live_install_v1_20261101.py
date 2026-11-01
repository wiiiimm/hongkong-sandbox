"""Existing atomic supported installer with full dispatch and current browser."""
from pathlib import Path
from supported_original_full_boundary_stage_v1_20261101 import configure,FAMILY_FILES
configure()
import selected_original_supported_live_install_v4_20261025 as installer
GENERIC=Path(installer.__file__)
installer.PUB=installer.HERE/'supported_original_full_boundary_publish_v1_20261101.py'
installer.BROWSER=installer.FOCUSED=installer.HERE/'ronsdale_three_live_browser_v15_20261026.mjs'
installer.__file__=__file__
load=installer.load
def bound_load(previous):
    keys,pointer,models,delta,refs=load(previous)
    paths=[GENERIC,Path(__file__),installer.HERE/'supported_original_full_boundary_stage_v1_20261101.py',installer.HERE/'supported_original_full_boundary_owned_loopback_v1_20261101.py',*FAMILY_FILES]
    refs=installer.distinct_refs([*refs,*[installer.ref(p)for p in paths]])
    for q in refs:installer.check(q)
    return keys,pointer,models,delta,refs
installer.load=bound_load
if __name__=='__main__':installer.main()
