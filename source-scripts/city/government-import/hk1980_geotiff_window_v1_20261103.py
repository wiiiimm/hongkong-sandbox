"""Locate an unfitted EPSG2326 crop in an explicitly north-up GeoTIFF."""
import math


def window(tags, size, bounds):
    keys = list(tags[34735])
    assert keys[:3] == [1, 1, 0] and len(keys) == 4 + 4 * keys[3]
    values = {}
    for n in range(keys[3]):
        key, location, count, value = keys[4 + n * 4:8 + n * 4]
        assert key not in values
        if location == 0:
            assert count == 1
            values[key] = value
    assert values[1024] == 1 and values[1025] == 1 and values[3072] == 2326
    assert 34264 not in tags, 'Rotated/matrix TIFF requires a separate explicit transform'
    scale, tie = list(tags[33550]), list(tags[33922])
    assert len(scale) == 3 and scale[0] > 0 and scale[1] > 0 and scale[2] == 0
    assert len(tie) == 6 and tie[:3] == [0, 0, 0] and tie[5] == 0
    x0, y0, dx, dy = tie[3], tie[4], scale[0], scale[1]
    xmin, ymin, xmax, ymax = bounds
    assert all(math.isfinite(v) for v in [*bounds, *scale, *tie])
    assert xmin < xmax and ymin < ymax and 0 < size[0] * size[1] <= 400_000_000
    pixels = (math.floor((xmin - x0) / dx), math.floor((y0 - ymax) / dy),
              math.ceil((xmax - x0) / dx), math.ceil((y0 - ymin) / dy))
    l, t, r, b = pixels
    assert 0 <= l < r <= size[0] and 0 <= t < b <= size[1], 'Whole source crop must fit without clipping'
    extent = [x0 + l * dx, x0 + r * dx, y0 - b * dy, y0 - t * dy]
    return dict(pixelWindow=list(pixels), hk1980Extent=extent, pixelSizeM=[dx, dy], crs=2326,
                pixelIsArea=True, fittedTransform=False, resampling=False)
