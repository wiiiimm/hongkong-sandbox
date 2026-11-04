"""Diagnostic projection of unchanged source faces above a component height.

This clips copies for measurement only. It never creates a model asset, grants
ownership, suppresses a form, or changes any physical acceptance threshold.
"""
import math
import numpy as np
import shapely

def above_height_projection(triangles, height):
    if not math.isfinite(height):
        raise ValueError('Finite height required')
    triangles=np.asarray(triangles,dtype=float)
    if triangles.ndim!=3 or triangles.shape[1:]!=(3,3) or not np.isfinite(triangles).all():
        raise ValueError('Finite complete triangles required')
    full=triangles[triangles[:,:,1].min(axis=1)>=height]
    crossing=triangles[(triangles[:,:,1].min(axis=1)<height)&(triangles[:,:,1].max(axis=1)>=height)]
    polygons=list(shapely.polygons(full[:,:,[0,2]]))
    for triangle in crossing:
        output=[]
        for previous,current in zip(np.roll(triangle,1,axis=0),triangle):
            pin,cin=previous[1]>=height,current[1]>=height
            if pin!=cin:
                ratio=(height-previous[1])/(current[1]-previous[1])
                output.append(previous+ratio*(current-previous))
            if cin:output.append(current.copy())
        if len(output)>=3:
            polygon=shapely.Polygon(np.asarray(output)[:,[0,2]])
            if polygon.area>1e-10:polygons.append(polygon)
    return shapely.union_all([p for p in polygons if p.area>1e-10])

def measure(triangles, footprint, height):
    projection=above_height_projection(triangles,height)
    area=float(projection.intersection(footprint).area)
    return {'thresholdHeightHKPD':height,'componentAreaM2':float(footprint.area),
            'coveredAreaM2':area,'coveredFraction':area/footprint.area if footprint.area else None,
            'acceptanceGranted':False,'qualification':'Height-plane coverage only. Height metadata can differ from original geometry. High coverage is not complete geometry, ownership, support or suppression proof.'}
