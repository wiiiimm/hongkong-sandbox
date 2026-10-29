"""Rectangularise complete parent land cells without filling water or partial cells."""
import shapely


def partition(land,bounds,cells,required):
    x0,z0,x1,z1=cells
    assert all(type(i)is int for i in cells)and x0<x1 and z0<z1
    a,b,c,d=bounds;dx=(c-a)/(x1-x0);dz=(d-b)/(z1-z0)
    assert dx==dz and dx>0
    extent=shapely.box(a,b,c,d)
    assert extent.covers(land)and not land.is_empty and land.is_valid
    live=set();cell_polygons=[]
    for z in range(z0,z1):
        for x in range(x0,x1):
            tile=shapely.box(a+(x-x0)*dx,b+(z-z0)*dz,a+(x+1-x0)*dx,b+(z+1-z0)*dz)
            if tile.difference(land).is_empty:
                live.add((x,z));cell_polygons.append(tile)
            else:
                assert tile.intersection(land).area==0,'Partial parent land cell requires another exact method'
    union=shapely.union_all(cell_polygons)
    assert union.symmetric_difference(land).is_empty,'Parent land domain changed'
    assert required.difference(union).is_empty,'Required source/return region touches absent parent land'
    active={};rectangles=[]
    for z in range(z0,z1):
        runs=[];start=None
        for x in range(x0,x1+1):
            if x<x1 and(x,z)in live:
                if start is None:start=x
            elif start is not None:runs.append((start,x));start=None
        current=set(runs)
        for run in set(active)-current:rectangles.append(active.pop(run))
        for run in runs:
            if run in active:active[run][3]=z+1
            else:active[run]=[run[0],z,run[1],z+1]
    rectangles.extend(active.values());rectangles.sort(key=lambda r:(r[1],r[0],r[3],r[2]))
    polygons=[shapely.box(a+(r[0]-x0)*dx,b+(r[1]-z0)*dz,a+(r[2]-x0)*dx,b+(r[3]-z0)*dz)for r in rectangles]
    assert shapely.union_all(polygons).symmetric_difference(land).is_empty
    for i,left in enumerate(polygons):
        assert all(left.intersection(right).area==0 for right in polygons[i+1:])
    return rectangles,polygons
