"""Exact retained mesh protection; empty bounding-box corners grant no rejection.

All original runtime faces, including vertical lines, must fit the pinned parent.
This is a terrain preparation proof only, not physical/publication acceptance.
"""
import numpy as np
import shapely
from shapely.geometry import box


def retained_projection(rows, entries, parent_bounds, new_projection):
    assert len(rows)==len(entries) and {r['uid'] for r in rows}==set(entries), 'Missing or repeated retained mesh'
    regions=[]
    for row in rows:
        entry=entries[row['uid']]
        assert row['sourceSHA256']==entry['sha256'], 'Retained original source changed'
        position=np.asarray(row['position'],dtype=float)
        index=np.asarray(row['index'])
        assert position.ndim==index.ndim==1 and len(position)%3==len(index)%3==0
        assert len(position)>0 and len(index)>0 and np.isfinite(position).all()
        assert np.issubdtype(index.dtype,np.integer) and index.min()>=0 and index.max()<len(position)//3
        vertices=position.reshape(-1,3)
        assert len(index)//3==entry['triangles'], 'Incomplete original retained mesh'
        assert np.max(np.abs(np.array([vertices.min(axis=0),vertices.max(axis=0)])-entry['worldBounds']))<.002
        faces=vertices[index.reshape(-1,3)]
        # Convex hull retains vertical/degenerate projected faces as lines/points.
        region=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in faces]).buffer(.02,join_style='mitre')
        assert not region.is_empty and region.is_valid
        regions.append(region)
    combined=shapely.union_all(regions)
    assert box(*parent_bounds).buffer(1e-6).covers(combined), 'Original retained mesh outside pinned terrain parent'
    assert combined.intersection(new_projection).area<1e-8, 'Original retained mesh overlaps new source'
    return combined
