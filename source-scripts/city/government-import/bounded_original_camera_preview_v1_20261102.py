"""Broaden capture framing around original companions; retain all preview gates.

Camera bounds only. Source/world bounds, actors, geometry, leases, approval
flags, runtime budgets and the existing browser assertions are unchanged.
"""
import math
from pathlib import Path
from run import HERE, save
from primrose_compound_foundation_v2_20261015 import module


def main():
    producer_path = HERE / 'selected_original_unapproved_private_server_browser_v2_20261030.py'
    producer = module('bounded_camera_existing_original_preview', producer_path)
    bounds = producer.CONFIG['captureBoundsByModel']
    assert bounds and set(bounds) <= set(producer.SOURCES)
    for box in bounds.values():
        assert len(box) == 2 and all(len(p) == 3 for p in box)
        assert all(type(v) in (int, float) and math.isfinite(v) for p in box for v in p)
        assert all(box[0][i] < box[1][i] for i in range(3))
    ordinary_module = producer.module

    def write(path, value):
        if path.name == 'preflight-config.json' or path.name.startswith('browser-config-'):
            assert not set(bounds) - set(value['browserUids'])
            value = {**value, 'captureBoundsByModel': bounds}
        return save(path, value)

    def load(name, path):
        result = ordinary_module(name, path)
        if Path(path).name == 'xl-popcorn-source-investigations-checkpoints-20261009.py':
            ordinary_freeze = result.freeze
            def freeze(batch, recipe, refs, summary):
                summary = {**summary, 'captureBoundsByModel': bounds,
                           'cameraFramingOnly': True, 'sourceBoundsChanged': False}
                return ordinary_freeze(batch, recipe,
                    list(dict.fromkeys([*refs, producer_path, Path(__file__)])), summary)
            result.freeze = freeze
        return result

    # The existing owned-child invocation must return through this wrapper.
    producer.__file__ = __file__
    producer.save = write
    producer.module = load
    producer.main()


if __name__ == '__main__':
    main()
