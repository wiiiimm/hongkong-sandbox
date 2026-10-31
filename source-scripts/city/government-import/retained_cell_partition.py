"""Validate a root-cell candidate with full source transition and retained coverage."""
def validate_partition(cells, world_bounds, old_cells, parent, extent):
    assert len(cells) == 4 and all(type(c) is int for c in cells)
    c0, r0, c1, r1 = cells
    assert 0 <= c0 < c1 < parent['w'] and 0 <= r0 < r1 < parent['h']
    assert c0 <= old_cells[0] and r0 <= old_cells[1]
    assert c1 >= old_cells[2] and r1 >= old_cells[3], 'All retained cells required'
    x0, z0, x1, z1 = extent(cells, parent)
    for lo, hi in world_bounds:
        # Original source core adds 1 m; original transition is 10 m wide.
        assert lo[0] - 11 >= x0 and lo[2] - 11 >= z0
        assert hi[0] + 11 <= x1 and hi[2] + 11 <= z1
    return list(cells)
