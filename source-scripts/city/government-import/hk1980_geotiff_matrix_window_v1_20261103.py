"""Require a literal north-up matrix and an independently agreeing world file."""
import math
from hk1980_geotiff_window_v1_20261103 import window


def matrix_window(tags, size, bounds, world_file):
    keys = list(tags[34735])
    assert keys[:3] == [1, 1, 0] and len(keys) == 4 + 4 * keys[3]
    values = {}
    for n in range(keys[3]):
        key, location, count, value = keys[4 + n * 4:8 + n * 4]
        assert key not in values
        if location == 0:
            assert count == 1
            values[key] = value
    assert values[1024] == 1 and values[3072] == 2326 and values.get(1025, 1) == 1
    assert 33550 not in tags and 33922 not in tags
    matrix = list(tags[34264])
    assert len(matrix) == 16 and all(math.isfinite(v) for v in matrix)
    dx, dy, x0, y0 = matrix[0], -matrix[5], matrix[3], matrix[7]
    assert dx > 0 and dy > 0
    assert matrix == [dx, 0, 0, x0, 0, -dy, 0, y0, 0, 0, 1, 0, 0, 0, 0, 1]
    world = [float(v) for v in world_file.split()]
    assert len(world) == 6 and all(math.isfinite(v) for v in world)
    expected = [dx, 0, 0, -dy, x0 + dx / 2, y0 - dy / 2]
    assert all(abs(a - b) <= 1e-7 for a, b in zip(world, expected)), 'World-file centres and TIFF matrix disagree'
    # Equivalent affine coordinates for the existing crop arithmetic; raw source tags stay intact.
    equivalent = {34735: (1, 1, 0, 3, 1024, 0, 1, 1, 1025, 0, 1, 1, 3072, 0, 1, 2326),
                  33550: (dx, dy, 0), 33922: (0, 0, 0, x0, y0, 0)}
    result = window(equivalent, size, bounds)
    result.update(originalNorthUpMatrix=matrix, independentWorldFileMatches=True,
                  rasterTypeTagPresent=1025 in values, rawSourceTagsChanged=False,
                  pixelCornerAndCentreEstablishedByIndependentWorldFile=True)
    return result
