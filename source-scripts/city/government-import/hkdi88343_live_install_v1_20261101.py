"""Unchanged atomic installer with the explicit HKDI evidence-bound publisher."""
from pathlib import Path
from hkdi88343_installed_parent_adapter_v1_20261101 import configure, review_and_refs
configure()
import installed_support_model_only_live_install_v1_20261027 as installer
GENERIC = Path(installer.__file__)
installer.PUB = installer.HERE / 'hkdi88343_guarded_publish_v1_20261101.py'
# The existing supervisor re-enters __file__ for its owned child. Keep the
# explicit route active there, and authenticate both wrapper and generic code.
installer.__file__ = __file__
load = installer.load
def bound_load(previous):
    keys, pointer, models, delta, refs = load(previous)
    _, paths = review_and_refs()
    refs = installer.distinct_refs([*refs, *[installer.ref(p) for p in [GENERIC, Path(__file__),
        installer.HERE / 'hkdi88343_owned_loopback_v1_20261101.py', *paths]]])
    for item in refs: installer.check(item)
    return keys, pointer, models, delta, refs
installer.load = bound_load
if __name__ == '__main__': installer.main()
