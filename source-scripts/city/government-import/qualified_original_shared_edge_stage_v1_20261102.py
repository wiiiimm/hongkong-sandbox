"""Explicit shared-edge routing around the unchanged full-boundary stage.

Only this stage invocation installs the dispatcher; every other point contact
keeps its original verifier. All dispatchers are restored even on failure.
"""
from contextlib import contextmanager
from pathlib import Path
from run import ROOT, HERE, read, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
import original_terrain_point_contact_v2_20261025 as point
import original_terrain_obligation_union_v2_20261025 as union
from original_terrain_shared_edge_v1_20261102 import verify as edge_verify
from original_terrain_obligation_union_v3_20261102 import merge as edge_merge
from supported_original_full_boundary_stage_v1_20261101 import configure


@contextmanager
def dispatch(scope, candidate, parent, previous):
    ordinary_verify, ordinary_merge = point.verify, union.merge
    def verify(s, c, p, old):
        if s != scope:
            return ordinary_verify(s, c, p, old)
        assert c == candidate and p == parent and old == previous
        return edge_verify(s, c, p, old)
    point.verify, union.merge = verify, edge_merge
    try:
        yield
    finally:
        point.verify, union.merge = ordinary_verify, ordinary_merge


def main():
    stage = configure()
    cfg = stage.CONFIG
    assert cfg['sharedEdgeContext'] == cfg['pointContactContext']
    base = ROOT / 'docs/astra-city/government-import'
    folder = base / cfg['sharedEdgeContext']
    _, pins = authenticate(folder)
    def take(binding):
        path = ROOT / binding['path']
        assert digest(path.read_bytes()) == binding['sha256'] == pins[binding['path']]
        return read(path)
    path = folder / 'summary.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    context = read(path)
    scope, candidate, parent = [take(context[k]) for k in ['scopeBinding', 'candidateBinding', 'parentBinding']]
    previous = {b['url']: take(b) for b in context['oldTerrainBindings']}
    replay = edge_verify(scope, candidate, parent, previous)
    assert {k: context[k] for k in replay} == replay
    original_module = stage.module
    def load(name, source):
        result = original_module(name, source)
        if Path(source).name == 'xl-popcorn-source-investigations-checkpoints-20261009.py':
            freeze = result.freeze
            def bound(batch, recipe, refs, summary):
                extra = [Path(__file__), HERE/'original_terrain_shared_edge_v1_20261102.py',
                    HERE/'original_terrain_obligation_union_v3_20261102.py',
                    HERE/'test_original_terrain_shared_edge_v1_20261102.py']
                return freeze(batch, recipe, list(dict.fromkeys([*refs, *extra])), summary)
            result.freeze = bound
        return result
    stage.module = load
    try:
        with dispatch(scope, candidate, parent, previous):
            stage.main()
    finally:
        stage.module = original_module


if __name__ == '__main__':
    main()
